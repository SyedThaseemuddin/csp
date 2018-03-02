/*******************************************************************************
  Reset Controller (RSTC) Peripheral Library Interface Header File

  Company
    Microchip Technology Inc.

  File Name
    plib_rstc.h

  Summary
    RSTC peripheral library interface.

  Description
    This file defines the interface to the RSTC peripheral library.  This 
    library provides access to and control of the associated Reset Controller.

  Remarks:
    This header is for documentation only. The actual RSTC headers will be
    generated as required by the MCC.

*******************************************************************************/

// DOM-IGNORE-BEGIN
/*******************************************************************************
Copyright (c) 2017 released Microchip Technology Inc.  All rights reserved.

Microchip licenses to you the right to use, modify, copy and distribute
Software only when embedded on a Microchip microcontroller or digital signal
controller that is integrated into your product or third-party product
(pursuant to the sublicense terms in the accompanying license agreement).

You should refer to the license agreement accompanying this Software for
additional information regarding your rights and obligations.

SOFTWARE AND DOCUMENTATION ARE PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND,
EITHER EXPRESS OR IMPLIED, INCLUDING WITHOUT LIMITATION, ANY WARRANTY OF
MERCHANTABILITY, TITLE, NON-INFRINGEMENT AND FITNESS FOR A PARTICULAR PURPOSE.
IN NO EVENT SHALL MICROCHIP OR ITS LICENSORS BE LIABLE OR OBLIGATED UNDER
CONTRACT, NEGLIGENCE, STRICT LIABILITY, CONTRIBUTION, BREACH OF WARRANTY, OR
OTHER LEGAL EQUITABLE THEORY ANY DIRECT OR INDIRECT DAMAGES OR EXPENSES
INCLUDING BUT NOT LIMITED TO ANY INCIDENTAL, SPECIAL, INDIRECT, PUNITIVE OR
CONSEQUENTIAL DAMAGES, LOST PROFITS OR LOST DATA, COST OF PROCUREMENT OF
SUBSTITUTE GOODS, TECHNOLOGY, SERVICES, OR ANY CLAIMS BY THIRD PARTIES
(INCLUDING BUT NOT LIMITED TO ANY DEFENSE THEREOF), OR OTHER SIMILAR COSTS.
*******************************************************************************/
// DOM-IGNORE-END

#ifndef RSTC_H    // Guards against multiple inclusion
#define RSTC_H

// *****************************************************************************
// *****************************************************************************
// Section: Included Files
// *****************************************************************************
// *****************************************************************************

/* This section lists the other files that are included in this file.
*/

#include <stdbool.h>

