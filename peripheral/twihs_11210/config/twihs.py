
num=0

def instantiateComponent(twihsComponent):

    global num
    
    num = twihsComponent.getID()[-1:]
    print("Running TWIHSHS" + str(num))

    #main menu
    twihsMenu = twihsComponent.createMenuSymbol("TWIHS_MENU_MAIN", None)
    
    twihsMenu.setLabel("Hardware Settings ")

    #instance index
    twihsIndex = twihsComponent.createIntegerSymbol("INDEX", twihsMenu)
    
    twihsIndex.setVisible(False)
    twihsIndex.setDefaultValue(int(num))

    #operation mode
    opModeValues = ["MASTER"]
    
    twihsOpMode = twihsComponent.createComboSymbol("TWIHS_OPMODE", twihsMenu, opModeValues)
    
    twihsOpMode.setLabel("TWIHS Operation Mode")
    twihsOpMode.setDefaultValue("MASTER")
    
    #Number of Transaction request blocks
    twihsNumTRBs = twihsComponent.createIntegerSymbol("TWIHS_NUM_TRBS", twihsMenu)
    
    twihsNumTRBs.setLabel("Number of TRB's")
    twihsNumTRBs.setDefaultValue(2)
    twihsNumTRBs.setMax(255)

    #Clock speed
    twihsSymClockSpeed = twihsComponent.createIntegerSymbol("TWIHS_CLK_SPEED", twihsMenu)
    
    twihsSymClockSpeed.setLabel("Clock Speed")
    twihsSymClockSpeed.setDefaultValue(400000)
    twihsSymClockSpeed.setMax(400000)

    cldiv, chdiv, ckdiv = getTWIHSClockDividerValue(twihsSymClockSpeed.getValue())
    
    #Clock Divider
    twihsSymDivider = twihsComponent.createStringSymbol("TWIHS_DIVIDER", twihsMenu)
    
    twihsSymDivider.setVisible(False)
    twihsSymDivider.setDependencies(setClockDividerValue, ["TWIHS_CLK_SPEED", "core.MASTERCLK_FREQ"])
    
    #CLDIV
    twihsSym_CWGR_CLDIV = twihsComponent.createIntegerSymbol("TWIHS_CWGR_CLDIV", twihsMenu)
    
    twihsSym_CWGR_CLDIV.setVisible(False)
    twihsSym_CWGR_CLDIV.setValue(cldiv, 1)
    
    #CHDIV
    twihsSym_CWGR_CHDIV = twihsComponent.createIntegerSymbol("TWIHS_CWGR_CHDIV", twihsMenu)
    
    twihsSym_CWGR_CHDIV.setVisible(False)
    twihsSym_CWGR_CHDIV.setValue(chdiv, 1)
    
    #CKDIV
    twihsSym_CWGR_CKDIV = twihsComponent.createIntegerSymbol("TWIHS_CWGR_CKDIV", twihsMenu)
    
    twihsSym_CWGR_CKDIV.setVisible(False)
    twihsSym_CWGR_CKDIV.setValue(ckdiv, 1)
    
    # Initialize peripheral clock
    Database.clearSymbolValue("core", "PMC_ID_TWIHS" + str(num))
    Database.setSymbolValue("core", "PMC_ID_TWIHS" + str(num), True, 1)
    
    # get peripheral id for TWIHS
    peripId = Interrupt.getInterruptIndex("TWIHS" + str(num))
    
    # Initialize peripheral Interrupt
    Database.clearSymbolValue("core", "NVIC_" + str(peripId) + "_ENABLE")
    Database.setSymbolValue("core", "NVIC_" + str(peripId) + "_ENABLE", True, 1)
    
    # Set Interrupt Handler Name
    Database.clearSymbolValue("core", "NVIC_" + str(peripId) + "_HANDLER")
    Database.setSymbolValue("core", "NVIC_" + str(peripId) + "_HANDLER", "TWIHS" + str(num) + "_InterruptHandler", 1)
    
    # Master Clock Frequency
    twihsSymMasterClkFreq = twihsComponent.createStringSymbol("TWIHS_CLK_SRC_FREQ", twihsMenu)
    twihsSymMasterClkFreq.setVisible(False)
    twihsSymMasterClkFreq.setDefaultValue(Database.getSymbolValue("core","MASTERCLK_FREQ"))
    twihsSymMasterClkFreq.setDependencies(setClockSourceFreq, ["core.MASTERCLK_FREQ"])
    
    # Warning for change in Clock Enable Symbol
    twihsSymClkEnComment = twihsComponent.createCommentSymbol("TWIHS_CLK_EN_COMMENT", twihsMenu)
    twihsSymClkEnComment.setVisible(False)
    twihsSymClkEnComment.setLabel("Warning!!! TWIHS Peripheral Clock is Disabled in Clock Manager")
    twihsSymClkEnComment.setDependencies(setEnCommentVisibility, ["core.PMC_ID_TWIHS" + str(num)])
    
    # Warning for change in Interrupt Enable Symbol
    twihsSymIntEnComment = twihsComponent.createCommentSymbol("TWIHS_INT_EN_COMMENT", twihsMenu)
    twihsSymIntEnComment.setVisible(False)
    twihsSymIntEnComment.setLabel("Warning!!! TWIHS Interrupt is Disabled in Interrupt Manager")
    twihsSymIntEnComment.setDependencies(setEnCommentVisibility, ["core.NVIC_" + str(peripId) + "_ENABLE"])
    
    REG_MODULE_TWIHS = Register.getRegisterModule("TWIHS")
    
    configName = Variables.get("__CONFIGURATION_NAME")
    
    #Master Header
    twihsMasterHeaderFile = twihsComponent.createFileSymbol("TWIHS_FILE_MASTER_HEADER", None)
    
    twihsMasterHeaderFile.setSourcePath("../peripheral/twihs_" + REG_MODULE_TWIHS.getID() + "/plib_twihs_master.h")
    twihsMasterHeaderFile.setOutputName("plib_twihs_master.h")
    twihsMasterHeaderFile.setDestPath("/peripheral/twihs/")
    twihsMasterHeaderFile.setProjectPath("config/" + configName + "/peripheral/twihs/")
    twihsMasterHeaderFile.setType("HEADER")

    #Source File
    twihsMainSourceFile = twihsComponent.createFileSymbol("TWIHS_FILE_SRC_MAIN", None)
    
    twihsMainSourceFile.setSourcePath("../peripheral/twihs_" + REG_MODULE_TWIHS.getID() + "/templates/plib_twihs.c.ftl")
    twihsMainSourceFile.setOutputName("plib_twihs" + str(num) + ".c")
    twihsMainSourceFile.setDestPath("/peripheral/twihs/")
    twihsMainSourceFile.setProjectPath("config/" + configName + "/peripheral/twihs/")
    twihsMainSourceFile.setType("SOURCE")
    twihsMainSourceFile.setMarkup(True)
    
    #Instance Header File
    twihsInstHeaderFile = twihsComponent.createFileSymbol("TWIHS_FILE_MAIN_HEADER", None)
    
    twihsInstHeaderFile.setSourcePath("../peripheral/twihs_" + REG_MODULE_TWIHS.getID() + "/templates/plib_twihs.h.ftl")
    twihsInstHeaderFile.setOutputName("plib_twihs" + str(num) + ".h")
    twihsInstHeaderFile.setDestPath("/peripheral/twihs/")
    twihsInstHeaderFile.setProjectPath("config/" + configName + "/peripheral/twihs/")
    twihsInstHeaderFile.setType("HEADER")
    twihsInstHeaderFile.setMarkup(True)
    
    #TWIHS Initialize 
    twihsSystemInitFile = twihsComponent.createFileSymbol("TWIHS_FILE_SYS_INIT", None)
    twihsSystemInitFile.setType("STRING")
    twihsSystemInitFile.setOutputName("core.LIST_SYSTEM_INIT_C_SYS_INITIALIZE_PERIPHERALS")
    twihsSystemInitFile.setSourcePath("../peripheral/twihs_" + REG_MODULE_TWIHS.getID() + "/templates/system/system_initialize.c.ftl")
    twihsSystemInitFile.setMarkup(True)

    #TWIHS definitions header
    twihsSystemDefFile = twihsComponent.createFileSymbol("TWIHS_FILE_SYS_DEF", None)
    
    twihsSystemDefFile.setType("STRING")
    twihsSystemDefFile.setOutputName("core.LIST_SYSTEM_DEFINITIONS_H_INCLUDES")
    twihsSystemDefFile.setSourcePath("../peripheral/twihs_" + REG_MODULE_TWIHS.getID() + "/templates/system/system_definitions.h.ftl")
    twihsSystemDefFile.setMarkup(True)
    
