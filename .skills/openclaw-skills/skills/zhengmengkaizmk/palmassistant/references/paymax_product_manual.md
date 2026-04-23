# Paymax 刷掌服务平台产品手册

 
    刷掌服务平台 Paymax V1.2 Paymax_User Guide_v1.2     Issue： Date： 
©2013-2026 Tencent Cloud. All rights reserved. 
 Issue（） Security Level：PUBLIC i 
Copyright Notice The content of this document is protected by copyright and belongs to Tencent Cloud. Unauthorized use, including copying, modifying, disseminating, publishing, or plagiarizing any part of this document, is strictly prohibited without prior written permission from Tencent Cloud. This document contains internal data specific to Tencent Cloud and is accessible only to authorized individuals designated by Tencent Cloud. If you have obtained any portion of this document without proper authorization, please promptly delete it. Do not use this document or its content for any purpose, including copying, disclosure, or dissemination nor take any action on the basis of this document or its content.   Trademark Statement  Trademarks related to Tencent Cloud Services, including “Tencent” and “Tencent Cloud,” are owned by Tencent Cloud and/or its affiliates. Any third-party trademarks mentioned in this document are legally owned by their respective right holders.   Disclaimer This document provides an overview of Tencent Cloud products and services available at the time of drafting. However, due to technical adjustments, project design changes, or other factors, products and services may evolve in the future, potentially affecting service scope and levels. Therefore, this document serves as a reference only. Tencent Cloud does not guarantee the accuracy, suitability, or completeness of this document. The specific category, scope, and service level of Tencent Cloud products and services that you purchase and use will be governed by the contract between you and Tencent Cloud. Unless explicitly agreed upon, Tencent Cloud makes no express or implied commitments or guarantees regarding the content of this document. 

 Paymax_User Guide_v1.2  Change History  
 Issue（） Security Level：PUBLIC ii 
Change History Issue Date Changed By Description 
 Paymax_User Guide_v1.2  Contents  
 Issue（） Security Level：PUBLIC iii 
Contents   
 Paymax_User Guide_v1.2  About This Document  
 Issue（） Security Level：PUBLIC iv 
About This Document Purpose This document is used to help you quickly understand the version information of the product, including the release time of each version, new features, system optimization, module changes, and other details.   Intended Audience This document is intended for: ● Customers ● Delivery PMs ● Delivery technical architects ● Delivery engineers ● Product delivery architects ● R&D engineers ● O&M engineers   Symbol Conventions The symbols that may be found in this document are defined as follows. Symbol Description  Supplements the information in the main text.  Indicates a low-level potential risk, mainly information that users must read or consider. If the information is ignored, there may be certain adverse consequences due to misoperation or the operation may not be successful.  Indicates a medium-level potential risk, such as high-risk operations that users should pay attention to. If the information is ignored, there may be device damage, data loss, performance deterioration, or other unpredictable results.  Indicates a high-level potential risk, such as prohibited operations that users should pay attention to. If the 

 Paymax_User Guide_v1.2  About This Document  
 Issue（） Security Level：PUBLIC v 
 
Symbol Description operations are not avoided, there will be serious problems such as system crashes and irreparable data loss. 
 Paymax_User Guide_v1.2  Quick Start_v1.2  
 Issue（） Security Level：PUBLIC 1 
