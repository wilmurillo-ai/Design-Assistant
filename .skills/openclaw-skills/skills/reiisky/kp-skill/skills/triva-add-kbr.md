# 🚀 triva-add-kbr

**Use when:** Adding a new Keyword-Based Routing (KBR) shortcut to initiate a conversation with a specific product or campaign flow.

## ⚠️ Prerequisites (Mandatory Order)

Before wiring any logic, you MUST define the following foundations:

1.  **NLU Definition (`nlu.yml`)**: Define the keyword group (e.g., `shortCutRamadhanKeyword`).
2.  **Intent Definition (`nlu.yml` or flow):** Create the primary intent (e.g., `shortcutHappyRamadhanIntent`) and its float version (e.g., `shortcutHappyRamadhanIntentFloat`).
3.  **Destination State:** Ensure the target state in the destination flow (e.g., `menuProduct.yml`) exists or is created to handle the specific content delivery.

## Implementation Steps

0.  **Locate Destination Flow**: Use `grep_search` to identify which flow file (e.g., `menuProduct.yml`, `handover.yml`, `menuFaq.yml`, etc.) contains the target state for the shortcut. You must know exactly where the bot should jump.

1.  **Update `greeting.yml` - Intent Setup**:
    *   Add the new intent to the `initial` state transition condition.
    *   Add the new intent to the `callApiCust` state's `mapping.data` section.

2.  **Update `greeting.yml` - Flow Routing**:
    *   Add a transition in `callApiCust` to route the shortcut flag to the destination flow (e.g., `toFlowProduk`).

3.  **Update Destination Flow - Logic Wiring**:
    *   In the destination flow (e.g., `menuProduct.yml`), locate the `initial` state.
    *   Add a transition to the target API/content state (e.g., `callAPIContentHappyBulanan`).
    *   The condition must check for the shortcut flag (e.g., `data.shortcutHappyBulanan`).
    *   Ensure the shortcut flag is cleared (set to `null`) in the `mapping.data` to prevent re-triggering.

4.  **Handle Floating Shortcuts (Jump Logic)**:
    *   If the shortcut can trigger while in an active conversation, add a `float` state in `greeting.yml` that captures the `...Float` intent.
    *   The state should use `command: nextState` and transition to the target flow (e.g., `toFlowProduk` or `showCSRoam`) while mapping the shortcut flag to `true`.
    *   Example floating state name: `floatShortcut[Campaign]`.

## 💡 Keyword Combination Rules

When defining NLU keywords for a KBR, ensure the combinations are strictly related to the product/campaign. Avoid including unrelated terms from other campaigns. A robust KBR keyword set should include:
- **Full Phrase:** The complete target phrase (e.g., "mau happy bulanan").
- **Core Action + Subject:** (e.g., "mau bulanan").
- **Product Name:** (e.g., "happy bulanan").
- **Single Identifier:** (e.g., "bulanan").

## Best Practices

- **Validate Before Wire**: Always verify that the NLU keyword, intent, and destination state are defined before adding them to `greeting.yml`.
- **Atomic Mapping**: Ensure the shortcut flag (e.g., `shortcutHappyRamadhan: true`) is properly mapped in the `callApiCust` transition.
- **Floating Intent**: Always create an `...IntentFloat` version of your intent to allow users to trigger the shortcut from anywhere in the bot.

## Example

```yaml
# 1. NLU Definition
shortCutRamadhanKeyword:
    type: keyword
    options:
        keywords:
            all: ["Mau Happy Ramadhan"]

# 2. Add to greeting.yml (init transition)
# condition: ... || intent == "shortcutHappyRamadhanIntent"
# mapping: ... shortcutHappyRamadhan: 'intent == "shortcutHappyRamadhanIntent"'

# 3. Add to greeting.yml (callApiCust routing)
# toFlowProduk:
#     condition: '... || data.shortcutHappyRamadhan'
```
