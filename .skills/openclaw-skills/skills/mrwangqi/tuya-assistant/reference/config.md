# Tuya Smart Device Configuration Management (config.env)

This document explains how to manage Tuya smart device configuration through the config.env file. All four configurations are required - none can be missing, otherwise the system cannot run.


### config.env Configuration Template:
```
# Tuya Developer Platform Access ID
TUYA_ACCESS_ID=xxx
# Tuya Developer Platform Access Secret
TUYA_ACCESS_SECRET=xxx
# Tuya App Account UID
TUYA_UID=xxx
# Data center
TUYA_ENDPOINT=your data center Configuration
```

**Data center Configuration:**
- China: `https://openapi.tuyacn.com`
- US West: `https://openapi.tuyaus.com`
- US East: `https://openapi-ueaz.tuyaus.com`
- Central Europe: `https://openapi.tuyaeu.com`
- Western Europe: `https://openapi-weaz.tuyaeu.com`
- India: `https://openapi.tuyain.com`
- Singapore: `https://openapi-sg.iotbing.com`


**Note for TUYA_ENDPOINT**: Do not show the URL to the user. Simply ask the user to provide their data center region (e.g., China, US West, US East, Central Europe, Western Europe, India, Singapore). Then map the region to the corresponding URL and place it in TUYA_ENDPOINT.


### Configuration Scenarios

Configure config.env according to the scenario

| Scenario | Existing Config | User Provides New Value | Behavior |
|----------|---------------|----------------------|----------|
| Scenario 1 | ✅ Yes | ❌ No | Use existing configuration directly |
| Scenario 2 | ✅ Yes | ✅ Yes | Overwrite existing configuration with new value |
| Scenario 3 | ❌ No | ❌ No | **Prompt user that configuration must be provided, and provide https://developer.tuya.com/cn/docs/developer/apply-cloud-api-key?id=Kff30z8sv62ah documentation to guide user on how to apply** |
| Scenario 4 | ❌ No | ✅ Yes | Save new configuration |



