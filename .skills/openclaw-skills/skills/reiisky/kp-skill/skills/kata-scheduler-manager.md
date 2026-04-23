# Kata Scheduler Manager Skill

## Skill Metadata

```yaml
name: kata-scheduler-manager
version: 1.0.0
description: Manage scheduled messages and prevent scheduler leaks
author: Kata.ai Engineering
platforms: [kata.ai]
```

## When to Use This Skill

Use this skill when:

- **Creating timed messages** - Reminders, follow-ups, timeouts
- **Debugging scheduler issues** - "Bye" messages appearing unexpectedly
- **Cleaning up schedulers** - Ensure proper lifecycle management
- **Preventing scheduler leaks** - Audit scheduler create/cleanup pairs
- **Implementing timeouts** - User inactivity handling

## ⚠️ CRITICAL RULE

**Every `scheduleRun*` action MUST have a corresponding `scheduleOff*` cleanup action.**

Failure to clean up schedulers causes:
- Orphaned timers firing after flow ends
- Unexpected "bye" or timeout messages
- User confusion and poor experience
- Difficult-to-debug issues

## Core Capabilities

### 1. Create Schedulers

Set up timed messages for:
- User response timeouts (3-5 minutes)
- Payment reminders
- Follow-up messages
- Session timeouts

### 2. Clean Up Schedulers

Ensure schedulers are removed:
- Before creating new ones (prevent duplicates)
- In bye/end states (flow cleanup)
- On flow transitions (state changes)
- On error paths

### 3. Audit Schedulers

Scan codebase for:
- Orphaned schedulers (no cleanup)
- Duplicate scheduler IDs
- Missing bye state cleanup
- Scheduler intent handlers

## Technical Context

### Scheduler Action Structure

#### Create Scheduler (scheduleRun)

```yaml
actions:
    scheduleRunReminder:
        type: schedule
        options:
            id: uniqueSchedulerId        # Unique ID
            command: add                 # Create scheduler
            message:
                type: command
                content: reminderCommand # Command to trigger
            start: "2026-01-30 14:00:00" # Start time
            end: "2026-01-30 14:00:00"   # End time
            freqType: minute             # minute|hour|day
            freqInterval: 5              # Every 5 units
```

#### Delete Scheduler (scheduleOff)

```yaml
actions:
    scheduleOffReminder:
        type: schedule
        options:
            id: uniqueSchedulerId        # Same ID as scheduleRun
            command: remove              # Delete scheduler
```

### Scheduler Intent

Schedulers trigger command intents:

```yaml
intents:
    reminderIntent:
        type: command
        priority: 1
        condition: "content == 'reminderCommand'"
```

### Time Calculation Method

```javascript
function calculateReminderTime(msg, ctx, dat, opts, cfg) {
    var now = new Date(ctx.context.$now);

    // Add 3 minutes
    now.setMinutes(now.getMinutes() + 3);

    // Format as "YYYY-MM-DD HH:MM:SS"
    var dateISO = now.toISOString();
    var parts = dateISO.split('T');
    var timeParts = parts[1].split('.');

    ctx.context.reminderTime = parts[0] + ' ' + timeParts[0];

    return ctx;
}
```

## Usage Patterns

### Pattern 1: User Response Timeout

**User Request:** "Add 3-minute timeout if user doesn't respond"

**Complete Implementation:**

```yaml
intents:
    # Intent triggered by scheduler
    timeoutIntent:
        type: command
        priority: 1
        condition: "content == 'userTimeout'"

states:
    askQuestion:
        # Calculate time before actions
        enter: calculateTimeoutTime
        action:
            # CRITICAL: Turn off old scheduler first
            - name: scheduleOffTimeout

            # Create new scheduler
            - name: scheduleRunTimeout

            # Ask the question
            - name: questionText
        transitions:
            processAnswer:
                condition: "intent == 'answerIntent'"
                mapping:
                    data.userAnswer: "content"

            # Fallback - stay and wait
            askQuestion:
                fallback: true

    processAnswer:
        action:
            # IMPORTANT: Clean up scheduler when user responds
            - name: scheduleOffTimeout

            # Process the answer
            - name: validateAnswer
        transitions:
            # ...

    # Float state - catches timeout from ANY state
    timeout:
        priority: 100
        float:
            condition: "intent == 'timeoutIntent'"
        action:
            # Clean up scheduler
            - name: scheduleOffTimeout

            # Notify user
            - name: timeoutMessage
        end: true

actions:
    scheduleRunTimeout:
        type: schedule
        options:
            id: userResponseTimeout  # Unique ID
            command: add
            message:
                type: command
                content: userTimeout  # Matches intent condition
            start: $(context.timeoutTime)
            end: $(context.timeoutTime)
            freqType: minute
            freqInterval: 3

    scheduleOffTimeout:
        type: schedule
        options:
            id: userResponseTimeout  # Same ID
            command: remove

    timeoutMessage:
        type: text
        options:
            text: |
                No response received. Session timed out.
                Type 'Hi' to start again.

methods:
    calculateTimeoutTime(ctx): "
        var now = new Date(ctx.context.$now);
        now.setMinutes(now.getMinutes() + 3);

        var dateISO = now.toISOString();
        var parts = dateISO.split('T');
        var timeParts = parts[1].split('.');

        ctx.context.timeoutTime = parts[0] + ' ' + timeParts[0];

        return ctx;
    "
```

