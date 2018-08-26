from os.path import join
from xml.etree import ElementTree

Log.writeInfoMessage("Loading DMA Manager for " + Variables.get("__PROCESSOR"))

################################################################################
#### Global Variables ####
################################################################################

global dmacHeaderFile
global dmacSourceFile
global dmacSystemInitFile
global dmacSystemDefFile

# Parse atdf xml file to get instance name for the peripheral which has DMA id.
# And construct a list of PERIDs

global per_instance
per_instance = {}
per_instance["Software Trigger"] = 0

global peridValueListSymbols
peridValueListSymbols = []

global dmacActiveChannels
dmacActiveChannels = []

global dmacChannelIds
dmacChannelIds = []

# Create lists for peripheral triggers and the corresponding ID values
node = ATDF.getNode("/avr-tools-device-file/devices/device/peripherals")
modules = node.getChildren()
for module in range (0, len(modules)):
    instances = modules[module].getChildren()
    for instance in range (0, len(instances)):
        options = instances[instance].getChildren()
        for option in range (0, len(options)):
            if "parameters" == options[option].getName():
                parameters = options[option].getChildren()
                for parameter in range(0, len(parameters)):
                    if "name" in parameters[parameter].getAttributeList():
                        name = str(parameters[parameter].getAttribute("name"))
                        module = str(instances[instance].getAttribute("name"))
                        if "DMAC_ID" in name:
                            global per_instance
                            if int(parameters[parameter].getAttribute("value")) not in per_instance.values():
                                name = name.replace('DMAC_ID_', '')
                                name = name.replace('TX', 'Transmit')
                                name = name.replace('RX', 'Receive')
                                name = name.replace('LEFT', 'Left')
                                name = name.replace('RIGHT', 'Right')
                                per_instance[module + "_" + name] = int(parameters[parameter].getAttribute("value"))

# This is the dictionary for all trigger sources and corresponding DMAC settings.
# "dmacTriggerLogic" business logic will override the DMAC setting values
# based on the trigger source selected.

global triggerSettings
global triggerRegister

triggerSettings, triggerRegister = setDMACDefaultSettings()

################################################################################
#### Business Logic ####
################################################################################

def setDMACChannelEnableProperty(symbol, event):

    channelId = int(symbol.getID().strip("DMAC_ENABLE_CH_"))

    channelCount = int(event["value"])

    if channelId < channelCount:
        symbol.setVisible(True)
    else:
        symbol.setVisible(False)

def dmacTriggerLogic(symbol, event):

    global triggerSettings
    global triggerRegister

    symbolID = symbol.getID()

    if event["value"] in triggerSettings:
        trigger = event["value"]
    else:
        if "Receive" in event["value"]:
            trigger = "Standard_Receive"
        else:
            trigger = "Standard_Transmit"

    symbol.clearValue()

    if "TRIGACT" in symbolID:
        symbol.setSelectedKey(str(triggerSettings[trigger][0]), 2)
        if (triggerSettings[trigger][0] == "TRANSACTION"):
            symbol.setReadOnly(True)
        else:
            symbol.setReadOnly(False)
    elif "STEPSEL" in symbolID:
        symbol.setSelectedKey(str(triggerSettings[trigger][1]), 2)
    elif "SRCINC" in symbolID:
        symbol.setSelectedKey(str(triggerSettings[trigger][2]), 2)
    elif "DSTINC" in symbolID:
        symbol.setSelectedKey(str(triggerSettings[trigger][3]), 2)
    elif "STEPSIZE" in symbolID:
        symbol.setSelectedKey(str(triggerSettings[trigger][4]), 2)
    elif "BEATSIZE" in symbolID:
        symbol.setSelectedKey(str(triggerSettings[trigger][5]), 2)
    elif "PER_REGISTER" in symbolID:
        symbol.setValue(str(triggerRegister[event["value"]][0]), 2)