1   Quick Start_v1.2 1. Admin Console: Please ask the contact person for the request URL and account password.  2. Initialization Process Overview:  2.1 Device Activation: Step 1: Go to the management backend, click "Device Management" to register the device SN;  
 

 Paymax_User Guide_v1.2  Quick Start_v1.2  
 Issue（） Security Level：PUBLIC 2 
 
  Step 2: Generate the device activation code. The activation code is valid for 10 minutes.  
 

 Paymax_User Guide_v1.2  Quick Start_v1.2  
 Issue（） Security Level：PUBLIC 3 
 
 Step 3: The device prompts "Scan to active" on startup. Scan the code to complete activation.   2.2 Configuring Device Silent Mode Images ● Log in to the management backend, click "System Settings" in the upper-right corner, then click "App Configuration" on the right to upload the logo for the homepage. 
 

 Paymax_User Guide_v1.2  Quick Start_v1.2  
 Issue（） Security Level：PUBLIC 4 
 
  ● The reference style for the homepage image is as follows: 
 Figure 1-1 App Configuration Example 

 Paymax_User Guide_v1.2  Quick Start_v1.2  
 Issue（） Security Level：PUBLIC 5 
  2.3 (Optional) Business Line/Merchant Management: Note: Used to associate devices with merchants. After association, palm-scan records will display the corresponding merchant; otherwise, merchant information will be blank. Step 1: Create a Business Line: In the management backend, go to "Business Management" → "Business line management" to create a new business line (Business Line). Business lines can be used as independent units for data statistics. For example, when multiple retail brands are served simultaneously, each brand can be set up as a separate business line. Under the business line, you can continue to create affiliated merchants (Merchant). For example, when both Aeon and Starbucks are served, you can create two business lines: "Aeon" and "Starbucks," then create specific merchants under each business line (such as "Aeon Shop 1" and "Aeon Shop 2").  
 

 Paymax_User Guide_v1.2  Quick Start_v1.2  
 Issue（） Security Level：PUBLIC 6 
 
 Step 2: Create Merchant: Create merchant categories under each Business, with up to 5 levels of subcategories. If a category is deleted, you need to select to transfer the merchants under that category (they can only be transferred to the same Business line).  
 

 Paymax_User Guide_v1.2  Quick Start_v1.2  
 Issue（） Security Level：PUBLIC 7 
 
  Step 3: Create Merchant. In non-direct connection mode, there is no need to enter the Channel merchant number.  
 

 Paymax_User Guide_v1.2  Quick Start_v1.2  
 Issue（） Security Level：PUBLIC 8 
 
  Step 4: Associate devices under Merchant details. One Merchant can be associated with multiple devices; however, a single device can only be associated with one Merchant.  
   

 Paymax_User Guide_v1.2  Device-Side Operation Manual_v1.2  
 Issue（） Security Level：PUBLIC 9 
2   Device-Side Operation Manual_v1.2 1. Device Activation: Refer to the document "Quick Start" for details and complete the activation process.   2. Material Preparation: ● Prepare O2 modules or O2 card reader palm devices and serial cables; 
 

 Paymax_User Guide_v1.2  Device-Side Operation Manual_v1.2  
 Issue（） Security Level：PUBLIC 10 
● Prepare Android and windows host computer devices; ● Devices need to connect to the network (the wired network edition requires a network cable connection); ● To use the host computer feature, connect the device to the host computer. Locate the device's HID port, connect via a USB cable, and plug the other end into the host computer. 
 ● To facilitate device debugging for developers, we provide a windows host computer testing tool. For download and usage instructions, refer to the Appendix.   3. Device Attribute Management: 3.1 Attribute Specification: Depending on the usage scenario, you can configure various server-side properties. All configurable properties are as follows: 
Property Value Note Application Type You can select one of the following two types: [PAY] Used for payment scenarios. After palm scanning, it can output payment credentials and only supports HID signal output; [KYC] Used for identity verification and access control scenarios. After palm scanning, it can output user ID or physical card number, and supports Wiegand signal and HID signal output. 
 Paymax_User Guide_v1.2  Device-Side Operation Manual_v1.2  
 Issue（） Security Level：PUBLIC 11 