### Pattern 2: Multi-Stage Reminder

**User Request:** "Send reminders at 3min, 5min, and 10min if no payment"

**Approach:**

```yaml
intents:
    reminder1Intent:
        type: command
        condition: "content == 'paymentReminder1'"

    reminder2Intent:
        type: command
        condition: "content == 'paymentReminder2'"

    reminder3Intent:
        type: command
        condition: "content == 'paymentReminder3'"

states:
    waitingForPayment:
        enter: calculateReminderTimes
        action:
            # Clean up all reminders first
            - name: scheduleOffReminder1
            - name: scheduleOffReminder2
            - name: scheduleOffReminder3

            # Create all three reminders
            - name: scheduleRunReminder1
            - name: scheduleRunReminder2
            - name: scheduleRunReminder3

            # Inform user
            - name: waitingMessage
        transitions:
            paymentReceived:
                condition: "intent == 'paymentConfirmed'"

            waitingForPayment:
                fallback: true

    paymentReceived:
        action:
            # CRITICAL: Clean up all schedulers
            - name: scheduleOffReminder1
            - name: scheduleOffReminder2
            - name: scheduleOffReminder3

            # Confirm payment
            - name: paymentSuccessMessage
        end: true

    # Float states for each reminder
    reminder1:
        float:
            condition: "intent == 'reminder1Intent'"
        action:
            - name: reminder1Text

    reminder2:
        float:
            condition: "intent == 'reminder2Intent'"
        action:
            - name: reminder2Text

    reminder3:
        float:
            condition: "intent == 'reminder3Intent'"
        action:
            # Last reminder - clean up all and end
            - name: scheduleOffReminder1
            - name: scheduleOffReminder2
            - name: scheduleOffReminder3
            - name: finalReminderText
        end: true

actions:
    scheduleRunReminder1:
        type: schedule
        options:
            id: paymentReminder1
            command: add
            message:
                type: command
                content: paymentReminder1
            start: $(context.reminder1Time)
            end: $(context.reminder1Time)
            freqType: minute
            freqInterval: 3

    scheduleRunReminder2:
        type: schedule
        options:
            id: paymentReminder2
            command: add
            message:
                type: command
                content: paymentReminder2
            start: $(context.reminder2Time)
            end: $(context.reminder2Time)
            freqType: minute
            freqInterval: 5

    scheduleRunReminder3:
        type: schedule
        options:
            id: paymentReminder3
            command: add
            message:
                type: command
                content: paymentReminder3
            start: $(context.reminder3Time)
            end: $(context.reminder3Time)
            freqType: minute
            freqInterval: 10

    # Corresponding cleanup actions
    scheduleOffReminder1:
        type: schedule
        options:
            id: paymentReminder1
            command: remove

    scheduleOffReminder2:
        type: schedule
        options:
            id: paymentReminder2
            command: remove

    scheduleOffReminder3:
        type: schedule
        options:
            id: paymentReminder3
            command: remove

methods:
    calculateReminderTimes(ctx): "
        var now = new Date(ctx.context.$now);

        // Reminder 1: +3 minutes
        var time1 = new Date(now);
        time1.setMinutes(time1.getMinutes() + 3);
        var iso1 = time1.toISOString();
        var parts1 = iso1.split('T');
        var timeParts1 = parts1[1].split('.');
        ctx.context.reminder1Time = parts1[0] + ' ' + timeParts1[0];

        // Reminder 2: +5 minutes
        var time2 = new Date(now);
        time2.setMinutes(time2.getMinutes() + 5);
        var iso2 = time2.toISOString();
        var parts2 = iso2.split('T');
        var timeParts2 = parts2[1].split('.');
        ctx.context.reminder2Time = parts2[0] + ' ' + timeParts2[0];

        // Reminder 3: +10 minutes
        var time3 = new Date(now);
        time3.setMinutes(time3.getMinutes() + 10);
        var iso3 = time3.toISOString();
        var parts3 = iso3.split('T');
        var timeParts3 = parts3[1].split('.');
        ctx.context.reminder3Time = parts3[0] + ' ' + timeParts3[0];

        return ctx;
    "
```

