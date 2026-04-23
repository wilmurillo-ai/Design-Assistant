# O2 设备 USB 双向通信协议






刷掌服务平台
Paymax V1.2
Paymax_O2_Device_Bidirectional_Communication_Protocol_v1.2




Issue：
Date：
©2013-2026 Tencent Cloud. All rights reserved.

Copyright Notice
The content of this document is protected by copyright and belongs to Tencent Cloud. Unauthorized use, including copying, modifying, disseminating, publishing, or plagiarizing any part of this document, is strictly prohibited without prior written permission from Tencent Cloud.
This document contains internal data specific to Tencent Cloud and is accessible only to authorized individuals designated by Tencent Cloud. If you have obtained any portion of this document without proper authorization, please promptly delete it. Do not use this document or its content for any purpose, including copying, disclosure, or dissemination nor take any action on the basis of this document or its content.
 
Trademark Statement

Trademarks related to Tencent Cloud Services, including “Tencent” and “Tencent Cloud,” are owned by Tencent Cloud and/or its affiliates. Any third-party trademarks mentioned in this document are legally owned by their respective right holders.
 
Disclaimer
This document provides an overview of Tencent Cloud products and services available at the time of drafting. However, due to technical adjustments, project design changes, or other factors, products and services may evolve in the future, potentially affecting service scope and levels. Therefore, this document serves as a reference only.
Tencent Cloud does not guarantee the accuracy, suitability, or completeness of this document. The specific category, scope, and service level of Tencent Cloud products and services that you purchase and use will be governed by the contract between you and Tencent Cloud. Unless explicitly agreed upon, Tencent Cloud makes no express or implied commitments or guarantees regarding the content of this document.

Change History
Issue
Date
Changed By
Description

Contents



About This Document
Purpose
This document is used to help you quickly understand the version information of the product, including the release time of each version, new features, system optimization, module changes, and other details.
 
Intended Audience
This document is intended for:
	•	Customers
	•	Delivery PMs
	•	Delivery technical architects
	•	Delivery engineers
	•	Product delivery architects
	•	R&D engineers
	•	O&M engineers
 
Symbol Conventions
The symbols that may be found in this document are defined as follows.
Symbol
Description

Supplements the information in the main text.

Indicates a low-level potential risk, mainly information that users must read or consider. If the information is ignored, there may be certain adverse consequences due to misoperation or the operation may not be successful.

Indicates a medium-level potential risk, such as high-risk operations that users should pay attention to. If the information is ignored, there may be device damage, data loss, performance deterioration, or other unpredictable results.

Indicates a high-level potential risk, such as prohibited operations that users should pay attention to. If the operations are not avoided, there will be serious problems such as system crashes and irreparable data loss.


	•	Paymax_O2_Device_Bidirectional_Communication_Protocol_v1.2
Definitions
	•	Palm-scanning device (lower-level machine): A terminal device integrated with palm-scanning algorithms. In this document, it specifically refers to the O2.
	•	Host computer: Works in coordination with palm-scanning devices through bidirectional communication protocols to implement business logic. Common examples include PCs and cash registers.
	•	Palm-scanning service: An access layer service connected to palm-scanning devices, used for processes such as identification and palm registration.
	•	Business service: A customer-owned business service, typically invoked via cloud-to-cloud requests from the palm-scanning service. It is triggered after user identification to execute specific business logic, such as payment processing.
 
[Host Computer -> Palm-Scanning Device] Communication Protocol
Function
functionId
data
Description
Start palm-scanning
6001
Null
① Activate the palm-scanning device;
② At this point, a successful palm scan can return identity information to the host computer;
Terminate palm-scanning
6002
Null
Terminate the palm-scanning device

 
[Palm-Scanning Device->Host Computer] Communication Protocol
General Protocol Structure

{
 "code": <<code>>,
  "msg": "xxx",
  "data": {
  }
}
 
 
code: Return code, where 0 indicates success;
msg: Return message, for error cause description only; must not be used for logical judgment or UI display;
data: Business data JSON structure


Function
functionId
data
Description
Recognition Result Command
6001
json string:
{
  "code": 0,
  "msg": "success",
  "data": {
    "user_id": "xxxx",
    "token": "xxxx",
    "biz_info": {
    }
  }
}
After successful recognition, the palm-scanning device returns information to the host computer;
Structure Description of data:
user_id: User id, returned only in identity verification scenarios, not returned in payment scenarios;
token: Dynamic token for user identity, such as payment credential;
biz_info: Passthrough data returned by the business server, optional, determined by the business-side service.
Remarks: In actual development, otc can be understood as a one-time dynamic token.
Termination Result
6002
json string:
{
  "code": 0,
  "msg": "success",
  "data": {}
}
When the host computer terminates the palm-scanning process, the operation result returned by the palm-scanning device;
data is empty.
Status of key intermediate nodes in palm-scanning
6003
json string:
{
  "code": 0,
  "msg": "success",
  "data": {
      "stage": 1
  }
}
Business nodes returned during intermediate processes; the host computer can provide relevant interactions or reminders based on this;
The code remains 0, and errors are uniformly handled at 6001.
 