# The following business logic creates a list of enabled DMA channels and sorts
# them in the descending order. The left most channel number will be the highest
# index enabled, also if the list is empty then none of the channel is enabled.
# Highest index will be used to create DMAC objects in source code.
# List empty or non-empty status helps to generate/discard DMAC code.
def dmacGlobalLogic(symbol, event):

    global dmacActiveChannels

    index = event["id"].strip("DMAC_ENABLE_CH_")

    try:
        index = int(index)
    except:
        return

    if event["value"] == True:
        if index not in dmacActiveChannels:
            dmacActiveChannels.append(index)
    else :
        if index in dmacActiveChannels:
            dmacActiveChannels.remove(index)

    dmacActiveChannels.sort()
    dmacActiveChannels.reverse()

    symbol.clearValue()
    # Check if the list is not empty first since list element is accessed in the code
    if dmacActiveChannels:
        if symbol.getID() == "DMAC_HIGHEST_CHANNEL":
            symbol.setValue(int(dmacActiveChannels[0]) + 1, 2)

    if symbol.getID() == "DMAC_ENABLE":
        if dmacActiveChannels and symbol.getValue() == False:
            symbol.setValue(True, 2)

        if not dmacActiveChannels:
            symbol.setValue(False, 2)

def onGlobalEnableLogic(symbol, event):

    # File generation logic
    dmacHeaderFile.setEnabled(event["value"])
    dmacSourceFile.setEnabled(event["value"])
    dmacSystemInitFile.setEnabled(event["value"])
    dmacSystemDefFile.setEnabled(event["value"])

def dmacTriggerCalc(symbol, event):

    global per_instance

    symbol.clearValue()
    symbol.setValue(per_instance.get(event["value"]), 2)

# This function enables DMA channel and selects respective trigger if DMA mode
# is selected for any peripheral ID.
# And once the DMA mode is unselected, then the corresponding DMA channel will
# be disabled and trigger source will be reset to "Software trigger"
def dmacChannelAllocLogic(symbol, event):

    dmaChannelCount = Database.getSymbolValue("core", "DMAC_CHANNEL_COUNT")
    perID = event["id"].strip('DMA_CH_NEEDED_FOR_')
    channelAllocated = False

    for i in range(0, dmaChannelCount):
        dmaChannelEnable = Database.getSymbolValue("core", "DMAC_CH" + str(i) + "_ENABLE")
        dmaChannelPerID = str(Database.getSymbolValue("core", "DMAC_CHCTRLB_TRIGSRC_CH_" + str(i)))

        # Client requested to allocate channel
        if event["value"] == True:
            # Reserve the first available free channel
            if dmaChannelEnable == False:
                Database.clearSymbolValue("core", "DMAC_CH" + str(i) + "_ENABLE")
                Database.setSymbolValue("core", "DMAC_CH" + str(i) + "_ENABLE", True, 2)

                Database.clearSymbolValue("core", "DMAC_CHCTRLB_TRIGSRC_CH_" + str(i))
                Database.setSymbolValue("core", "DMAC_CHCTRLB_TRIGSRC_CH_" + str(i), perID, 2)

                Database.clearSymbolValue("core", "DMA_CH_FOR_" + perID)
                Database.setSymbolValue("core", "DMA_CH_FOR_" + perID, i, 2)

                channelAllocated = True
                i = 0
                break

        # Client requested to deallocate channel
        else:
            # Reset the previously allocated channel
            if perID == dmaChannelPerID and dmaChannelEnable == True:
                Database.clearSymbolValue("core", "DMAC_CH" + str(i) + "_ENABLE")
                Database.setSymbolValue("core", "DMAC_CH" + str(i) + "_ENABLE", False, 2)
                Database.clearSymbolValue("core", "DMAC_CHCTRLB_TRIGSRC_CH_" + str(i))
                Database.setSymbolValue("core", "DMAC_CHCTRLB_TRIGSRC_CH_" + str(i), "Software Trigger", 2)
                Database.clearSymbolValue("core", "DMA_CH_FOR_" + perID)
                Database.setSymbolValue("core", "DMA_CH_FOR_" + perID, -1, 2)

    if event["value"] == True and channelAllocated == False:
        # Couldn't find any free DMA channel, hence set warning.
        Database.clearSymbolValue("core", "DMA_CH_FOR_" + perID)
        Database.setSymbolValue("core", "DMA_CH_FOR_" + perID, -2, 2)