### Pattern 3: Bye State Cleanup

**User Request:** "Ensure all schedulers are cleaned up when user exits"

**Approach:**

```yaml
states:
    # Global bye state (catches from anywhere)
    bye:
        priority: 100
        float:
            condition: "intent == 'byeIntent' || intent == 'timeoutIntent' || intent == 'cancelIntent'"
            mapping:
                # Clear sensitive data
                data.tempData: "'null'"
                data.sessionData: "'null'"
        action:
            # CRITICAL: Clean up ALL schedulers
            - name: scheduleOffTimeout
            - name: scheduleOffReminder
            - name: scheduleOffFollowup
            - name: scheduleOffNotification

            # Send goodbye message
            - name: byeMessage
        end: true

actions:
    byeMessage:
        type: text
        options:
            text: "Goodbye! Thank you for using our service. Type 'Hi' to start again."

    # All scheduler cleanup actions
    scheduleOffTimeout:
        type: schedule
        options:
            id: userResponseTimeout
            command: remove

    scheduleOffReminder:
        type: schedule
        options:
            id: paymentReminder
            command: remove

    scheduleOffFollowup:
        type: schedule
        options:
            id: followupMessage
            command: remove

    scheduleOffNotification:
        type: schedule
        options:
            id: notificationScheduler
            command: remove
```

## Debugging Scheduler Issues

### Issue: Unexpected "Bye" Message

**Symptoms:**
- User receives goodbye/timeout message unexpectedly
- Message appears while user is still active
- Happens after specific duration (3, 5, 10 minutes)

**Root Cause:**
Scheduler created but never cleaned up

**Debug Steps:**

1. **Find the scheduler intent:**
   ```bash
   grep -r "scheduleRunPart1\|scheduleRunTimeout\|scheduleRun" flows/
   ```

2. **Check if cleanup exists:**
   ```bash
   grep -r "scheduleOffPart1\|scheduleOffTimeout\|scheduleOff" flows/
   ```

3. **Verify bye state has cleanup:**
   ```yaml
   # In the flow file
   states:
       bye:
           float:
               condition: "intent == 'schedulerIntent'"
           action:
               # Must include scheduleOff!
               - name: scheduleOffXXX
   ```

4. **Check transition states:**
   ```yaml
   # States that transition away should clean up
   states:
       stateWithScheduler:
           action:
               - name: scheduleRunReminder
           transitions:
               nextState:
                   # Should clean up before moving
                   mapping:
                       # ...

       nextState:
           action:
               - name: scheduleOffReminder  # Clean up here
   ```

**Fix Pattern:**

```yaml
# BEFORE (Broken)
states:
    askQuestion:
        action:
            - name: scheduleRunTimeout  # Created
            - name: questionText
        transitions:
            answered:
                # ... no cleanup!

    bye:
        float:
            condition: "intent == 'byeIntent'"
        action:
            - name: byeText
            # Missing scheduleOffTimeout!
        end: true

# AFTER (Fixed)
states:
    askQuestion:
        action:
            - name: scheduleOffTimeout  # Clean old
            - name: scheduleRunTimeout  # Create new
            - name: questionText
        transitions:
            answered:
                # Will clean up in next state

    answered:
        action:
            - name: scheduleOffTimeout  # Clean up!
            - name: processAnswer
        transitions:
            # ...

    bye:
        float:
            condition: "intent == 'timeoutIntent' || intent == 'byeIntent'"
        action:
            - name: scheduleOffTimeout  # Clean up!
            - name: byeText
        end: true
```

### Issue: Scheduler Fires in Wrong Flow

**Symptoms:**
- Scheduler triggers after transitioning to different flow
- Intent not defined in new flow

**Root Cause:**
Scheduler not cleaned up before flow transition

**Fix:**

```yaml
# In source flow
states:
    transitionToOtherFlow:
        action:
            # CRITICAL: Clean up before transitioning
            - name: scheduleOffThisFlowScheduler

            # Transition command
            - name: goToOtherFlow
        end: true
```

## Scheduler Audit Checklist

Use this to audit your flows:

### 1. Find All Schedulers

```bash
# Find all scheduleRun actions
grep -n "scheduleRun" flows/*.yml

# Output example:
# flows/payment.yml:123:    - name: scheduleRunReminder
# flows/support.yml:456:    - name: scheduleRunTimeout
```

### 2. Check Each Has Cleanup

For each `scheduleRun*` found:

- [ ] Is there a corresponding `scheduleOff*` action defined?
- [ ] Is `scheduleOff*` called before creating new scheduler?
- [ ] Is `scheduleOff*` called in bye state?
- [ ] Is `scheduleOff*` called when user responds?
- [ ] Is `scheduleOff*` called before flow transitions?

