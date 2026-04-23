## Quick Reference

| User Requirement | Command | Description |
|---------|------|------|
| List all devices | `python scripts/tuya-cli.py devices` | View user's device list (including detailed status) |
| Control device status | `python scripts/tuya-cli.py control <device_id> <dpCode> <dpValue>` | Control status of a device capability |
| Query status | `python scripts/tuya-cli.py status <device_id>` | Get device current status |
| Search device | `python scripts/tuya-cli.py find "name"` | Search device by name |



##

**Scenario 1: User wants to control a device's status**

```bash
# Step 1: Search device - try multiple keywords
python scripts/tuya-cli.py find "living room light"
# If not found, try:
python scripts/tuya-cli.py find "living room"
python scripts/tuya-cli.py find "light"

#  step2 Check device information status, in the following format, for device EGD1-1001-vdevo, Current Status is the device's status information
EGD1-1001-vdevo
     ID: vdevo173279908550810
     Product: EGD1-1001
     Category: ckmkzq
     Status: True desc: 🟢 Online
     IP: 172.28.18.129
     Timezone:
     Product ID: gcmwzdriibeeoc0o
     Product Name: xxxxx
     Current Status:
       • dpCode:switch_1  dpValue:False  dpValueType: bool  desc: ❌ OFF
       • dpCode:countdown_1  dpValue:0  dpValueType: int  desc: 0
       • dpCode:door_state_1  dpValue:unclosed_time  dpValueType: str  desc: unclosed_time

Device information description:
- EGD1-1001-vdevo is the device name
- ID: Device Id <device_id>
- Status: Whether the device is currently online
- Current Status:
    - dpCode is a capability description of the device, for example the device's switch, dpCode is switch_1
    - dpValue is the current status value of a device capability, for example the device's switch, value is False, which means the status is OFF
    - dpValueType is the type corresponding to the value of a capability, for example the device's switch corresponds to bool type, there are also int, str types
    - desc is the string description output of dpValue

# step3 Identify user control action

If the user wants to turn on the device's switch, find the dpCode for the switch from the device's Current Status, and check what type dpValueType is, and set dpValue according to the type.

To check which dpCode corresponds to the user's intent, you can use the following checking methods:
- Switches generally start with switch, for example for device "EGD1-1001-vdevo", the switch is switch_1, the device may have many switches, such as switch_1, switch_2, etc., you can prompt the user whether to turn them all on
- dpCode generally starts in English, you can indirectly understand which dpCode the user wants to operate based on the English description, then execute this dpCode
- If the control action cannot find the corresponding dpCode, directly report an error to the user, the operation instruction cannot be found on this device, and list the device information for the user to check


# step4 Control device

Execution template:
python scripts/tuya-cli.py control <device_id> <dpCode> <dpValue>

For example, to turn on the light of xx device (taking EGD1-1001-vdevo as an example), the switch's dpCode is switch_1, dpValueType is bool type, because it is turning on, the dpValue value is true, execute the following command to turn on:

Execution example:
python scripts/tuya-cli.py control vdevo173279908550810 switch_1 True

# step5 Control result check
- If a success message is returned, directly proceed to step5 to verify device status
- If a failure message is returned, check if it carries "command or value not support", this error message indicates that a non-existent dpCode or dpValue was given, you can adjust it yourself, or choose to let the user choose which dpCode to control

# Step6: Verify device status (REQUIRED)
python scripts/tuya-cli.py status <device_id>

```

**Scenario 2: User wants to view all device status**

```bash
# Step 1: Smart check environment variables
if [ -n "$TUYA_ACCESS_ID" ] && [ -n "$TUYA_ACCESS_SECRET" ] && [ -n "$TUYA_UID" ]; then
    echo "✓ Configuration ready, starting query..."
else
    echo "⚠️  Please configure environment variables first"
    exit 1
fi

# Step 2: List all devices
python scripts/tuya-cli.py devices
```

### Smart Search Strategy

When the user says "living room's light", the search keywords may have various forms:

```bash
# Strategy 1: Direct search
python scripts/tuya-cli.py find "living room light"

# Strategy 2: Remove "的"
python scripts/tuya-cli.py find "living room light" | sed 's/的//g'

# Strategy 3: Only use room name
python scripts/tuya-cli.py find "living room"

# Strategy 4: List all devices for user to choose
python scripts/tuya-cli.py devices
```

**Important**: If the search returns multiple results, please ask the user to confirm which one to select.

### Post-execution Verification (REQUIRED)

**After executing a control command, you must verify the device status:**

```bash
# Execute command
python scripts/tuya-cli.py control <device_id> <dpCode> <dpValue>

# Wait 1-2 seconds
sleep 2

# Verify status
python scripts/tuya-cli.py status <device_id>
```

**If verification fails:**
1. Check if the device is online
2. Confirm the device has been authorized to the cloud project
3. Try different DP codes