################################################################################
#### Component ####
################################################################################

dmacChannelNode = ATDF.getNode("/avr-tools-device-file/devices/device/peripherals/module@[name=\"DMAC\"]/instance@[name=\"DMAC\"]/parameters/param@[name=\"CH_NUM\"]")
dmacChannelCount = int(dmacChannelNode.getAttribute("value"))

dmaManagerSelect = coreComponent.createStringSymbol("DMA_MANAGER_PLUGIN_SELECT", None)
dmaManagerSelect.setVisible(False)
dmaManagerSelect.setDefaultValue("SAMM0:SAMM0DMAModel")

dmacMenu = coreComponent.createMenuSymbol("DMAC_MENU", None)
dmacMenu.setLabel("DMA (DMAC)")
dmacMenu.setDescription("DMA (DMAC) Configuration")

dmacIndex = coreComponent.createIntegerSymbol("DMAC_INDEX", dmacMenu)
dmacIndex.setVisible(False)
dmacIndex.setDefaultValue(0)

dmacEnable = coreComponent.createBooleanSymbol("DMAC_ENABLE", dmacMenu)
dmacEnable.setLabel("Use DMA Service ?")
dmacEnable.setVisible(False)

dmacFileGen = coreComponent.createBooleanSymbol("DMAC_FILE_GEN", dmacEnable)
dmacFileGen.setLabel("DMA (DMAC) File Generation")
dmacFileGen.setVisible(False)
dmacFileGen.setDependencies(onGlobalEnableLogic, ["DMAC_ENABLE"])

dmacHighestCh = coreComponent.createIntegerSymbol("DMAC_HIGHEST_CHANNEL", dmacEnable)
dmacHighestCh.setLabel("DMA (DMAC) Highest Active Channel")
dmacHighestCh.setVisible(False)

dmacChCount = coreComponent.createIntegerSymbol("DMAC_CHANNEL_COUNT", dmacEnable)
dmacChCount.setLabel("DMA (DMAC) Channels Count")
dmacChCount.setDefaultValue(dmacChannelCount)
dmacChCount.setVisible(False)

dmacChannelLinkedList = coreComponent.createBooleanSymbol("DMAC_LL_ENABLE", dmacMenu)
dmacChannelLinkedList.setLabel("Use Linked List Mode ?")

#DMA Channel Enable Count
DMAC_CHAN_ENAB_CNT_SelectionSym = coreComponent.createIntegerSymbol("DMAC_CHAN_ENABLE_CNT", dmacMenu)
DMAC_CHAN_ENAB_CNT_SelectionSym.setLabel("Number of DMA channels to enable")
DMAC_CHAN_ENAB_CNT_SelectionSym.setDefaultValue(1)
DMAC_CHAN_ENAB_CNT_SelectionSym.setMin(1)
DMAC_CHAN_ENAB_CNT_SelectionSym.setMax(dmacChannelCount)

#Priority Control 0 Register
for dmacCount in range(0, 4):

    #Level 0/1/2/3 Round-Robin Arbitration Enable
    PRICTRL0_LVLPRI_SelectionSym = coreComponent.createKeyValueSetSymbol("DMAC_LVLXPRIO_" + str(dmacCount),dmacMenu)
    PRICTRL0_LVLPRI_SelectionSym.setLabel("Priority Level " + str(dmacCount) + " Arbitration Scheme")

    PRICTRL0_LVLPRI_SelectionSym.addKey("STATIC_LVL", "0", "Static Priority Arbitration")
    PRICTRL0_LVLPRI_SelectionSym.addKey("ROUND_ROBIN_LVL", "1", "Round Robin Priority Arbitration")
    PRICTRL0_LVLPRI_SelectionSym.setDefaultValue(1)
    PRICTRL0_LVLPRI_SelectionSym.setOutputMode("Value")
    PRICTRL0_LVLPRI_SelectionSym.setDisplayMode("Description")

