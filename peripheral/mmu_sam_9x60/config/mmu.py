"""*****************************************************************************
* Copyright (C) 2019 Microchip Technology Inc. and its subsidiaries.
*
* Subject to your compliance with these terms, you may use Microchip software
* and any derivatives exclusively with Microchip products. It is your
* responsibility to comply with third party license terms applicable to your
* use of third party software (including open source software) that may
* accompany Microchip software.
*
* THIS SOFTWARE IS SUPPLIED BY MICROCHIP "AS IS". NO WARRANTIES, WHETHER
* EXPRESS, IMPLIED OR STATUTORY, APPLY TO THIS SOFTWARE, INCLUDING ANY IMPLIED
* WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, AND FITNESS FOR A
* PARTICULAR PURPOSE.
*
* IN NO EVENT WILL MICROCHIP BE LIABLE FOR ANY INDIRECT, SPECIAL, PUNITIVE,
* INCIDENTAL OR CONSEQUENTIAL LOSS, DAMAGE, COST OR EXPENSE OF ANY KIND
* WHATSOEVER RELATED TO THE SOFTWARE, HOWEVER CAUSED, EVEN IF MICROCHIP HAS
* BEEN ADVISED OF THE POSSIBILITY OR THE DAMAGES ARE FORESEEABLE. TO THE
* FULLEST EXTENT ALLOWED BY LAW, MICROCHIP'S TOTAL LIABILITY ON ALL CLAIMS IN
* ANY WAY RELATED TO THIS SOFTWARE WILL NOT EXCEED THE AMOUNT OF FEES, IF ANY,
* THAT YOU HAVE PAID DIRECTLY TO MICROCHIP FOR THIS SOFTWARE.
*****************************************************************************"""

Log.writeInfoMessage("Loading MMU for " + Variables.get("__PROCESSOR"))

cacheMenu = coreComponent.createMenuSymbol("CACHE_MENU", cortexMenu)
cacheMenu.setLabel("CACHE")
cacheMenu.setDescription("CACHE Configuration")

dcacheEnable = coreComponent.createBooleanSymbol("DATA_CACHE_ENABLE", cacheMenu)
dcacheEnable.setLabel("Enable Data Cache")
dcacheEnable.setDefaultValue(True)

icacheEnable = coreComponent.createBooleanSymbol("INSTRUCTION_CACHE_ENABLE", cacheMenu)
icacheEnable.setLabel("Enable Instruction Cache")
icacheEnable.setDefaultValue(True)

cacheAlign = coreComponent.createIntegerSymbol("CACHE_ALIGN", cacheMenu)
cacheAlign.setLabel("Cache Alignment Length")
cacheAlign.setVisible(False)
cacheAlign.setDefaultValue(32)

configName = Variables.get("__CONFIGURATION_NAME")

mmuFile = coreComponent.createFileSymbol(None, None)
mmuFile.setSourcePath("../peripheral/mmu_sam_9x60/templates/plib_mmu.c.ftl")
mmuFile.setOutputName("plib_mmu.c")
mmuFile.setDestPath("peripheral/mmu/")
mmuFile.setProjectPath("config/" + configName + "/peripheral/mmu/")
mmuFile.setType("SOURCE")
mmuFile.setMarkup(True)

mmuHeader = coreComponent.createFileSymbol(None, None)
mmuHeader.setSourcePath("../peripheral/mmu_sam_9x60/templates/plib_mmu.h.ftl")
mmuHeader.setOutputName("plib_mmu.h")
mmuHeader.setDestPath("peripheral/mmu/")
mmuHeader.setProjectPath("config/" + configName + "/peripheral/mmu/")
mmuHeader.setType("HEADER")
mmuHeader.setMarkup(True)

cp15Header = coreComponent.createFileSymbol(None, None)
cp15Header.setSourcePath("../peripheral/mmu_sam_9x60/templates/cp15.h")
cp15Header.setOutputName("cp15.h")
cp15Header.setDestPath("peripheral/mmu/")
cp15Header.setProjectPath("config/" + configName + "/peripheral/mmu/")
cp15Header.setType("HEADER")
cp15Header.setMarkup(False)

mmuSystemInitFile = coreComponent.createFileSymbol(None, None)
mmuSystemInitFile.setType("STRING")
mmuSystemInitFile.setOutputName("core.LIST_SYSTEM_INIT_C_SYS_INITIALIZE_PERIPHERALS")
mmuSystemInitFile.setSourcePath("../peripheral/mmu_sam_9x60/templates/system/initialization.c.ftl")
mmuSystemInitFile.setMarkup(True)

mmuSystemDefFile = coreComponent.createFileSymbol(None, None)
mmuSystemDefFile.setType("STRING")
mmuSystemDefFile.setOutputName("core.LIST_SYSTEM_DEFINITIONS_H_INCLUDES")
mmuSystemDefFile.setSourcePath("../peripheral/mmu_sam_9x60/templates/system/definitions.h.ftl")
mmuSystemDefFile.setMarkup(True)