// DOM-IGNORE-BEGIN
#ifdef __cplusplus // Provide C++ Compatibility

    extern "C" {

#endif
// DOM-IGNORE-END

// *****************************************************************************
// *****************************************************************************
// Section: Data Types
// *****************************************************************************
// *****************************************************************************

/* User Reset type

  Summary:
    Identifies the type of reset.

  Description:
    This enums identifies either General, Backup, Watchdog, Software or User 
    Reset

  Remarks:
    Refer to the specific device data sheet to determine availability.
*/

typedef enum
{
    /* First power reset */
    RSTC_GENERAL_RESET = RSTC_SR_RSTTYP_GENERAL_RST, 
    
    /* Reset after Return from Backup mode */
    RSTC_BACKUP_RESET = RSTC_SR_RSTTYP_BACKUP_RST,

    /* Reset when Watchdog fault occurred */
    RSTC_WATCHDOG_RESET = RSTC_SR_RSTTYP_WDT_RST,

    /* Reset caused by dedicated software instruction */
    RSTC_SOFTWARE_RESET = RSTC_SR_RSTTYP_SOFT_RST,

    /* Reset occurs when NRST pin is detected low */
    RSTC_USER_RESET = RSTC_SR_RSTTYP_USER_RST,    
	      
} RSTC_RESET_CAUSE;

/* Reset type

   Summary:
    Identifies the type of reset, either Processor reset or External Reset.

   Description:
    This enums identifies either Processor reset or External Reset.

  Remarks:
    Refer to the specific device data sheet to determine availability.
*/

typedef enum
{
    /* Processor reset */
    RSTC_RESET_PROC = RSTC_CR_PROCRST_Msk,
    
    /* External reset */
    RSTC_RESET_EXT = RSTC_CR_EXTRST_Msk,
    
    /* Processor and External reset */
    RSTC_RESET_EXT_PROC= (RSTC_CR_PROCRST_Msk | RSTC_CR_EXTRST_Msk) 
    
} RSTC_RESET_TYPE;

typedef void (*RSTC_CALLBACK) (uintptr_t context);
// *****************************************************************************
// *****************************************************************************
// Section: Interface Routines
// *****************************************************************************
// *****************************************************************************

/* Function:
    void RSTCx_Initialize (void);

  Summary:
    Initializes RSTC module with the user configuration.

  Description:
    This function initializes RSTC module with the values configured in MCC GUI.

  Precondition:
    MCC GUI should be configured with the right values.

  Parameters:
    None.

  Returns:
    None.

  Example:
    <code>
        RSTC0_Initialize();
    </code>

  Remarks:
    This function must be called before any other RSTC function is called.                                           

*/

void RSTCx_Initialize (void);

// *****************************************************************************
/* Function:
    void RSTCx_Reset (RSTC_RESET_TYPE type)

   Summary:
     Resets the processor and all the embedded peripherals, if RSTC_RESET type is
     "RSTC_RESET_PROC ".
     Asserts the NRST pin, if RSTC_RESET type is "RSTC_RESET_EXT ".

   Description:
     This function resets the processor and all the embedded peripherals including the memory system
     and, in particular, the Remap Commandor  or this function asserts NRST Pin.

   Precondition:
     None.

   Parameters:
     RSTC_RESET - "RSTC_RESET_PROC", For Processor reset.
                               "RSTC_RESET_EXT", For External Reset
                               "RSTC_RESET_EXT_PROC", For both Processor and External Reset

   Returns:        
     None.

   Example:
     <code>
     RSTC0_Reset (RSTC_RESET_PROC);
     </code>

   Remarks:
     None.

*/
void RSTCx_Reset (RSTC_RESET_TYPE type);

// *****************************************************************************
/* Function:
    bool RSTCx_NRSTPinRead (void)

   Summary:
    This API used to read the NRST pin level, sampled on each 
    "Master Clock(MCK)" rising edge.

   Description:
    This function helps to read the NRST pin status in firmware, When NSRT pin 
    is configured to neither generate reset nor generate interrupt, the NRST pin
    could be used as digital input pin. 
    
   Precondition:
    None.

   Parameters:
    None.
  
   Returns:
    bool - Returns True when NRST pin is high
              Returns False when NRST pin is Low

  Example:
    <code>

    if ( RSTC0_NRSTPinRead () )
    {
        //Application related tasks
    }
    
    </code>

  Remarks:
    None.
*/

bool RSTCx_NRSTPinRead (void);

// *****************************************************************************
/* Function:
    RSTC_RESET_CAUSE RSTCx_ResetCauseGet (void)

   Summary:
    Reports the cause of the last reset.

   Description:
    This function is used to know the cause of the last reset.
    
   Precondition:
    None.

   Parameters:
    None.
  
   Returns:
    RSTC_RESET_CAUSE - Identifies cause of reset. Either General, Backup,
                                          Watchdog, Software or User Reset

  Example:
    <code>

    if ( RSTC_WATCHDOG_RESET == RSTC0_ResetCauseGet () )
    {
        //Application related tasks
    }
    
    </code>

  Remarks:
    None.
*/

RSTC_RESET_CAUSE RSTCx_ResetCauseGet (void);

// *****************************************************************************
/* Function:
    void RSTCx_CallbackRegister (RSTC_CALLBACK callback, uintptr_t context)

  Summary:
    Allows a client to identify a callback function.

  Description:
    None
    
  Precondition:
    Function RSTCx_Initialize should have been called before calling this
    function.

  Parameters:
    callback - Pointer to the callback function.
    context  - The value of parameter will be passed back to the client
               unchanged, when the callback function is called.  It can be used 
               to identify any client specific data object that identifies the
               instance of the client module (for example, it may be a pointer
               to the client module's state structure).   

  Returns:
   None.

  Example:
    <code>
    MY_APP_OBJ myAppObj;
    void APP_RSTC_EventHandler(uintptr_t context)
    {  
        // The context was set to an application specific object.
        // It is now retrievable easily in the event handler.
           MY_APP_OBJ myAppObj = (MY_APP_OBJ *) context;
        //Application related tasks
    }
                  
    RSTC0_CallbackRegister (APP_RSTC_EventHandler, (uintptr_t)&myAppObj);
    </code>

  Remarks:
    None.

*/

void RSTCx_CallbackRegister (RSTC_CALLBACK callback, uintptr_t context);

// DOM-IGNORE-BEGIN
#ifdef __cplusplus  // Provide C++ Compatibility

    }

#endif
// DOM-IGNORE-END

#endif //RSTC_H

/**
 End of File
*/