for channelID in range(0, dmacChCount.getValue()):

    global per_instance

    dmacChannelEnable = coreComponent.createBooleanSymbol("DMAC_ENABLE_CH_" + str(channelID), dmacMenu)
    dmacChannelEnable.setLabel("Use DMAC Channel " + str(channelID))

    if channelID != 0:
        dmacChannelEnable.setVisible(False)

    dmacChannelIds.append("DMAC_ENABLE_CH_" + str(channelID))
    dmacChannelEnable.setDependencies(setDMACChannelEnableProperty, ["DMAC_CHAN_ENABLE_CNT"])

    #Channel Run in Standby
    CH_CHCTRLA_RUNSTDBY_Ctrl = coreComponent.createBooleanSymbol("DMAC_CHCTRLA_RUNSTDBY_CH_" + str(channelID), dmacChannelEnable)
    CH_CHCTRLA_RUNSTDBY_Ctrl.setLabel("Run Channel in Standby mode")

    # CHCTRLB - Trigger Source
    dmacSym_CHCTRLB_TRIGSRC = coreComponent.createComboSymbol("DMAC_CHCTRLB_TRIGSRC_CH_" + str(channelID), dmacChannelEnable, sorted(per_instance.keys()))
    dmacSym_CHCTRLB_TRIGSRC.setLabel("Trigger Source")
    dmacSym_CHCTRLB_TRIGSRC.setDefaultValue("Software Trigger")

    dmacSym_PERID_Val = coreComponent.createIntegerSymbol("DMAC_CHCTRLB_TRIGSRC_CH_" + str(channelID) + "_PERID_VAL", dmacChannelEnable)
    dmacSym_PERID_Val.setLabel("PERID Value")
    dmacSym_PERID_Val.setDefaultValue(0)
    dmacSym_PERID_Val.setDependencies(dmacTriggerCalc, ["DMAC_CHCTRLB_TRIGSRC_CH_" + str(channelID)])
    dmacSym_PERID_Val.setVisible(False)

    dmacPeripheralRegister = coreComponent.createStringSymbol("DMAC_CH" + str(channelID) + "_PER_REGISTER", dmacChannelEnable)
    dmacPeripheralRegister.setLabel("Source Address")
    dmacPeripheralRegister.setDefaultValue("None")
    dmacPeripheralRegister.setReadOnly(True)
    dmacPeripheralRegister.setVisible(False)
    dmacPeripheralRegister.setDependencies(dmacTriggerLogic, ["DMAC_CHCTRLB_TRIGSRC_CH_" + str(channelID)])

    # CHCTRLB - Trigger Action
    dmacSym_CHCTRLB_TRIGACT = coreComponent.createKeyValueSetSymbol("DMAC_CHCTRLB_TRIGACT_CH_" + str(channelID), dmacChannelEnable)
    dmacSym_CHCTRLB_TRIGACT.setLabel("Trigger Action")
    dmacSym_CHCTRLB_TRIGACT.setReadOnly(True)
    dmacSym_CHCTRLB_TRIGACT.addKey("BLOCK", "0", "One Block Transfer Per DMA Request")
    dmacSym_CHCTRLB_TRIGACT.addKey("BEAT", "2", "One Beat Transfer per DMA Request")
    dmacSym_CHCTRLB_TRIGACT.setDefaultValue(1)
    dmacSym_CHCTRLB_TRIGACT.setOutputMode("Value")
    dmacSym_CHCTRLB_TRIGACT.setDisplayMode("Description")
    dmacSym_CHCTRLB_TRIGACT.setDependencies(dmacTriggerLogic, ["DMAC_CHCTRLB_TRIGSRC_CH_" + str(channelID)])

    #Channel Priority Level
    CHCTRLB_LVL_SelectionSym = coreComponent.createKeyValueSetSymbol("DMAC_CHCTRLB_LVL_CH_" + str(channelID), dmacChannelEnable)
    CHCTRLB_LVL_SelectionSym.setLabel("Channel Priority Level")
    CHCTRLB_LVL_SelectionSym.addKey("LVL0", "0", "Priority Level 0")
    CHCTRLB_LVL_SelectionSym.addKey("LVL1", "1", "Priority Level 1")
    CHCTRLB_LVL_SelectionSym.addKey("LVL2", "2", "Priority Level 2")
    CHCTRLB_LVL_SelectionSym.addKey("LVL3", "3", "Priority Level 3")
    CHCTRLB_LVL_SelectionSym.setDefaultValue(0)
    CHCTRLB_LVL_SelectionSym.setOutputMode("Value")
    CHCTRLB_LVL_SelectionSym.setDisplayMode("Description")

    # BTCTRL - Destination Increment
    dmacSym_BTCTRL_DSTINC_Val = coreComponent.createKeyValueSetSymbol("DMAC_BTCTRL_DSTINC_CH_" + str(channelID), dmacChannelEnable)
    dmacSym_BTCTRL_DSTINC_Val.setLabel("Destination Address Mode")
    dmacSym_BTCTRL_DSTINC_Val.addKey("FIXED_AM", "0", "Fixed Address Mode")
    dmacSym_BTCTRL_DSTINC_Val.addKey("INCREMENTED_AM", "1", "Increment Address After Every Transfer")
    dmacSym_BTCTRL_DSTINC_Val.setOutputMode("Key")
    dmacSym_BTCTRL_DSTINC_Val.setDisplayMode("Description")
    dmacSym_BTCTRL_DSTINC_Val.setDefaultValue(1)
    dmacSym_BTCTRL_DSTINC_Val.setDependencies(dmacTriggerLogic, ["DMAC_CHCTRLB_TRIGSRC_CH_" + str(channelID)])

    # BTCTRL - Source Increment
    dmacSym_BTCTRL_SRCINC_Val = coreComponent.createKeyValueSetSymbol("DMAC_BTCTRL_SRCINC_CH_" + str(channelID), dmacChannelEnable)
    dmacSym_BTCTRL_SRCINC_Val.setLabel("Source Address Mode")
    dmacSym_BTCTRL_SRCINC_Val.addKey("FIXED_AM", "0", "Fixed Address Mode")
    dmacSym_BTCTRL_SRCINC_Val.addKey("INCREMENTED_AM", "1", "Increment Address After Every Transfer")
    dmacSym_BTCTRL_SRCINC_Val.setOutputMode("Key")
    dmacSym_BTCTRL_SRCINC_Val.setDisplayMode("Description")
    dmacSym_BTCTRL_SRCINC_Val.setDefaultValue(1)
    dmacSym_BTCTRL_SRCINC_Val.setDependencies(dmacTriggerLogic, ["DMAC_CHCTRLB_TRIGSRC_CH_" + str(channelID)])

    # BTCTRL - Beat Size
    dmacSym_BTCTRL_BEATSIZE = coreComponent.createKeyValueSetSymbol("DMAC_BTCTRL_BEATSIZE_CH_" + str(channelID), dmacChannelEnable)
    dmacSym_BTCTRL_BEATSIZE.setLabel("Beat Size")

    dmacBeatSizeNode = ATDF.getNode("/avr-tools-device-file/modules/module@[name=\"DMAC\"]/value-group@[name=\"DMAC_BTCTRL__BEATSIZE\"]")
    dmacBeatSizeValues = []
    dmacBeatSizeValues = dmacBeatSizeNode.getChildren()

    dmacBeatSizeDefaultValue = 0

    for index in range(len(dmacBeatSizeValues)):
        dmacBeatSizeKeyName = dmacBeatSizeValues[index].getAttribute("name")

        if (dmacBeatSizeKeyName == "BYTE"):
            dmacBeatSizeDefaultValue = index

        dmacBeatSizeKeyDescription = dmacBeatSizeValues[index].getAttribute("caption")
        dmacBeatSizeKeyValue = dmacBeatSizeValues[index].getAttribute("value")
        dmacSym_BTCTRL_BEATSIZE.addKey(dmacBeatSizeKeyName, dmacBeatSizeKeyValue, dmacBeatSizeKeyDescription)

    dmacSym_BTCTRL_BEATSIZE.setDefaultValue(dmacBeatSizeDefaultValue)
    dmacSym_BTCTRL_BEATSIZE.setOutputMode("Key")
    dmacSym_BTCTRL_BEATSIZE.setDisplayMode("Description")
    dmacSym_BTCTRL_BEATSIZE.setDependencies(dmacTriggerLogic, ["DMAC_CHCTRLB_TRIGSRC_CH_"+ str(channelID)])

