## Quick Reference

| User Requirement | Command | Description |
| ---------------------------- | ---------------------------------------------------------------------------------- | ------------------------------------ |
| List family list | `python scripts/tuya-cli.py family_list` | View user's family and room information |
| Query family room list | `python scripts/tuya-cli.py family_rooms <home_id>` | View room list for specified family |
| Query family device list | `python scripts/tuya-cli.py family_devices <home_id>` | View device list for specified family |
| Query automation list | `python scripts/tuya-cli.py automations <home_id>` | View automation list for specified family |
| Enable automation | `python scripts/tuya-cli.py automation_on <home_id> <automation_id>` | Enable automation for specified family |
| Disable automation | `python scripts/tuya-cli.py automation_off <home_id> <automation_id>` | Disable automation for specified family |
| Delete automation | `python scripts/tuya-cli.py automation_del <home_id> <automation_id>` | Delete automation for specified family |
| Create automation | `python scripts/tuya-cli.py add_automation <home_id> --json '{"name":"Test",...}'` | Add automation to specified family via JSON string |
| Query city list | `python scripts/tuya-cli.py cities` | Query city information |
| Query weather conditions supported by automation scenarios | `python scripts/tuya-cli.py conditions_weather` | Query weather conditions |


## Provide home_id family id information

- When the user proposes scenario-related information, need to check if the user has provided a valid home_id
- If home_id is not provided, you can provide "List Family List" function to prompt the user to choose which home_id to use, and output all family names for the user to choose



## Workflow

Trigger mechanisms:

1. Device linkage to device
- When socket device switch is turned on, need to turn on desk lamp
- When socket device switch is turned off, need to turn off desk lamp

2. Timer linkage to device
- Automatically turn on socket at 19:00 every day
- Automatically turn on curtain every Tuesday

3. Weather linkage to device
- Open curtain when weather is sunny
- Close air purifier when air quality is excellent


### Create automation scenario

When creating automation, you need to analyze semantics first, what are conditions and what are actions, for example:
- When socket device switch is turned on, need to turn on desk lamp: socket switch turned on is the condition, turn on desk lamp is the action
- Automatically turn on socket at 19:00 every day: every day at 19:00 is the condition, turn on socket is the action
- Open curtain when weather is sunny: weather sunny is the condition, open curtain is the action


The following is the basic JSON format description for creating automation scenarios:

```json
{
  "background": "https://images.tuyacn.com/smart/rule/cover/bedroom.png",
  "match_type": 1,
  "name": "openclaw test automation",
  "conditions": [],
  "actions": []
}
```

Basic field explanation:

- background: Automation scenario background image, this value can be hardcoded to "https://images.tuyacn.com/smart/rule/cover/bedroom.png"
- name: Scenario name, can be automatically generated based on user's description, scenario name prefix needs to include "AI Automation Scenario", for example "AI Automation Scenario: Socket close automation"
- match_type: Match type (1 means trigger when any condition is met, 2 means trigger when all conditions are met), when user has multiple conditions, need to remind user whether to meet any condition or all conditions, when only 1 condition, can directly hardcode to 1.
- conditions and actions are explained separately below


conditions and actions can have multiple, but timer and weather can only appear in conditions


#### conditions conditions

