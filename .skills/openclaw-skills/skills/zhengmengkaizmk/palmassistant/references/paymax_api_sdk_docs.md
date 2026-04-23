# Paymax 刷掌服务平台 API 与 SDK 对接文档






刷掌服务平台
Paymax V1.2
Paymax_Open API Document_v1.2




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


	•	Paymax_Open API Document_v1.2
1. Obtain Luzhang QR Code for Identity Authentication API 
 1.1. Feature Description
Based on the user information passed from the payment gateway, create a corresponding user record in the PalmScan Platform, while generating a QR code string associated with the user record. (Upon successful scanning, the PalmScan Platform will bind the user's palmprint to the associated record.)
1.2. Request Method:
POST(application/json)
 
 1.3. Request Address:
https://domain/cgi-bin/user-palm-register
See attachment for signature.
 
1.4. Input Parameters Description:
Parameter
Required
Type
Example
Description
user_id
Yes
string[4,64]
aeon_user
User Unique Identifier
user_name
No
string[1,32]
Aj4FDJncSD3den==
Username (to be encrypted)
payment_token
Yes
string[1,1024]
 
Aj4FJncSD3den==
Payment Voucher (to be encrypted)
phone_no
No
string[4,20]
Aj4FDJncSD3den==
Mobile number (to be encrypted)
physical_card_no
No
string[0,32]
Aj4FDJncSD3den==
Physical card number (to be encrypted)

 
1.5. Output Parameter Description:
Parameter
Type
Example
Description
code
int
0
Return code, indicating whether the current request is successful. A value of 0 indicates that the current request is successful.
message
string
success.
Return Description
code_str
string
palmpact://sdfiwnenvlkxcvi
Palm print QR code

 
1.6.  Return Reminder:
code Table
Return Code
Description
Solutions
0
Successful
 
1000
Invalid parameter.
View the message and check the parameters.
1100
Internal server error.
Contact the developers.
10020
The user is already registered.
Check whether the user is registered.

 
2. [Luzhang Result Query] Query Luzhang Result API 
2.1. Feature Description
Provided to the payment gateway (the APP polls the payment gateway) for polling the transaction result. If the result returns 0-pending, it needs to continue polling.

2.2. Request Method:
POST(application/json)
 
2.3. Request URL:
https://domain/cgi-bin/check-palm-record-result
See attachment for signature.
 
2.4. Input Parameters:
Parameter
Required
Type
Example
Description
code_str
Yes
string
palmpact://sdfiwnenvlkxcvi
Palm print QR code

 
2.5. Output Parameters Description:
Parameter
Type
Example
Description
code
int
0
Return code, indicating whether the current request is successful. A value of 0 indicates that the current request is successful.
message
string
success.
Return Description
result
int
1
Palm print result: 0-Pending; 1-Success; 2-Failure
fail_reason
string
invalid code_str
Reason for palm print enrollment failure
palm_direction
int
1
Palm print orientation: 0-Invalid; 1-Left hand; 2-Right hand
physical_card_no
string
TC1234
Physical card number

2.6. Return Reminder:
code Table
Return Code
Description
Solutions
0
Successful
 
1000
Invalid parameter.
View the message and check the parameters.
1100
Internal server error.
Contact the developers.
10007
QR code is invalid or expired.
Re-obtain the QR code.

 
3. [User Palm Enrollment Status] Query Palm Enrollment Status API 
3.1. Feature Description
Provided to the payment gateway for querying the palmprint status (registered or not registered) of the user corresponding to the user_id. This project does not have a pre-registered palmprint status (PreRegistered). Before the "1. [Obtain Palmprint QR Code] Identity Verification API" is called, it will return a user does not exist error.
            
3.2. Request Method:
POST(application/json)
 
3.3. Request URL:
https://domain/cgi-bin/get-user-palm
See attachment for signature.
 
3.4. Input Parameters Description:
Parameter
Required
Type
Example
Description
user_id
Yes
string
"aeon_user"
User Unique Identifier

 
3.5. Output Parameter Description:
Parameter
Type
Example
Description
code
int
0
Return code, indicating whether the current request is successful. A value of 0 indicates that the current request is successful.
message
string
user not found.
Return Description
palm_state
string
Registered
Palm registration status: Registered - Registered; Unregistered - Unregistered; PreRegistered - Pre-registered (air palm registration completed but not yet activated on device)
palm_direction
int
1
Palm print orientation: 0-Invalid; 1-Left hand; 2-Right hand

 
3.6. Return Reminder:
code Table
Return Code
Description
Solutions
0
Successful
 
1000
Invalid parameter.
View the message and check the parameters.
1100
Internal server error.
Contact the developers.
10003
The user does not exist.
Check whether the user is registered.

 
4. Delete/Unbind Palmprint: Delete Palmprint API
4.1. Feature Description
For users who have registered their palmprints, unbind the corresponding palmprint information.
4.2. Request Method:
POST(application/json)
 
4.3.     Request Address:
https://domain/cgi-bin/delete-palm
See attachment for signature.
 
4.4. Input Parameter Description:
Parameter
Required
Type
Example
Description
user_id
Yes
string
"aeon_user"
User Unique Identifier

 
4.5. Output Parameters Description:
Parameter
Type
Example
Description
code
int
0
Return code, indicating whether the current request is successful. A value of 0 indicates that the current request is successful.
message
string
user not found.
Return Description

 
4.6.     Return Reminder:
code Table
Return Code
Description
Solutions
0
Successful
 
1000
Invalid parameter.
View the message and check the parameters.
1100
Internal server error.
Contact the developers.
10003
The user does not exist.
Check whether the user is registered.
10021
The user has not registered their palm print.
Check whether the user has registered their palm print.

 
 
5. Palm Print Status Change Push Notification API 
5.1. Feature Description
Changes in the user's palm print status (such as registration and deletion) will be asynchronously notified to the payment gateway.

5.2.     Request Method:
POST(application/json)
 
5.3. Request Address:
Customer-provided push URL
Signature verification. For details, refer to section 14.3.
 
5.4.  Input Parameters Description:
Parameter
Required
Type
Example
Description
action
Yes
string[1,36]
"update_palm"
Event type: "update_palm": Palm print status change
user_id
Yes
string[4,64]
"aeon_user"
User Unique Identifier
palm_state
Yes
 
string[1,36]
 
Palm registration status: Registered - Enrolled; Unregistered - Not enrolled; PreRegistered - Pre-enrolled (completed air registration but not activated via device verification)
Palm registration status: Registered - Registered; Unregistered - Unregistered; PreRegistered - Pre-registered (air palm registration completed but not yet activated on device)
palm_direction
Yes
int
1
Palm print orientation: 0-Invalid; 1-Left hand; 2-Right hand
 

 
5.5. Output Parameters Description:
Parameter
Type
Example
Description
code
int
0
Return code, indicating whether the current request is successful. A value of 0 indicates that the current request is successful.
message
string
user not found.
Return Description

 
 5.6.     Return Reminder:
code Table
Return Code
Description
Solutions
0
Successful
 

A non-zero return code indicates a push failure.
 
 
6.[Palm Verification Record] API for Querying Palm Verification Records 
6.1. Feature Description
Retrieve palmprint records list, which can be filtered by user, merchant, or time range criteria.
           
6.2. Request Method:
POST(application/json)
 
6.3. Request URL:
https://domain/cgi-bin/pass-records/list
See attachment for signature.
 
 6.4. Input Parameters Description:
Parameter
Required
Type
Example
Description
pagination
Yes
object
 
Pagination parameters
 
offset
Yes
int
0
Offset
 
limit
Yes
int
100
Record limit, maximum 100 records queried
filter
No
object
 
Filter Condition
 
user_id
No
string
id12345
Either user_id or merchant ID must be provided.
 
out_merchant_id
No
string
id12345
Either user_id or merchant ID must be provided.
 
start_time
No
int
1761791940
Start timestamp
 
end_time
No
int
1761791940
End timestamp

 
6.5. Output Parameters Description:
Parameter
Type
Example
Description
code
int
0
Return code, indicating whether the current request is successful. A value of 0 indicates that the current request is successful.
message
string
success
Return Description
list
array
 
Palm scan record list
 
user_id
string
id1234
User ID
 
user_name
string
zhangsan
Username.
 
device_sn
string
X8AZ1S1E3500011C8TJ5CB5
Device sn
 
device_name
string
test_device
Device Name
 
palm_time
int
1761791940
Palm-scanning timestamp
 
business_line_id
string
efc8fd41-8a8e-479d-a1a4-f268e76c8dc0
Business Line id
 
business_line_name
string
businessline
Business Line Name
 
out_merchant_id
string
id1234
Merchant id
 
out_merchant_name
string
testmerchant
Merchant Name
 
category_id
string
efc8fd41-8a8e-479d-a1a4-f268e76c8dc0
Merchant Category id
 
category_name
string
category
Merchant Category Name
 
palm_direction
int
1
Palm print orientation: 0-Invalid; 1-Left hand; 2-Right hand
 
 

 
6.6. Return Reminder:
code Table
Return Code
Description
Solutions
0
Successful
 
1000
Invalid parameter.
Check parameters.
1100
Internal server error.
Contact the developers.
70064
Palm scan record could not be obtained.
Contact the developers.



7. [Merchant] Creating a New Merchant API 
7.1. Feature Description
Create merchants (stores) under a business line. (category_id is the merchant category ID in the Palm Pay platform, which identifies the business line.)
7.2.     Request Method:
POST(application/json)
 
7.3. Request URL:
https://domain/cgi-bin/merchant/create
See attachment for signature.
 
 7.4. Input Parameters Description:
Parameter
Required
Type
Example
Description
out_merchant_id
Yes
string[1,36]
ab123
Merchant id
out_merchant_id
Yes
string[1,36]
Test Merchant
Merchant Name
category_id
Yes
string[36,36]
efc8fd41-8a8e-479d-a1a4-f268e76c8dc0
Merchant Category id

 
 7.5. Output Parameter Description:
Parameter
Type
Example
Description
code
int
0
Return code, indicating whether the current request is successful. A value of 0 indicates that the current request is successful.
message
string
success
Return Description
data
object
 
Returned data
 
out_merchant_id
string
ab123
Merchant id
 
out_merchant_name
string
Test Merchant
Merchant Name
 
category_id
string
efc8fd41-8a8e-479d-a1a4-f268e76c8dc0
Merchant Category id
 
internal_merchant_id
string
b7c0d4a0-86f1-41f3-8051-24959ddb2156
Platform Merchant id
 
business_line_id
string
38a9f1f3-2238-4bfd-9975-67fb9e742ab1
Business Line id

 
7.6. Return Reminder:
code Table
Return Code
Description
Solutions
0
Successful
 
1000
Invalid parameter.
Check parameters.
1100
Internal server error.
Contact the developers.
70038
Internal creation failure
Contact the developers.
70045
Merchant already exists.
Modify merchant id or name.

    
8. Obtain Merchant API 
8.1.     Feature Description
Batch retrieve the merchant list, and filter by specifying merchant id or merchant name.

8.2. Request Method:
POST(application/json)
 
8.3.      Request URL:
https://domain/cgi-bin/merchant/list
See attachment for signature.
 
8.4. Input Parameter Description:
Parameter
Required
Type
Example
Description
pagination
Yes
object
 
Pagination parameters
 
offset
No
int
0
Offset
 
limit
Yes
int
100
Record limit, maximum 100 records queried
filter
No
object
 
Filter Condition
 
out_merchant_id
No
string
ab123
Merchant id
 
out_merchant_name
No
string
Test Merchant
Merchant Name

 
8.5.     Output Parameter Description:
Parameter
Type
Example
Description
code
int
0
Return code, indicating whether the current request is successful. A value of 0 indicates that the current request is successful.
message
string
success
Return Description
total
int
1
Total number
list
array
 
Merchant List
 
out_merchant_id
string
ab123
Merchant id
 
out_merchant_name
string
Test Merchant
Merchant Name
 
category_id
string
efc8fd41-8a8e-479d-a1a4-f268e76c8dc0
Merchant Category id
 
category_name
string
Test Merchant Category
Merchant Category Name
 
internal_merchant_id
string
b7c0d4a0-86f1-41f3-8051-24959ddb2156
Platform Merchant id
 
business_line_id
string
38a9f1f3-2238-4bfd-9975-67fb9e742ab1
Business Line id
 
business_line_name
string
Test Business Line
Business Line Name

 
8.6.     Return Reminder:
code Table
Return Code
Description
Solutions
0
Successful
 
1000
Invalid parameter.
Check parameters.
1100
Internal server error.
Contact the developers.
70041
Internal query failure
Contact the developers.

9. [Merchant] Edit API 
9.1. Feature Description
Locate the corresponding merchant record using the platform merchant id, and modify its merchant name and merchant category.

9.2. Request Method:
POST(application/json)
 
9.3. Request URL:
https://domain/cgi-bin/merchant/edit
See attachment for signature.
 
9.4. Input Parameter Description:
Parameter
Required
Type
Example
Description
out_merchant_name
No
string[1,36]
Merchant B
Merchant Name
category_id
No
string[36,36]
efc8fd41-8a8e-479d-a1a4-f268e76c8dc0
Merchant Category id
internal_merchant_id
Yes
string[36,36]
b7c0d4a0-86f1-41f3-8051-24959ddb2156
Platform Merchant id


9.5. Output Parameters Description:
Parameter
Type
Example
Description
code
int
0
Return code, indicating whether the current request is successful. A value of 0 indicates that the current request is successful.
message
string
success
Return Description
data
 
object
 
 
 
out_merchant_id
string
ab123
Merchant id
 
out_merchant_name
string
Merchant B
Merchant Name
 
category_id
string
efc8fd41-8a8e-479d-a1a4-f268e76c8dc0
Merchant Category id
 
internal_merchant_id
string
b7c0d4a0-86f1-41f3-8051-24959ddb2156
Platform Merchant id
 
business_line_id
string
38a9f1f3-2238-4bfd-9975-67fb9e742ab1
Business Line id

 
9.6. Return Reminder:
code Table
Return Code
Description
Solutions
0
Successful
 
1000
Invalid parameter.
Check parameters.
70039
Internal edit failed.
Contact the developers.
70044
Merchant does not exist.
Check whether the platform merchant id is correct.


10.[Merchant] Delete Merchant API 
10.1. Feature Description
Delete the merchant corresponding to the specified platform merchant id.

10.2. Request Method:
POST(application/json)
 
10.3. Request Address:
https://domain/cgi-bin/merchant/delete
See attachment for signature.
 
10.4. Input Parameters Description:
Parameter
Required
Type
Example
Description
internal_merchant_id
Yes
string
b7c0d4a0-86f1-41f3-8051-24959ddb2156
Platform Merchant id

 
10.5. Output Parameter Description:
Parameter
Type
Example
Description
code
int
0
Return code, indicating whether the current request is successful. A value of 0 indicates that the current request is successful.
message
string
success
Return Description

 
10.6. Return Alert:
code Table
Return Code
Description
Solutions
0
Successful
 
1000
Invalid parameter.
Check parameters.
1100
Internal server error.
Contact the developers.
70040
Internal merchant deletion failed.
Contact the developers.
70044
Merchant does not exist.
Merchant does not exist. Deletion is not required.
70049
Merchant has bound devices.
Unbind the device first, then delete it.


11.[Device] Input Device API 
11.1. Feature Description
Batch register devices and bind them to the merchant corresponding to the merchant id (optional); configure device attributes (optional, default values will be populated if left empty). The interface allows duplicate registrations, but note that empty device attributes will override existing values with defaults.

11.2.     Request Method:
POST(application/json)
 
11.3. Request URL:
https://domain/cgi-bin/devices/add
See attachment for signature.
 
11.4. Input Parameter Description:
Parameter
Required
Type
Example
Description
device_sn_list
Yes
array
["X8AZ1S1E3500011C8TJ5CB5","X8AZ102E4500017L5F2PNUL"]
Device Sn list, up to 20 devices
out_merchant_id
 
No
string[1,36]
b7c0d4a0-86f1-41f3-8051-24959ddb2156
Merchant id
device_property
No
object
 
 
 
palm_behavior
No
object
 
Palm scan behavioral attributes
 
 
application_type
No
string
PAY (default value)
Application type: KYC/PAY
 
 
palm_proximity_wake_up
No
string
OFF (default value)
Palm proximity sensing wake-up switch ON/OFF
 
 
post_proximity_mode
No
string
ENROLLMENT (default value)
Proximity wake-up mode: ENROLLMENT/RECOGNITION
 
 
post_host_mode
No
string
HYBRID (default value)
Host computer mode after wake-up: RECOGNITION/HYBRID
 
 
output_protocol
No
string
USB_HOST (default value)
Output protocol: USB_HOST/WIEGAND
 
 
output_content
No
string
OTC (default value)
Output content: USER_ID/OTC/CARD_NUMBER
 
device_behavior
No
object
 
Device common properties
 
 
language
No
string
en_US (default value)
Language: en_US-English; jp_JP-Japanese; zh_CN-Chinese

 
11.5. Output Parameter Description:
Parameter
Type
Example
Description
code
int
0
Return code, indicating whether the current request is successful. A value of 0 indicates that the current request is successful.
message
string
success
Return Description
failed_devices
array
 
 
 
device_sn
string
X8AZ1S1E3500011C8TJ5CB5
Device Sn
 
reason
string
set device property value format invalid.
Failure reason

11.6 Return Reminder:
code Table
Return Code
Description
Solutions
0
Successful
 
1000
Invalid parameter.
Check parameters.
1100
Internal server error.
Contact the developers.
70065
Device enrollment failed.
Contact the developers.

 
 
12.[Device] Obtain Device API 
12.1. Feature Description
Obtain the device list by specifying the device SN or merchant name to filter.

12.2. Request Method:
POST(application/json)
 
12.3. Request Address:
https://domain/cgi-bin/devices/list
See attachment for signature.
 
12.4. Input Parameter Description:
Parameter
Required
Type
Example
Description
pagination
Yes
object
 
Pagination parameters
 
offset
Yes
int
0
Offset
 
limit
Yes
int
100
Record limit, maximum 100 records queried
filter
No
object
 
Filter Condition
 
device_sn
No
string
X8AZ1S1E3500011C8TJ5CB5
Device Sn
 
out_merchant_id
No
string[1,36]
b7c0d4a0-86f1-41f3-8051-24959ddb2156
Merchant id

 
12.5. Output Parameter Description:
Parameter
 
Type
Example
Description
code
int
0
Return code, indicating whether the current request is successful. A value of 0 indicates that the current request is successful.
message
string
success
Return Description
list
array
 
Device Info List
 
device_sn
string
X8AZ1S1E3500011C8TJ5CB5
Device sn
 
out_merchant_id
string
b7c0d4a0-86f1-41f3-8051-24959ddb2156
Merchant id
 
out_merchant_name
string
Test Merchant
Merchant Name
 
summary
string
Test Device
Description
 
activate_state
int
3
Activation Status: 0-Not activated, 1-Activating, 2-Initialized, 3-Activated
 
device_property
object
 
 
 
 
palm_behavior
object
 
Palm scan behavioral attributes
 
 
 
application_type
string
PAY
Application type: KYC/PAY
 
 
 
palm_proximity_wake_up
string
OFF
Palm proximity sensing wake-up switch ON/OFF
 
 
 
post_proximity_mode
string
ENROLLMENT
Proximity wake-up mode: ENROLLMENT/RECOGNITION
 
 
 
post_host_mode
string
HYBRID
Host computer mode after wake-up: RECOGNITION/HYBRID
 
 
 
output_protocol
string
USB_HOST
Output protocol: USB_HOST/WIEGAND
 
 
 
output_content
string
OTC
Output content: USER_ID/OTC/CARD_NUMBER
 
 
device_brhavior
object
 
Device Behavioral Attributes
 
 
 
language
string
en_US
Language: en_US/jp_JP/zh_CN

 
 
12.6. Return Reminder:
code Table
Return Code
Description
Solutions
0
Successful
 
1000
Invalid parameter.
Check parameters.
1100
Internal server error.
Contact the developers.
70066
Failed to obtain the device.
Contact the developers.

 
13 [Device] Edit Device API  
13.1. Feature Description
Edit the device.

13.2. Request Method
POST(application/json)

13.3. Request Address
https://domain/cgi-bin/devices/edit
See attachment for signature.

13.4. Input Parameters Description:
Parameter
Required
Type
Example
Description
device_sn
Yes
string
X8AZ1S1E3500011C8TJ5CB5
device Sn 
device_property
No
object
 
 
 
palm_behavior
No
object
 
Palm scan behavioral attributes
 
 
application_type
No
string
PAY
Application type: KYC/PAY
 
 
palm_proximity_wake_up
No
string
OFF
Palm proximity sensing wake-up switch ON/OFF
 
 
post_proximity_mode
No
string
ENROLLMENT
Proximity wake-up mode: ENROLLMENT/RECOGNITION
 
 
post_host_mode
No
string
HYBRID
Host computer mode after wake-up: RECOGNITION/HYBRID
 
 
output_protocol
No
string
USB_HOST
Output protocol: USB_HOST/WIEGAND
 
 
output_content
No
string
OTC
Output content: USER_ID/OTC/CARD_NUMBER
 
device_behavior
No
object
 
Device common properties
 
 
language
No
string
en_US
Language: en_US-English; jp_JP-Japanese; zh_CN-Chinese

13.5. Output Parameter Description:
Parameter
Type
Example
Description
code
int
0
Return code, indicating whether the current request is successful. A value of 0 indicates that the current request is successful.
message
string
success
Return Description

13.6.     Return Reminder:
code table
Return Code
Description
Solutions
0
Successful
 
1000
Invalid parameter.
Check parameters.
1100
Internal server error.
Contact the developers.

 
 
14. Palm Scan Records Notification API 
 14.1. Feature Description
When the user successfully swipes their palm, the details of the palm-swipe event will be pushed to the request URL.

14.2. Request Method:
POST(application/json)
 
14.3. Request URL:
Customer-provided address.
Signature verification. For details, refer to section 14.3.
 
 14.4. Input Parameter Description:
Parameter
Required
Type
Example
Description
user_id
Yes
string
useid
User ID
user_name
Yes
string
user
Username
device_sn
Yes
string
X8AZ1S1E3500011C8TJ5CB5
Device sn
palm_time
Yes
int
1761791940
Palm-scanning time
business_line_id
Yes
string
efc8fd41-8a8e-479d-a1a4-f268e76c8dc0
Business Line id
business_line_name
Yes
string
Test Business Line
Business Line Name
out_merchant_id
Yes
string
ab123
Merchant id
out_merchant_name
Yes
string
Test Merchant
Merchant Name
category_id
Yes
string
efc8fd41-8a8e-479d-a1a4-f268e76c8dc0
Merchant Category id
category_name
Yes
string
Test Merchant Category
Merchant Category Name
palm_direction
Yes
int
1
Palm print orientation: 0-Invalid; 1-Left hand; 2-Right hand
 

 
 14.5. Output Parameters Description:
Parameter
Type
Example
Description
code
int
0
Return code, indicating whether the current request is successful. A value of 0 indicates that the current request is successful.
message
string
success
Return Description

 
14.6. Return Reminder:
code Table
Return Code
Description
Solutions
0
Successful
 

 
15.(User) Create User API 
15.1. Feature Description
Create a user.

15.2. Request Method:
POST(application/json)
 
 15.3.     Request URL:
https://domain/cgi-bin/users/create
Signature verification, see Appendix.
 
15.4.  Input Parameter Description:
Parameter
Required
Type
Example
Description
user_id
Yes
string
useid
User ID
user_name
No
string
user
Username
phone_no
No
string
123456789
Mobile Number
physical_card_no
No
string
TC1234
Physical card number

 
15.5. Output Parameters Description:
Parameter
Type
Example
Description
code
int
0
Return code, indicating whether the current request is successful. A value of 0 indicates that the current request is successful.
message
string
success
Return Description

 
15.6.     Return Alert:
code Table
Return Code
Description
Solutions
0
Successful
 
10011
user id already exists.
 
1000
Invalid parameter format.
 

 
16.[User] Edit User API 
16.1. Feature Description
Create a user.

16.2. Request Method:
POST(application/json)
 
16.3. Request Address:
https://domain/cgi-bin/users/modify
Signature verification, see Appendix.
 
16.4. Input Parameters Description:
Parameter
Required
Type
Example
Description
user_id
Yes
string
useid
User ID
user_name
No
string
user
Username
phone_no
No
string
123456789
Mobile Number
physical_card_no
No
string
TC1234
Physical card number

 
16.5. Output Parameter Description:
Parameter
Type
Example
Description
code
int
0
Return code, indicating whether the current request is successful. A value of 0 indicates that the current request is successful.
message
string
success
Return Description

 
16.6. Return Notification:
code Table
Return Code
Description
Solutions
0
Successful
 
10003
user id does not exist.
 
1000
Invalid parameter format.
 


17.[User] Delete User API 
17.1. Feature Description
Delete user.

17.2. Request Method:
POST(application/json)
 
17.3. Request URL:
https://domain/cgi-bin/users/delete
Signature verification, see Appendix.
 
17.4.     Parameter Description:
Parameter
Required
Type
Example
Description
user_id
Yes
string
useid
User ID

 
17.5. Output Parameters Description:
Parameter
Type
Example
Description
code
int
0
Return code, indicating whether the current request is successful. A value of 0 indicates that the current request is successful.
message
string
success
Return Description

 
17.6.     Return Reminder:
code Table
Return Code
Description
Solutions
0
Successful
 
10003
user id does not exist.
 

 
Appendix: Encryption and Signature Verification
18.1.     Encryption Algorithm
User name (user_name), phone number (phone_no), and payment Token (payment_token) must be transmitted in encrypted form.
The Micro Card Palm-Swipe Platform generates RSA public-private key pairs, provides the public key to customers, who then use it to encrypt data.
Encryption Algorithm: RSA public key encryption, OAEP Padding
 

Base64Encode(RSAEncrypt(PublicKey, StringData))


 
Example:

Assume user_name = "Adon".
EncryptedString = Base64Encode(RSAEncrypt(PublicKey, "Adon")) Result:
"cphwlo9p9KRDttI9EmjTOFspwZofcGiwD8STJHufFCM9EC92p8w2b2/+pOi4OK+Lgb+5gW2DbZEc5pRyz6ZvhzQCXi6dEtLZa/JXIBCT0kgsyzaT3fsYaLeuDKyasj0y2P02nui2AGwHS98FSi0FzVAwAgcsOnbZOkQW547atFRMxTXO/tNI68p5uNcoAwLKjTPK4NkQB14P1lf3lXSWdB2xsP4kp3syL3xYlboAn+mjU4gNHCWkuIVLWLMyL3NitmG1AGCryEu0lX0VqzqX/KLrlR1efCi8CGY9Pw2kuBzkx58RbJ1YQ5RUoiOB8VLHjd0YS8DjeH8j66n4s0GZZg==","phone_no":"EdEvUlP6Gasqw5TkC3ykgD5C2T8UOJo+VKmx2oQryXNS+m8FyeSlr/GEzb2O8/Sefdk2spMbfw9E+MUkLz3dniKLqdmArI8TYJ/kGLG3f1wtVA3ctQO52+eOLr7GaYHCxES33kfJuhLo3+yEIaAJJ3dhTMiDuKut8uLpTIpsXDoRrFs7GflwlQR1+H4sdiL5hv79ex1WjwJ0mS2WP+x+MNBenWv+n4XktPp0QenyZ88G68vI6X0sHUSoeaK+7GSAJyjdmbj3OwRd1+xTq005afKy9mHDw06axRGZ8U+is1jYas/yVSH/n7iqAU8XwZ1JV1b68bRVYa//fhw6zfu3FQ=="
 
RSADecrypt(PrivateKey, Base64Decode(EncryptedString)) Result:
"Adon"


 
18.2. Open API Signature
See the API signature documentation for details.
Open API Signature.pdf

18.3. Push Signature Verification
Push API Signature Verification Process.pdf
 
 