### 3. Check Intent Handlers

For each scheduler:

- [ ] Is there an intent with matching `condition: "content == 'schedulerCommand'"`?
- [ ] Does the intent have proper priority?
- [ ] Is there a state that handles this intent (float or transition)?

### 4. Verify Bye States

Every flow with schedulers needs:

- [ ] Bye state exists
- [ ] Bye state is float (can trigger from anywhere)
- [ ] Bye state has ALL `scheduleOff*` actions
- [ ] Bye state has `end: true`

## Best Practices

### DO ✅

1. **Always clean up before creating**
   ```yaml
   action:
       - name: scheduleOffReminder  # Off first
       - name: scheduleRunReminder  # Then create
   ```

2. **Use descriptive scheduler IDs**
   ```yaml
   # Good
   id: userResponseTimeout3Min
   id: paymentReminderFirst
   id: followupMessage24h

   # Bad
   id: reminder1
   id: sched
   id: temp
   ```

3. **Document scheduler purpose**
   ```yaml
   actions:
       scheduleRunPaymentReminder:
           # Reminds user to complete payment after 5 minutes
           type: schedule
           options:
               id: paymentReminder5Min
               # ...
   ```

4. **Centralize cleanup in bye state**
   ```yaml
   states:
       bye:
           action:
               # Clean up ALL schedulers in one place
               - name: scheduleOffTimeout
               - name: scheduleOffReminder
               - name: scheduleOffFollowup
   ```

5. **Test scheduler timing**
   - Verify schedulers fire at correct time
   - Test cleanup on normal flow
   - Test cleanup on error flow
   - Test cleanup on flow transition

### DON'T ❌

1. **Create scheduler without cleanup**
   ```yaml
   # BAD - No cleanup!
   action:
       - name: scheduleRunReminder
   ```

2. **Reuse scheduler IDs across flows**
   ```yaml
   # BAD - ID conflict!
   # flow1.yml
   id: reminder

   # flow2.yml
   id: reminder  # Same ID!
   ```

3. **Forget float condition for bye**
   ```yaml
   # BAD - Not a float, can't interrupt
   states:
       bye:
           action:
               - name: byeText
           end: true

   # GOOD - Float can trigger from anywhere
   states:
       bye:
           float:
               condition: "intent == 'byeIntent'"
           action:
               - name: scheduleOffAll
               - name: byeText
           end: true
   ```

4. **Skip bye state cleanup**
   ```yaml
   # BAD
   states:
       bye:
           action:
               - name: byeText
           # Missing scheduler cleanup!
           end: true

   # GOOD
   states:
       bye:
           action:
               - name: scheduleOffAll
               - name: byeText
           end: true
   ```

## Integration with Other Skills

### With kata-flow-builder

Schedulers are integrated into flow states:

```yaml
states:
    waitForUser:
        enter: calculateTimeoutTime  # kata-method-writer
        action:
            - name: scheduleRunTimeout  # kata-scheduler-manager
            - name: askQuestion
        transitions:
            # ...
```

### With kata-debugger

Debug scheduler issues:
```bash
# Find orphaned schedulers
grep -A5 "scheduleRun" flows/*.yml | grep -v "scheduleOff"

# Check bye state cleanup
grep -A10 "bye:" flows/*.yml | grep "scheduleOff"
```

## Quick Reference

### Scheduler Lifecycle

```
1. Calculate time (enter method)
2. Clean up old (scheduleOff)
3. Create new (scheduleRun)
4. User responds OR timeout
5. Clean up (scheduleOff)
6. End or transition
```

### Time Calculation Template

```javascript
function calculateSchedulerTime(msg, ctx, dat, opts, cfg) {
    var now = new Date(ctx.context.$now);
    now.setMinutes(now.getMinutes() + 5);  // +5 minutes

    var dateISO = now.toISOString();
    var parts = dateISO.split('T');
    var timeParts = parts[1].split('.');

    ctx.context.schedulerTime = parts[0] + ' ' + timeParts[0];
    return ctx;
}
```

### Scheduler Pair Template

```yaml
# Create
actions:
    scheduleRunName:
        type: schedule
        options:
            id: uniqueSchedulerId
            command: add
            message:
                type: command
                content: schedulerCommand
            start: $(context.schedulerTime)
            end: $(context.schedulerTime)
            freqType: minute
            freqInterval: 5

# Cleanup
    scheduleOffName:
        type: schedule
        options:
            id: uniqueSchedulerId  # SAME ID
            command: remove
```

---

**End of Kata Scheduler Manager Skill**

*For complete scheduler reference, see KATA_PLATFORM_GUIDE.md*