Property Value Note If it does not involve returning payment credentials, please select the [KYC] type. Place your hand near the proximity sensing wake-up switch. 
Used to control whether the device can capture palm prints when a hand is placed during silent mode. It can be set to [Disable] or [Enable]. [Disable] In silent mode, placing a hand on the device will not trigger any response. The device can only be operated via the host computer's command environment. [Enable] You can set the "Post Wake-up Mode" to control the device state after proximity activation. Post Wake-up Mode Used to control the mode after the device is woken up by palm placement during silent mode: [Registration Mode] Unregistered users can complete palm registration after scanning their palm, while a welcome message will be displayed upon scanning for registered users. [Recognition Mode] Registered users will complete output based on the configured [Output Protocol] and [Output Content] after palm scanning, while unregistered users will display a "Palm not registered" prompt upon scanning. Note: For [PAY] type applications, this property can only be set to [Registration Mode]; for [KYC] type applications, it can be set to [Registration Mode] or [Recognition Mode]. Host Computer Post Wake-up Mode 
Used to control the mode after the device is woken up by host computer commands: [Recognition Mode] Registered users will complete output based on the configured [Output Protocol] and [Output Content] after palm scanning, while unregistered users will display a "Palm not registered" prompt upon scanning. [Hybrid Mode] Registered users will complete output based on the configured [Output Protocol] and [Output Content] after palm scanning, while unregistered users will first enter the registration process and automatically complete output according to the configured [Output Protocol] and [Output Content] upon 
 Paymax_User Guide_v1.2  Device-Side Operation Manual_v1.2  
 Issue（） Security Level：PUBLIC 12 
  3.2 Common Attribute Configuration: 
Property Value Note successful registration. Output Protocol PAY type: Only supports [USB_Host] for connecting to the host computer; KYC type: Supports [USB_Host] and [Wiegand] (for access control scenarios); Output Content PAY type: Only supports [otc] output, that is, payment token; KYC type: In [USB_Host] mode, only [userid] can be output; in [Wiegand] mode, either [userid] or [physical card number] can be output. However, the [Wiegand] mode only supports numeric output. If this mode is selected, please note that both [userid] and [physical card number] must be purely numeric; otherwise, palm scanning will fail to output successfully. Language Supports Chinese, English, and Japanese. 
Property Value 
Independent Registration Terminal or Registration Machine (Device Not Connected to Host Computer) 
Payment Terminal (After Palm Scanning, Return Payment Voucher) 
Member Authentication Device (After Palm Scan, Return User ID) 
Access Control Device (Control Door Opening After Palm Scan) 
Application Type Select based on the actual scenario. If no payment credentials are involved, choose the [KYC] type. 
PAY KYC KYC 
Place your Enabled Disabled. Disabled. Enabled 
 Paymax_User Guide_v1.2  Device-Side Operation Manual_v1.2  
 Issue（） Security Level：PUBLIC 13 
Property Value 
Independent Registration Terminal or Registration Machine (Device Not Connected to Host Computer) 
Payment Terminal (After Palm Scanning, Return Payment Voucher) 
Member Authentication Device (After Palm Scan, Return User ID) 
Access Control Device (Control Door Opening After Palm Scan) 
hand near the proximity sensing wake-up switch. Post Wake-up Mode Registration Mode - - Recognition Mode Host Computer Post Wake-up Mode - Select [Recognition Mode] or [Hybrid Mode] based on business requirements. 
Select [Recognition Mode] or [Hybrid Mode] based on business requirements. 
- 
Output Protocol - USB_Host USB_Host Wiegand Output Content - OTC userid Physical card number or userid If this mode is selected, please note that both [userid] and [physical card number] must be purely numeric; 
 Paymax_User Guide_v1.2  Device-Side Operation Manual_v1.2  
 Issue（） Security Level：PUBLIC 14 
   3.3 Device Attribute Modification Method: ● Single Item Edit: Log in to the management backend, search for the corresponding device in [Business Management]→[Device Management], click [Edit] to complete the edit; after editing, the configuration will be synchronized to the corresponding device in about 1 minute;  
 