Structure Description of data:
stage: node in the intermediate process

 
Error Code Enumeration [Palm-Scanning Device -> Host Computer]
⚠️ Note: Grayed-out items are newly added in this version; the original error code 306 has been removed and replaced by 206.
Function
functionId
Event
code
data
Description
Recognition Result Command
6001
Successful
0
functionId: 6001{
  "code": 0,
  "msg": "sucess",
  "data": {
    "user_id": "xxxx",
    "token": "xxxx",
    "biz_info": {
    }
  }
}
Upon successful recognition, return user_id (identity information), token (dynamic business token, such as payment credential), and biz_info (passthrough data from the business platform).


The device has been woken up and cannot be re-woken.
101
 
6001 failed to wake up the device because it is already in a woken state.


Palm print enrollment failed; QR code not detected within timeout.
202
 
Palm print registration process failed; QR code not detected within timeout.


Palm print enrollment failed; invalid identity code.
203
 
Palm print registration process failed; the code scanned by the user is not an identity QR code.


Palm print enrollment failed; invalid QR code.
204
 
Palm print registration process failed; the QR code scanned by the user is an identity QR code, but it may be expired, invalid, or incorrect.


Secondary palm print enrollment in [Hybrid Mode] timed out.
205
 
Hybrid Mode detected that the user is not registered and automatically initiated secondary palm print enrollment, but the user did not scan their palm within the specified time.


In [Recognition Mode], the user placed their palm, detecting an unregistered palm.
206
 
In Recognition Mode, the user scanned their palm and recognition was successful, but the palm is not registered, causing the payment/verification process to fail.


[Full Mode] After palm placement, the palm was judged to have quality issues; after 3 consecutive retries, quality issues persist, and the current collection is aborted.
207
 
[Full Mode] Palm quality issues detected; after 3 consecutive retries, quality issues persist. Collection aborted, and the payment/verification/registration process fails.


[Full Mode] After palm placement, the palm was judged to have quality issues; a reminder was issued to place the palm again, but no palm was placed within the timeout period, and the current collection was aborted.
208
 
In Full Mode, after palm placement, the palm was judged to have quality issues; a reminder was issued to place the palm again, but no palm was placed within the timeout period, and the current collection was aborted.


Palm-scanning device network abnormal.
301
 
During the identification/registration stage, a network issue occurred with the API request, resulting in request failure.


Palm-scanning service abnormal.
302
functionId: 6001{
  "code": 302,
  "msg": "recognize request failed, code: 1000xx, message: no upstream a vailable",
  "data": {
  }
}
Default return for failed recognition API (error occurred during the recognition stage)
 


Business service abnormal.
303
functionId: 6001{
  "code": 303,
  "msg": "payment request failed, code: 1000xx, message: no upstream a vailable",
  "data": {
  }
}
Business service abnormal due to network issues (indicating service unavailability).
Business service (payment) abnormal may occur during both the identification and registration stages.


Business service judgment abnormal.
304
functionId: 6001{
  "code": 304,
  "msg": "payment service returned failure",
  "data": {
   "token": "",
    "biz_info": {
        "mock_biz_code" : -10000,
        "mock_biz_others": "User has been banned"
    }
  }
}
The backend request to the business service is successful, but the service returns a failure.
Business service (payment) request returned as not permitted; this may occur during both the identification and registration stages.


Registration service abnormal
305
functionId: 6001{
  "code": 305,
  "msg": "register request failed, code: 100030, message: no upstream a vailable",
  "data": {
  }
}
Default return for failed registration API (error occurred during the registration stage)
Termination Result
6002
Successful Termination
0
 
The host computer sends 6002 to the palm-scanning device, and the device successfully terminates.


Termination process failure.
The current device is not in the awake state.
103
 
The host computer sends 6002 to the palm-scanning device, and since the device was not awake at that time, it did not perform the termination operation.


The current process cannot be aborted, for example, during recognition or when network requests are not completed.
104
 
The host computer sends 6002 to the palm-scanning device, but the device is currently in a non-interruptible state, such as during recognition or when network requests are not completed.
Status of key intermediate nodes in palm-scanning
6003
Palm capture successful, awaiting user to present code.
0
{
  "code": 0,
  "msg": "success",
  "data": {
     "stage": 1
  }
}
Detected a user palm scan, and the user is not registered, so it enters the code presentation operation.


Palm enrollment and user creation successful.
0
{
  "code": 0,
  "msg": "success",
  "data": {
     "stage": 2
  }
}
The user presented the code, and the registration operation was successfully performed.


Hybrid mode, placing an unregistered palm, entering the registration phase.
0
{
  "code": 0,
  "msg": "success",
  "data": {
     "stage": 3
  }
}
Hybrid Mode detected that the user is not registered and prompts the user to scan their palm again.

 
 
 