Different types of conditions have different internal structures, mainly according to entity_type rules:
- 1: Device status condition (for example when a device's switch changes)
- 3: Weather condition (for example temperature, humidity, weather, PM2.5, air quality, wind speed, etc.)
- 6: Timer condition (for example what time every day, or what time every week, sunrise(Hangzhou), sunset(Hangzhou))


##### 1. Device status condition example:
```json
{
    "conditions":[
        {
            "display":{
                "code":"switch_1",
                "operator":"==",
                "value":true
            },
            "entity_id":"vdevo15725982542****",
            "entity_type":1,
            "order_num":1
        }
    ]
}
```
- entity_id: Device Id
- entity_type: Condition type, device status condition value is 1
- order_num: Condition order, can hardcode to 1
- display:
  - code: Device's dpCode, for example "socket switch"'s dpCode
  - operator: Condition judgment method, Boolean and Enum use "==", Integer uses ">", "==", "<"
  - value: Value of device's dpCode, for example "socket open"'s value "open"

If the user's condition is to turn on the device's switch, find the dpCode for the switch from the device's Current Status, and check what type dpValueType is, and set dpValue according to the type. To check which dpCode corresponds to the user's intent, you can use the following checking methods:
- Switches generally start with switch, the device may have many switches, such as switch_1, switch_2, etc., you can prompt the user to choose which one to turn on
- dpCode generally starts in English, you can indirectly understand which dpCode the user wants to operate based on the English description, then set this dpCode
- If the condition cannot find the corresponding dpCode, directly report an error to the user, the operation instruction cannot be found on this device, and list the device information for the user to check

##### 2. Weather condition example:

```json
{
  "conditions":[
        {
            "display":{
                "code":"temp",
                "operator":"==",
                "value":"20"
            },
            "entity_id":"10",
            "entity_type":3,
            "order_num":1
        }
    ]
}
```
- entity_type: Condition type, weather condition value is 3
- order_num: Condition order, can hardcode to 1
- entity_id: Value is the corresponding city's ID, need to get city ID first
- display:
  - code: Weather unit, for example temp is temperature
  - operator: Use ">", "==", "<", for example temp temperature == equals
  - value: Value corresponding to code, for example temp temperature == equals 20


The entity_id in weather conditions is the city ID, it changes dynamically, you need to first check if the user provided city information, if not provided, you need to prompt the user to provide city information.

Use Query City List to get all city IDs:
```bash
# Query city list
python scripts/tuya-cli.py cities
```
Then automatically match information in cities based on the city provided by the user to get the city ID


The code in display also changes dynamically, you need to first query which weather configurations are supported, you can use "Query weather conditions supported by automation scenarios" to query:
```bash
# Query weather conditions supported by automation scenarios
python scripts/tuya-cli.py conditions_weather

# Returned data format
【{
    "category": "windSpeed",
    "category_name": "${v1,{\"code\":\"WINDSPEED\"}}",
    "operators": "[\"<\",\"==\",\">\"]",
    "property": {
      "code": "windSpeed",
      "name": "${v1,{\"code\":\"WINDSPEED\"}}",
      "property": {
        "desc": "",
        "max": 62,
        "min": 0,
        "step": 1,
        "type": "value",
        "unit": "m/s"
      }
    }
  }]
```
- category is the supported weather condition, for example windSpeed is wind speed, which also corresponds to the code in display, if category is condition, then you need to deduce from property whether it is wind speed
- operators is the operators supported by weather, which also corresponds to the operators in display
- property
  - property
    - type: type has many types, for example value numeric type, enum enumeration type, when type is numeric type, need to check if user's input value is within min and max range, if exceeds range, need to prompt user to reset; when type is enum enumeration, need to check if user's input value is in range area, if not exists, need to prompt user whether to reset. Finally set user's settings to display's code

You need to identify if the user's weather operation is in the weather conditions, if it does not exist, you need to prompt the user that it does not exist.


##### 3. Timer condition example:
```json
{
  "conditions": [
    {
      "entity_type": 6,
      "entity_id": "timer",
      "display": {
        "date": "20260302",
        "loops": "1111111",
        "time": "19:00",
        "timezone_id": "Asia/Shanghai"
      },
      "order_num": 1
    }
  ]
}
```
- entity_type: Condition type, timer condition value is 6
- order_num: Condition order, can hardcode to 1
- entity_id: Fixed to "timer"
- display:
  - date: Trigger date, format is yyyyMMdd, for example 20191125
  - loops: 7-digit number consisting of 0 and 1. 0 means not execute, 1 means execute. The first digit is Sunday, sequentially representing Monday to Saturday. For example, 0011000 means execute every Tuesday and Wednesday
  - time: Trigger time, 24-hour format, example: 14:00
  - timezone_id: Timezone ID, example: Asia/Shanghai


#### actions actions

##### 1. Device status action example:
```json
{
  "actions": [
    {
      "action_executor": "dpIssue",
      "entity_id": "vdevo174972647219148",
      "executor_property": {
        "switch_led": false
      }
    }
  ]
}
```
- action_executor: Action execution category, device status corresponding value is dpIssue
- entity_id: Device status corresponding value is Device Id
- executor_property: Executed device property
  - switch_led: Device's dpCode, for example "socket switch"'s dpCode
  - false: Device's dpCode's dpValue value, for example "socket open"'s value "open"

If the user's action is to turn on the device's switch, find the dpCode for the switch from the device's Current Status, and check what type dpValueType is, and set dpValue according to the type. To check which dpCode corresponds to the user's intent, you can use the following checking methods:
- Switches generally start with switch, the device may have many switches, such as switch_1, switch_2, etc., you can prompt the user to choose which one to turn on
- dpCode generally starts in English, you can indirectly understand which dpCode the user wants to operate based on the English description, then set this dpCode
- If the condition cannot find the corresponding dpCode, directly report an error to the user, the operation instruction cannot be found on this device, and list the device information for the user to check

## Create automation examples

### Create automation scenario 1 (device control): When AAA device is turned on, turn off BBB device switch

1. Let user choose which family to create automation in, and let user provide family id <home_id>

```bash
python scripts/tuya-cli.py family_list

```

2. Query device list under the family through family id <home_id>

```bash
python scripts/tuya-cli.py family_devices <home_id>

```

3. Check if AAA and BBB devices are in the device list under this family (supports fuzzy matching), if not exists, need to prompt user that device does not exist under this family, and stop the following steps, you can also let user re-select devices under this family, if devices are all under this family, continue the following steps


4. Read device information:

```
For example AAA's device information:
     ID: vdevo169536153736551
     Product: Prism
     Category: dj
     Status: True desc: 🟢 Online
     IP: 124.90.34.114
     Timezone:
     Product ID: pnaa4egznw49zztx
     Product Name: Prism
     Current Status:
       • dpCode:switch_led  dpValue:True  dpValueType: bool  desc: ✅ ON
       • dpCode:work_mode  dpValue:colour  dpValueType: str  desc: colour
       • dpCode:bright_value_v2  dpValue:110  dpValueType: int  desc: 110
       • dpCode:temp_value_v2  dpValue:216  dpValueType: int  desc: 216
       • dpCode:colour_data_v2  dpValue:{"h":231,"s":1000,"v":1000}  dpValueType: str  desc: {"h":231,"s":1000,"v":1000}
       • dpCode:countdown_1  dpValue:0  dpValueType: int  desc: 0


For example BBB's device information:
     ID: vdevo174972647219148
     Product: SOMLE
     Category: dd
     Status: True desc: 🟢 Online
     IP: 115.236.167.98
     Timezone:
     Product ID: zxc16czjxtbksvon
     Product Name: SOMLE
     Current Status:
       • dpCode:switch_led  dpValue:True  dpValueType: bool  desc: ✅ ON
       • dpCode:work_mode  dpValue:white  dpValueType: str  desc: white
       • dpCode:bright_value  dpValue:99  dpValueType: int  desc: 99
       • dpCode:temp_value  dpValue:500  dpValueType: int  desc: 500
       • dpCode:colour_data  dpValue:{"h":0,"s":100,"v":100}  dpValueType: str  desc: {"h":0,"s":100,"v":100}
       • dpCode:countdown  dpValue:0  dpValueType: int  desc: 0


```

5. Identify conditions and actions

- "AAA device turned on" is condition
- "Turn off BBB device switch" is action

6. Generate corresponding JSON structure

```json
{
  "background": "https://images.tuyacn.com/smart/rule/cover/bedroom.png",
  "match_type": 1,
  "name": "AI Automation Scenario: AAA turned on will turn off BBB switch",
  "conditions": [
    {
      "display": {
        "code": "switch_led",
        "operator": "==",
        "value": true
      },
      "entity_id": "vdevo169536153736551",
      "entity_type": 1,
      "order_num": 1
    }
  ],
  "actions": [
    {
      "action_executor": "dpIssue",
      "entity_id": "vdevo174972647219148",
      "executor_property": {
        "switch_led": false
      }
    }
  ]
}

```

7. Create automation scenario

> python scripts/tuya-cli.py add_automation <home_id> --json '{"name":"Test",...}'

If the result returns involving "command or value not support", it means dpCode and dpValue values do not correspond, can expose to let user confirm, and provide new values to continue

### Create automation scenario 2 (weather): Open curtain when weather is sunny

1. Let user choose which family to create automation in, and let user provide family id <home_id>

```bash
python scripts/tuya-cli.py family_list

```

2. Query device list under the family through family id <home_id>

```bash
python scripts/tuya-cli.py family_devices <home_id>
```

3. Check if curtain device is in the device list under this family (supports fuzzy matching), if not exists, need to prompt user that device does not exist under this family, and stop the following steps, you can also let user re-select devices under this family, if devices are all under this family, continue the following steps

4. Read device information
```
For example curtain's device information:
     ID: vdevo169536153736551
     Product: Prism
     Category: dj
     Status: True desc: 🟢 Online
     IP: 124.90.34.114
     Timezone:
     Product ID: pnaa4egznw49zztx
     Product Name: Prism
     Current Status:
       • dpCode:switch_led  dpValue:True  dpValueType: bool  desc: ✅ ON
       • dpCode:work_mode  dpValue:colour  dpValueType: str  desc: colour
       • dpCode:bright_value_v2  dpValue:110  dpValueType: int  desc: 110
       • dpCode:temp_value_v2  dpValue:216  dpValueType: int  desc: 216
       • dpCode:colour_data_v2  dpValue:{"h":231,"s":1000,"v":1000}  dpValueType: str  desc: {"h":231,"s":1000,"v":1000}
       • dpCode:countdown_1  dpValue:0  dpValueType: int  desc: 0
```

5. Identify conditions and actions

- Weather is sunny is condition
- Open curtain is action


6. When conditions involve weather, need to confirm city ID and sunny
```bash
# 1. Extract city from current conversation, if not, need to let user provide city, for example Hangzhou
# 2. Query city list
python scripts/tuya-cli.py cities
# 3. Extract Hangzhou's city ID in cities, for example 793409534348627968
# 4. Check if sunny is in weather conditions supported by automation scenarios, for example sunny
python scripts/tuya-cli.py conditions_weather
```

7. Generate corresponding JSON structure
```json
{
  "background": "https://images.tuyacn.com/smart/rule/cover/bedroom.png",
  "match_type": 1,
  "name": "AI Automation Scenario: Weather sunny open curtain",
  "conditions":[
        {
            "display":{
                "code":"condition",
                "operator":"==",
                "value":"sunny"
            },
            "entity_id":"793409534348627968",
            "entity_type":3,
            "order_num":1
        }
    ],
  "actions": [
    {
      "action_executor": "dpIssue",
      "entity_id": "vdevo169536153736551",
      "executor_property": {
        "switch_led": true
      }
    }
  ]
}
```

8. Create automation scenario

> python scripts/tuya-cli.py add_automation <home_id> --json '{"name":"Test",...}'

If the result returns involving "command or value not support", it means dpCode and dpValue values do not correspond, can expose to let user confirm, and provide new values to continue

### Create automation scenario 3 (timer): Turn on light at 7pm every day

1. Let user choose which family to create automation in, and let user provide family id <home_id>

```bash
python scripts/tuya-cli.py family_list

```

2. Query device list under the family through family id <home_id>

```bash
python scripts/tuya-cli.py family_devices <home_id>

```

3. Check if light device is in the device list under this family (supports fuzzy matching), if not exists, need to prompt user that device does not exist under this family, and stop the following steps, you can also let user re-select devices under this family; if devices are all under this family, continue the following steps

4. Read device information
```
For example light's device information:
     ID: vdevo177227153866535
     Product: AIBAR lamp
     Category: cz
     Status: True desc: 🟢 Online
     IP: 211.90.237.3
     Timezone:
     Product ID: ry39ktok0wviuaj3
     Product Name: AIBAR lamp
     Current Status:
       • dpCode:switch_1  dpValue:True  dpValueType: bool  desc: ✅ ON
       • dpCode:countdown_1  dpValue:0  dpValueType: int  desc: 0
       • dpCode:relay_status  dpValue:power_off  dpValueType: str  desc: power_off
       • dpCode:light_mode  dpValue:relay  dpValueType: str  desc: relay
       • dpCode:child_lock  dpValue:False  dpValueType: bool  desc: ❌ OFF
```

5. Identify conditions and actions

- Every day at 7pm is condition
- Turn on light is action

6. When conditions involve time, analyze time
- date: Get current system time, such as 20260302
- loops: Value for every day is 1111111
- time: Need to convert to 24-hour format, value is 19:00
- timezone_id: Get based on current system timezone, for example "Asia/Shanghai"

7. Generate corresponding JSON structure
```json
{
  "background": "https://images.tuyacn.com/smart/rule/cover/bedroom.png",
  "match_type": 1,
  "name": "AI Automation Scenario: Turn on light at 7pm",
  "conditions": [
    {
      "entity_type": 6,
      "entity_id": "timer",
      "display": {
        "date": "20260302",
        "loops": "1111111",
        "time": "19:00",
        "timezone_id": "Asia/Shanghai"
      },
      "order_num": 1
    }
  ],
  "actions": [
    {
      "action_executor": "dpIssue",
      "entity_id": "vdevo177227153866535",
      "executor_property": {
        "switch_1": true
      }
    }
  ]
}
```

8. Create automation scenario

> python scripts/tuya-cli.py add_automation <home_id> --json '{"name":"Test",...}'

If the result returns involving "command or value not support", it means dpCode and dpValue values do not correspond, can expose to let user confirm, and provide new values to continue


## Error handling solution

When encountering errors such as param is illegal, please refer to developer documentation in time to correct the writing: https://developer.tuya.com/cn/docs/cloud/scene-and-automatic?id=K95zu0bsi8i8s#title-80-%E6%B7%BB%E5%8A%A0%E8%87%AA%E5%8A%A8%E5%8C%96