def getMasterClockFreq():
    return int(Database.getSymbolValue("core", "MASTERCLK_FREQ"))
        
def getTWIHSClkSpeed():
    global num
    return Database.getSymbolValue('twihs' + str(num), "TWIHS_CLK_SPEED")

def getTWIHSLowLevelTimeLimit( ):
    return 384000

def getTWIHSClockDividerMaxValue( ):
    return 255

def getTWIHSClockDividerMinValue( ):
    return 7
        
def getTWIHSClockDividerValue( twihsClkSpeed ):

    cldiv = 0 
    chdiv = 0
    ckdiv = 0
    
    masterClockFreq = getMasterClockFreq( )

    if twihsClkSpeed > getTWIHSLowLevelTimeLimit():
        cldiv = masterClockFreq // ( getTWIHSLowLevelTimeLimit() * 2) - 3
        chdiv = masterClockFreq // ((twihsClkSpeed + (twihsClkSpeed - getTWIHSLowLevelTimeLimit())) * 2 ) - 3

        while cldiv > getTWIHSClockDividerMaxValue() and ckdiv < getTWIHSClockDividerMinValue():
            ckdiv += 1
            cldiv //= 2

        while chdiv > getTWIHSClockDividerMaxValue() and ckdiv < getTWIHSClockDividerMinValue():
            ckdiv += 1
            chdiv //= 2
    else:
        cldiv = masterClockFreq / ( twihsClkSpeed * 2 ) - 3

        while cldiv > getTWIHSClockDividerMaxValue() and ckdiv < getTWIHSClockDividerMinValue():
            ckdiv += 1
            cldiv //= 2

        chdiv = cldiv

    return cldiv, chdiv, ckdiv
                        
def setClockDividerValue( twihsSymDivider, event):
    
    global num
    cldiv, chdiv, ckdiv = getTWIHSClockDividerValue( getTWIHSClkSpeed( ) )
    
    # set CLDIV Value
    Database.setSymbolValue("twihs" + str(num), "TWIHS_CWGR_CLDIV", cldiv, 1)

    # set CHDIV Value
    Database.setSymbolValue("twihs" + str(num), "TWIHS_CWGR_CHDIV", chdiv, 1)
    
    # set CKDIV Value
    Database.setSymbolValue("twihs" + str(num), "TWIHS_CWGR_CKDIV", ckdiv, 1)
    
def setEnCommentVisibility( twihsSymComment, event ):
    if event["value"] is False:
        twihsSymComment.setVisible(True)
    else:
        twihsSymComment.setVisible(False)
        
def setClockSourceFreq( twihsSymClockFreq, event ):
    masterClockFreq = Database.getSymbolValue("core", "MASTERCLK_FREQ")
    twihsSymClockFreq.setValue(masterClockFreq, 1)

'''********************************End of the file*************************'''
    