dmacEnable.setDependencies(dmacGlobalLogic, dmacChannelIds)
dmacHighestCh.setDependencies(dmacGlobalLogic, dmacChannelIds)

# Interface for Peripheral clients
for per in per_instance.keys():
    dmacChannelNeeded = coreComponent.createBooleanSymbol("DMA_CH_NEEDED_FOR_" + str(per), dmacChannelEnable)
    dmacChannelNeeded.setLabel("Local DMA_CH_NEEDED_FOR_" + str(per))
    dmacChannelNeeded.setVisible(False)
    peridValueListSymbols.append("DMA_CH_NEEDED_FOR_" + str(per))

    dmacChannel = coreComponent.createIntegerSymbol("DMA_CH_FOR_" + str(per), dmacChannelEnable)
    dmacChannel.setLabel("Local DMA_CH_FOR_" + str(per))
    dmacChannel.setDefaultValue(-1)
    dmacChannel.setVisible(False)

dmacPERIDChannelUpdate = coreComponent.createBooleanSymbol("DMA_CHANNEL_ALLOC", dmacChannelEnable)
dmacPERIDChannelUpdate.setLabel("Local dmacChannelAllocLogic")
dmacPERIDChannelUpdate.setVisible(False)
dmacPERIDChannelUpdate.setDependencies(dmacChannelAllocLogic, peridValueListSymbols)

