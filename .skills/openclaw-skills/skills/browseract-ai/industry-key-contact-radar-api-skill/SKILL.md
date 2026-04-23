---
name: industry-key-contact-radar-api-skill
description: "This skill helps users discover key contacts across industries, roles, and social platforms via the BrowserAct API. Agent should proactively apply this skill when users express needs like finding public profiles for founders or CEOs, discovering key decision-makers in a specific industry, extracting contact details for lead generation, searching for growth leaders on LinkedIn or Facebook, gathering professional networking profiles, retrieving URLs and names of industry leaders, finding marketing managers in a specific field, conducting competitive analysis by identifying key personnel, sourcing talent acquisition targets across platforms, or compiling a list of target roles on specific social sites."
metadata: {"openclaw":{"emoji":"🌐","requires":{"bins":["python"],"env":["BROWSERACT_API_KEY"]}}}
---

# Industry Key Contact Radar

## 📖 Brief
This skill provides a centralized contact discovery service using BrowserAct's Industry Key Contact Radar API template. It extracts structured contact details directly from search results across various platforms, including profile URLs, names, introductions, and company associations. Simply input an industry, date limit, target site, and job title to receive clean, actionable contact data.

## ✨ Features
1. **No hallucinations, ensuring stable and accurate data extraction**: Pre-set workflows avoid AI generative hallucinations, ensuring stable and precise data extraction.
2. **No CAPTCHA issues**: No need to handle reCAPTCHA or other verification challenges.
3. **No IP restrictions or geo-blocking**: No need to handle regional IP restrictions or geofencing.
4. **Faster execution**: Tasks execute faster compared to pure AI-driven browser automation solutions.
5. **Extremely high cost-efficiency**: Significantly lowers data acquisition costs compared to high-token-consuming AI solutions.

## 🔑 API Key Guide
Before running, check the `BROWSERACT_API_KEY` environment variable. If not set, do not take other measures; ask and wait for the user to provide it.
**Agent must inform the user**:
> "Since you haven't configured the BrowserAct API Key yet, please go to the [BrowserAct Console](https://www.browseract.com/reception/integrations) to get your Key."

## 🛠️ Input Parameters
Agent should flexibly configure the following parameters based on user needs:

1. **industry (Industry)**
   - **Type**: `string`
   - **Description**: The industry or field to search for contacts.
   - **Example**: `Browser automation`, `E-commerce`, `Healthcare`
   - **Default**: `Browser automation`

2. **Datelimit (Max Items)**
   - **Type**: `number`
   - **Description**: Maximum number of records to extract. For the first run, the default value is recommended.
   - **Example**: `10`
   - **Default**: `10`

3. **site (Target Site)**
   - **Type**: `string`
   - **Description**: The social platform or website to search on.
   - **Example**: `facebook.com`, `linkedin.com`, `github.com`
   - **Default**: `facebook.com`

4. **Job_Title (Job Title)**
   - **Type**: `string`
   - **Description**: The specific role or job title of the target contact.
   - **Example**: `founder`, `CEO`, `marketing manager`
   - **Default**: `founder`

## 🚀 Invocation Method
Agent should use the following independent script to achieve "one-line command result":

```bash
# Example
python -u ./scripts/industry_key_contact_radar_api.py "Browser automation" 10 "facebook.com" "founder"
```

### ⏳ Running Status Monitoring
Since this task involves automated browser operations, it may take some time (several minutes). The script will **continuously output status logs with timestamps** (e.g., `[14:30:05] Task Status: running`).
**Agent guidelines**:
- While waiting for the script result, keep monitoring the terminal output.
- As long as the terminal is outputting new status logs, the task is running normally; do not mistake it for a deadlock or unresponsiveness.
- Only if the status remains unchanged for a long time or the script stops outputting without returning a result should you consider triggering the retry mechanism.

## 📊 Data Output
After successful execution, the script parses and prints results directly from the API response. Results include:
- `url`: The URL link to the contact's public profile
- `name`: The name of the contact or profile title
- `Introduction`: A brief introduction or bio description of the contact
- `Company`: The company or organization associated with the contact

## ⚠️ Error Handling & Retry
If an error occurs during script execution (e.g., network fluctuations or task failure), the Agent should follow this logic:

1. **Check Output Content**:
   - If the output **contains** `"Invalid authorization"`, it means the API Key is invalid or expired. **Do not retry**; guide the user to re-check and provide the correct API Key.
   - If the output **contains** `"concurrent"` or `"too many running tasks"` or similar concurrency limit messages, it means the current subscription plan's concurrent task limit has been reached. **Do not retry**; guide the user to upgrade their plan.
     **Agent must inform the user**:
     > "The current task cannot be executed because your BrowserAct account has reached the limit of concurrent tasks. Please go to the [BrowserAct Plan Upgrade Page](https://www.browseract.com/reception/recharge) to upgrade your subscription plan and enjoy more concurrent task benefits."
   - If the output **does not contain the above error keywords** but the task failed (e.g., output starts with `Error:` or returns empty results), the Agent should **automatically try to re-execute the script once**.

2. **Retry Limit**:
   - Automatic retry is limited to **one time**. If the second attempt fails, stop retrying and report the specific error information to the user.

## 🌟 Typical Use Cases
1. **Lead Generation**: Finding public profiles for founders and CEOs in target industries.
2. **Talent Acquisition**: Sourcing growth leaders and key roles for recruiting.
3. **Competitive Analysis**: Identifying key personnel in competing organizations.
4. **Professional Networking**: Gathering profiles for industry connections.
5. **Market Intelligence**: Collecting URLs and names of industry leaders.
6. **Cross-Platform Discovery**: Searching target profiles on specific sites like LinkedIn or GitHub.
7. **B2B Outreach**: Finding decision-makers and extracting contact details.
8. **Brand Marketing**: Locating marketing managers in a specific field.
9. **Sales Prospecting**: Building lists of specific job titles across industries.
10. **Targeted Job Title Search**: Compiling a list of target roles on specific social sites.