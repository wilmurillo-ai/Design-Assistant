# Paymax V1.2 Release Notes






刷掌服务平台
Paymax V1.2
Paymax_ReleaseNote_v1.2




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


	•	Paymax_ReleaseNote_v1.2
e-document version:  03  
Release Date:  March 16, 2026


Change History
Issue
Release Date
Changed By
Description
01
2025-03-10
seasonyuan
First release, as a public version starting from v1.2.














V1.2
Release Time: 2026-03-16
The version change notes for this release are as shown in the figure below:

Change Module
Change Type
Detailed Description
Algorithm Management Platform
New feature
Palm feature extraction: Receives palm images encrypted and uploaded by the device, automatically extracts fused features of palmprints and palm veins in the cloud, and stores them in the feature repository after deduplication processing.

New feature
Cloud recognition: Performs real-time palm feature extraction on the server side, compares it with the feature repository, and directly returns the recognition result (such as user ID).

New feature
Palm Database License Management supports two modes for capacity: one-time perpetual authorization and annual subscription authorization.
Device Management Platform
New feature
Device activation: Generates device activation codes, supports device activation within a LAN, and securely writes the service endpoint domain.

New feature
Device OTA: Supports online upgrades for applications and ROMs, allowing specific devices to be targeted and employing a batched upgrade policy.

New feature
Remote log retrieval: Supports remotely pulling device operation logs by device SN and date on the server side.

New feature
Remote command delivery: Supports issuing commands such as restart and factory reset to specified device SNs on the server side.

New feature
Device operation code: Provides a mobile device management tool (H5) that can generate temporary operation codes for device activation, log upload, volume adjustment, and screen brightness adjustment.
Business Management Platform
New feature
Payment Gateway: After PalmScan authentication is passed, the server requests a payment token from the payment channel and returns it to the device, which is then forwarded to the host computer.

New feature
Merchant Management: Supports managing merchants by customer entity dimension, providing a multi-level merchant management system and views categorized by region and level.

New feature
Device Attribute Management: Supports centralized configuration and delivery of device parameters on the server side, including: [Whether palm proximity wake-up is enabled], [Post-wake-up mode for palm detection], [Post-wake-up mode for host computer], [Output protocol], [Output content], [Device language], and supports applying different management modes by scenario.

New feature
Palm-scanning records: Displays transaction records of palm-scanning from all devices, including: palm-scanning time, device SN, and associated merchant.

New feature
User Management: View user palmprint registration information, including: registration time, registration method, user name, associated user ID.

New feature
Data Cockpit: Provides a visual dashboard of core data such as palm enrollment, device registration, and device activity.

New feature
Palm Enrollment: Identity verification api, Query enrollment results api, Query enrollment status api, Palmprint status change notification api, Query palm-scanning records api, Palm-scanning record notification api
Merchant Management: Create Merchant api, Obtain Merchant api, Edit Merchant api, Delete Merchant api
Device Management: Obtain Device api, Register Device api, Edit Device api
User Management: Create User api, Edit User api, Delete User api
Palm-scanning device (O2)
New feature
Palm-scan Payment: After palm scanning, either the device or the server requests a dynamic payment token from the payment channel and returns it to the host computer.
Palm-scan Authentication: After palm scanning, it directly outputs the user ID to the host computer, completing identity verification.
Palm-scan Access Control: After palm-scan authentication is passed, it outputs Wiegand signal or relay switch signal to control access control devices.


Reverse Palm Enrollment: Supports users in first placing their palm and then scanning a dynamic palm enrollment QR code to complete the registration process.


Device activation: Supports activation in a private deployment environment and securely writes the service domain to the secure chip.


Device Management: Supports remote OTA upgrades and server-issued device attribute management.


Multi-mode Management:
Registration Mode: New users can complete registration by palm scanning, while registered users will broadcast a welcome message upon palm scanning.
Recognition Mode: After palm scanning, it outputs the payment token or User ID to the host computer.
Hybrid Mode: Unregistered users can register on-site, while registered users complete identification and return the corresponding content (token or User ID) to the host computer based on the configuration.