###################################################################################################
####################################### Code Generation  ##########################################
###################################################################################################

configName = Variables.get("__CONFIGURATION_NAME")

# Instance Header File
dmacHeaderFile = coreComponent.createFileSymbol("DMAC_HEADER", None)
dmacHeaderFile.setSourcePath("../peripheral/dmac_u2223/templates/plib_dmac.h.ftl")
dmacHeaderFile.setOutputName("plib_dmac0.h")
dmacHeaderFile.setDestPath("/peripheral/dmac/")
dmacHeaderFile.setProjectPath("config/" + configName + "/peripheral/dmac/")
dmacHeaderFile.setType("HEADER")
dmacHeaderFile.setMarkup(True)
dmacHeaderFile.setEnabled(False)

# Source File
dmacSourceFile = coreComponent.createFileSymbol("DMAC_SOURCE", None)
dmacSourceFile.setSourcePath("../peripheral/dmac_u2223/templates/plib_dmac.c.ftl")
dmacSourceFile.setOutputName("plib_dmac0.c")
dmacSourceFile.setDestPath("/peripheral/dmac/")
dmacSourceFile.setProjectPath("config/" + configName + "/peripheral/dmac/")
dmacSourceFile.setType("SOURCE")
dmacSourceFile.setMarkup(True)
dmacSourceFile.setEnabled(False)

#System Initialization
dmacSystemInitFile = coreComponent.createFileSymbol("DMAC_SYS_INIT", None)
dmacSystemInitFile.setType("STRING")
dmacSystemInitFile.setOutputName("core.LIST_SYSTEM_INIT_C_SYS_INITIALIZE_PERIPHERALS")
dmacSystemInitFile.setSourcePath("../peripheral/dmac_u2223/templates/system/initialization.c.ftl")
dmacSystemInitFile.setMarkup(True)
dmacSystemInitFile.setEnabled(False)

#System Definition
dmacSystemDefFile = coreComponent.createFileSymbol("DMAC_SYS_DEF", None)
dmacSystemDefFile.setType("STRING")
dmacSystemDefFile.setOutputName("core.LIST_SYSTEM_DEFINITIONS_H_INCLUDES")
dmacSystemDefFile.setSourcePath("../peripheral/dmac_u2223/templates/system/definitions.h.ftl")
dmacSystemDefFile.setMarkup(True)
dmacSystemDefFile.setEnabled(False)