Property Value 
Independent Registration Terminal or Registration Machine (Device Not Connected to Host Computer) 
Payment Terminal (After Palm Scanning, Return Payment Voucher) 
Member Authentication Device (After Palm Scan, Return User ID) 
Access Control Device (Control Door Opening After Palm Scan) 
otherwise, palm scanning will fail to output successfully. 
 Paymax_User Guide_v1.2  Device-Side Operation Manual_v1.2  
 Issue（） Security Level：PUBLIC 15 
 
 ● Batch Editing: Click "Batch Edit" to download the import template, fill it out, and complete the editing through batch import.  
 

 Paymax_User Guide_v1.2  Device-Side Operation Manual_v1.2  
 Issue（） Security Level：PUBLIC 16 
 
 

 Paymax_User Guide_v1.2  Device-Side Operation Manual_v1.2  
 Issue（） Security Level：PUBLIC 17 
 4. Device Mode Description: 4.1 Registration Mode: ● After an unregistered user places their palm, they will be prompted to scan their identity code (requires api integration to obtain the user's identity code, embedded in the self-registration H5 or APP; refer to the appendix for demo application procedures). If no identity code is placed within 60 seconds, the current collection fails and the palm needs to be repositioned. ● Registered users will display a welcome message after placing their palm; 
 

 Paymax_User Guide_v1.2  Device-Side Operation Manual_v1.2  
 Issue（） Security Level：PUBLIC 18 
  4.2 Recognition Mode: ● Registered users will complete the output based on the configured [Output Protocol] and [Output Content] after palm scanning, while unregistered users will display a "Palm not registered" prompt upon scanning; 
 

 Paymax_User Guide_v1.2  Device-Side Operation Manual_v1.2  
 Issue（） Security Level：PUBLIC 19 
 4.3 Hybrid Mode:  ● Process experience: When an unregistered palm is detected, the system switches to [Registration Threshold] and the device prompts "Please scan again"; The scenarios are as follows: ① Within 3 seconds after the user places their palm, first determine whether the palm has been registered. If it has been registered, directly trigger recognition; if it has not been registered, enter the registration process. ② If no palm is placed within 3 seconds, the system will revert to the previous silent mode. 
 

 Paymax_User Guide_v1.2  Device-Side Operation Manual_v1.2  
 Issue（） Security Level：PUBLIC 20 
 
 

 Paymax_User Guide_v1.2  Device-Side Operation Manual_v1.2  
 Issue（） Security Level：PUBLIC 21 
 Appendix 1: windows Host Computer Debugging Tool Download Links and Operating Instructions:https://doc.weixin.qq.com/doc/w3_AUwAxAbjAI0CNoiiPcmRjTvOP4WLz?scode=AJEAIQdfAAotDq6LsdAa8AEAZXAOc   Appendix 2: Palm Registration demo Tool Application ● Contact the designated person to apply for the palm enrollment tool from the Tencent Cloud team. We will deploy the web-based H5 version of the palm enrollment tool to the specified environment (mobile domain). ● In this tool, the mobile phone numbers used for palm enrollment verification must be provided simultaneously. The Tencent Cloud team will enable test access for these numbers during deployment;  
 Paymax_User Guide_v1.2  Device-Side Operation Manual_v1.2  
 Issue（） Security Level：PUBLIC 22 
 

 Paymax_User Guide_v1.2  Device-Side Operation Manual_v1.2  
 Issue（） Security Level：PUBLIC 23 
                                          Appendix 3: O2 Card and Palm Device (Access Control Scenario) Wiring Method Attachment：O2 Palm Code Authentication Device (Wall-mounted) Product Manual 2024-6-28 (Network Port Edition).docx                                                        
 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 24 
3   Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2 1. Device Management Platform: 1.1 Device Activation: Step 1: Go to the management backend, click "Device Management" to register the device SN;  
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 25 
 
  Step 2: Generate the device activation code. The activation code is valid for 10 minutes.  
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 26 
 
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 27 
Step 3: The device prompts "Scan to active" on startup. Scan the code to complete activation.    1.2 Device List: ● In the device list, you can view the device online status (detected approximately every 270s), device version, and module activation status. 
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 28 
 1.3 Device Upgrade: Step 1: Create an upgrade package and upload the configuration file. (The upgrade package and configuration file are provided by the Tencent Shuazhang Team. For existing uploaded packages, directly go to Step 2.) ● Go to "Device Management" → "Device Upgrade" → "Manage Upgrade Package" to access the Upgrade Package Management. 
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 29 
 ● Click "Upload Upgrade Package", upload the upgrade package and configuration file, enter the Upadate Log (which can be used to describe the purpose of this upgrade; if unsure how to fill it, enter 1), to complete the creation of the upgrade package (Note: The upgrade package and configuration file must strictly correspond one-to-one; otherwise, there is a risk of upgrade failure for the device). 
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 30 
 
   Step 2: Create an upgrade task and select the devices to upgrade. ● Return to Device Upgrade, click Create Upgrade Task to go to the task creation page: 
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 31 
 ● Select the app or rom to be upgraded, enter the device SNs (separated by commas; only full updates are supported in this phase), then click "Comfirm" to submit; 
    Step 3: ● Return to "Device Upgrade" to view the upgrade list, click "Continue upgrade" to deploy the task. 
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 32 
 ● You can view the upgrade progress in Task Detail: 
  
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 33 
   1.4 Remotely Obtain Logs: ● In Device Management, go to Device Log, click "Fetch Log", enter [Device SN], [Log Date], [Log Type] to issue the command to the device. ● The log type can be selected from [Application Log], [System Log], and [Custom Path]. If selecting a custom path, manually enter the path (this mode is typically used by Ops personnel for debugging and is not required for regular users). 
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 34 
  ● After issuing the command to obtain logs, you can view the command status in the list. If the logs are obtained successfully, you can download them. ● After obtaining the logs, please provide them to Ops personnel for troubleshooting according to the instructions. 
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 35 
   1.5 Remote Commands: The server can send commands to the device, and after the device accepts them, it will perform the corresponding actions. ● Includes commands and usage scenarios description: 
 
Instruction Usage Effect Application Scenario Restart the application The palm-scanning application in the device is restarted, but the device itself does not restart. In the event of an application abnormality, recover using this method. Restart the device The device has completed a restart. In the event of device abnormality, recover using this method. Restore factory settings The device ROM and palm-scanning APP are restored to the factory version, but the device does not require reactivation. 
In the event of device abnormality, recover using this method. Clear the TTS cache The device clears the local voice cache and reloads new voice templates. When the voice is updated, it is necessary to clear the local voice cache on the device. 
 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 36 
Note: The current device commands apply only to O2 devices.    ● Usage method: Go to Device Management → Remote Command and select the command to be delivered. 
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 37 
 Enter the device SN and select the target APP. 
  After completing the command delivery, you can view the execution progress in the list. 
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 38 
   2. Workload Platform: 2.1 Home Page Data Panel: ● After logging in, go to the homepage to view data, including: ① Today's Data Preview; ② Palm-scanning and Palm Enrollment Trends; ③ Number of Active Devices; ④ Historical Data; 
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 39 
 2.2 Palm Scanning Records: ● Go to the palm-scan records section to query records by date, personnel, business line, or merchant, with support for export and viewing. 
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 40 
 2.3 Business Line/Merchant Management: Note: Used to associate devices with merchants. After association, palm-scan records will display the corresponding merchant; otherwise, merchant information will be blank. Step 1: Create a Business Line: In the management backend, go to "Business Management" → "Business line management" to create a new business line (Business Line). Business lines can be used as independent units for data statistics. For example, when multiple retail brands are served simultaneously, each brand can be set up as a separate business line. Under the business line, you can continue to create affiliated merchants (Merchant). For example, when serving both Aeon and Starbucks, you can create two business lines: "Aeon" and "Starbucks," then create specific merchants under each business line (such as "Aeon Shop 1" and "Aeon Shop 2").  
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 41 
 
 Step 2: Create Merchant: Create merchant categories under each Business, with up to 5 levels of subcategories. If a category is deleted, you need to select to transfer the merchants under that category (they can only be transferred to the same Business line).  
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 42 
 
  Step 3: Create Merchant. In non-direct connection mode, there is no need to enter the Channel merchant number.  
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 43 
 
  Step 4: Associate devices under Merchant details. One Merchant can be associated with multiple devices; however, a single device can only be associated with one Merchant.  
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 44 
    2.4 Device Attribute Management: ● Property Description: Depending on the usage scenario, you can configure different properties on the server. The following are all configurable properties: Property Value Note Application Type You can select one of the following two types: [PAY] Used for payment scenarios. After palm scanning, it can output payment credentials and only supports HID signal output; [KYC] Used for identity verification and access control scenarios. After palm scanning, it can output user ID or physical card number, and supports Wiegand signal and HID signal output. If it does not involve returning payment credentials, please select the [KYC] type. Place your hand near the proximity sensing wake-up switch. 
Used to control whether the device can capture palm prints when a hand is placed during silent mode. It can be set to [Disable] or [Enable]. [Disable] In silent mode, placing a hand on the device will not trigger any response. The device can only be operated via the host computer's command environment. [Enable] You can set the "Post Wake-up Mode" to control the device state after proximity activation. Post Wake-up Mode Used to control the mode after the device is woken up by palm placement during silent mode: [Registration Mode] Unregistered users can complete palm registration after scanning their palm, while a welcome message will be displayed when scanning is performed by registered users. [Recognition Mode] Registered users will complete output based 
 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 45 
 
Property Value Note on the configured [Output Protocol] and [Output Content] after palm scanning, while unregistered users will display a "Palm not registered" prompt upon scanning. Note: For [PAY] type applications, this property can only be set to [Registration Mode]; for [KYC] type applications, it can be set to [Registration Mode] or [Recognition Mode]. Host Computer Post Wake-up Mode 
Used to control the mode after the device is woken up by host computer commands: [Recognition Mode] Registered users will complete output based on the configured [Output Protocol] and [Output Content] after palm scanning, while unregistered users will display a "Palm not registered" prompt upon scanning. [Hybrid Mode] Registered users will complete output based on the configured [Output Protocol] and [Output Content] after palm scanning, while unregistered users will first enter the registration process and automatically complete output according to the configured [Output Protocol] and [Output Content] upon successful registration. Output Protocol PAY type: Only supports [USB_Host] for connecting to the host computer; KYC type: Supports [USB_Host] and [Wiegand] (for access control scenarios); Output Content PAY type: Only supports [otc] output, that is, payment token; KYC type: In [USB_Host] mode, only [userid] can be output; in [Wiegand] mode, either [userid] or [physical card number] can be output. However, the [Wiegand] mode only supports numeric output. If this mode is selected, please note that both [userid] and [physical card number] must be purely numeric; otherwise, palm scanning will fail to output successfully. Language Supports Chinese, English, and Japanese. 
 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 46 
 ● Common Property Configuration: 
Property Value 
Independent Registration Terminal or Registration Machine (Device Not Connected to Host Computer) 
Payment Terminal (After Palm Scanning, Return Payment Voucher) 
Member Authentication Device (After Palm Scan, Return User ID) 
Access Control Device (Control Door Opening After Palm Scan) 
Application Type Select based on the actual scenario. If no payment credentials are involved, choose the [KYC] type. 
PAY KYC KYC 
Place your hand near the proximity sensing wake-up switch. 
Enabled Disabled. Disabled. Enabled 
Post Wake-up Mode Registration Mode - - Recognition Mode Host Computer Post Wake-up Mode - Select [Recognition Mode] or [Hybrid Mode] based on business requirements. 
Select [Recognition Mode] or [Hybrid Mode] based on business requirements. 
- 
Output Protocol - USB_Host USB_Host Wiegand Output Content - OTC userid Physical card 
 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 47 
 
Property Value 
Independent Registration Terminal or Registration Machine (Device Not Connected to Host Computer) 
Payment Terminal (After Palm Scanning, Return Payment Voucher) 
Member Authentication Device (After Palm Scan, Return User ID) 
Access Control Device (Control Door Opening After Palm Scan) 
number or userid If this mode is selected, please note that both [userid] and [physical card number] must be purely numeric; otherwise, palm scanning will fail to output successfully. 
 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 48 
  ● Method for changing device properties: ● Single Item Edit: Log in to the management backend, search for the corresponding device in [Business Management]→[Device Management], click [Edit] to complete the edit; after editing, the configuration will be synchronized to the corresponding device in about 1 minute;  
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 49 
 
 ● Batch Editing: Click "Batch Edit" to download the import template, fill it out, and complete the editing through batch import.  
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 50 
 
 

 Paymax_User Guide_v1.2  Server-Side Operations Manual (Business Platform + Device Management Platform)_v1.2  
 Issue（） Security Level：PUBLIC 51 
   2.5 User Management: ● Go to User Management to view current user information, including palm registration status and registration time, which can be used to check the current user registration status. 
        

