# RELEASE-CHECKLIST.md
*Required before ANY code, doc, or config change is pushed to production or published to ClawHub.*
*Created by Eli | March 24, 2026 (Board action item)*

---

## Pre-Release Checklist

Complete every item. Do not skip. Check the box and note any issues found.

### 1. Smoke Test (User Journey)
Walk through the full end-to-end path as a NEW user (not as the developer):

- [ ] **Install:** `pip install northstar` (or `clawhub install northstar`) -- does it succeed cleanly?
- [ ] **Setup:** `northstar setup` -- does it prompt correctly for API keys?
- [ ] **Run:** `northstar` or `northstar demo` -- does it produce expected output?
- [ ] **Activate:** `northstar activate [KEY]` -- does activation succeed with a clear success message?
- [ ] **License request flow:** Open a GitHub issue using the template -- does the form load correctly with the right fields?
- [ ] **Payment path:** Read the README Subscribe section. Is the Venmo handle `@Daveglaser-3`? Is the amount correct?

### 2. Doc Consistency Check
```bash
grep -rn "Venmo\|venmo" . --include="*.md" | grep -v ".git"
```
- [ ] All Venmo references show `@Daveglaser-3` (not `@DaveGlaser`, not `@Dave-Glaser-3`)
- [ ] All payment amounts are consistent with PAYMENT.md (Standard: $19, Pro: $49)

```bash
grep -rn "payment link\|a link\|send a link" . --include="*.md" | grep -v ".git"
```
- [ ] No templates promise "a payment link" -- the payment method is Venmo/PayPal, not a link

### 2a. PII and License Key Security Check (MANDATORY)
**Before every git push to the public repo:**

```bash
# Check for email addresses
grep -rn "@gmail\.com\|@yahoo\.com\|@icloud\.com\|@me\.com\|@hotmail\.com" . --include="*.md" | grep -v ".git"

# Check for license key patterns (NSP-xxxx or NSS-xxxx format)
grep -rn "NS[PS]-[A-Z0-9]\{4\}-[A-Z0-9]\{4\}-[A-Z0-9]\{4\}" . --include="*.md" | grep -v ".git"

# Check for any key-looking patterns
grep -rn "\"key\":\|License Key:\|license key\|activate " . --include="*.md" | grep -v ".git" | grep -v "REDACTED"
```

- [ ] **Zero email addresses** belonging to customers in any tracked file
- [ ] **Zero license keys** (NSP-xxxx or NSS-xxxx patterns) in any tracked file
- [ ] Any operational doc containing PII is either: (a) in `.gitignore`, or (b) never committed to the repo

**Rule:** If a file needs to contain a customer email, key, or payment receipt -- it must NOT be committed to the public repo. Keep it local or in a private channel only.

### 3. README Accuracy Check
- [ ] Every command in the README actually works when copy-pasted into a fresh terminal
- [ ] The `northstar activate` command format matches the actual activation code
- [ ] The Subscribe section matches PAYMENT.md exactly

### 4. Fresh Install Test
```bash
rm -f ~/.config/northstar.json ~/northstar-config.json
northstar  # should ask for setup, not crash
```
- [ ] Fresh install prompts for setup cleanly
- [ ] No hardcoded credentials or stale config leaks

### 5. Error Message Review
Run these and check the output message is clear to a non-technical user:
- [ ] `northstar activate INVALID-KEY` -- does the error make sense?
- [ ] `northstar` without any config -- does it guide the user?
- [ ] `northstar activate` with no arguments -- does it explain usage?

### 6. AI/Docs Single Source of Truth
Before shipping any doc update:
- [ ] Does the change introduce a NEW reference to payment info? If yes, does it come from PAYMENT.md?
- [ ] Is there any doc (template, email draft, README) that still contains a payment handle not matching PAYMENT.md?

### 7. Changelog Entry
- [ ] `CHANGELOG.md` has an entry for this version
- [ ] Entry includes: version, date, what changed, and "Tested by: [Eli/Steve]"

### 8. External AI Evaluation (for user-facing changes)
Before shipping changes to landing page, README, ClawHub listing, pricing, or onboarding:

- [ ] Open ChatGPT at https://chatgpt.com (logged in on glaser.dave@gmail.com)
- [ ] Verify model is **ChatGPT 5.4 with Extended Thinking enabled** (check model selector + thinking toggle)
- [ ] Paste all public URLs (GitHub repo, landing page, ClawHub listing)
- [ ] Ask for brutal honest evaluation: first impressions, value prop clarity, pricing reaction, trust signals, purchase friction, what stops buying, what accelerates buying
- [ ] Process feedback and act on findings before shipping

### 9. ClawHub Publish (if applicable)
- [ ] Run `clawhub publish` after all fixes are committed and pushed
- [ ] Verify the new version is live: `curl -s "https://api.clawhub.ai/api/v1/skills/northstar" | python3 -m json.tool | grep version`
- [ ] Check for security warnings: `curl -s "https://api.clawhub.ai/api/v1/skills/northstar" | python3 -m json.tool | grep verdict`

---

## Incident Response (When a Bug Is Reported)

1. **Acknowledge within 1 hour** -- reply to the GitHub issue, email, or thread
2. **Root cause analysis in daily log:**
   - What broke?
   - Why didn't tests catch it? (unit tests, smoke tests, doc checks)
   - What change prevents recurrence?
3. **Fix, test the fix with this checklist, deploy**
4. **Update this checklist** if the bug class wasn't covered

---

## Change History

| Date | Change | Author |
|------|--------|--------|
| March 24, 2026 | Created per board action item (Ryan Venmo incident) | Eli |
| March 24, 2026 | Added 2a: PII/license key security check (Issue #2 - key + email exposure) | Eli |
| March 24, 2026 | Added 8: External AI evaluation step (board feedback - ChatGPT eval) | Eli |
| March 24, 2026 | Renumbered: ClawHub Publish -> 9, Paywall Integrity -> 10 | Eli |

### 10. Paywall Integrity Check (MANDATORY for any tier/license change)
Verifies the paywall cannot be bypassed via local config editing.

```bash
cd product/northstar && python3 tests/test_northstar_pro.py 2>&1 | grep -E "PASS|FAIL|paywall|spoofing|bypass"
```

- [ ] All 42 tests pass (including the 9 paywall acceptance tests in `TestTierCheck`)
- [ ] Test `test_tier_spoofing_no_key_rejected` passes
- [ ] Test `test_tier_spoofing_wrong_token_rejected` passes
- [ ] Test `test_tier_spoofing_mismatched_key_rejected` passes

**Manual check:**
```bash
# Simulate the attack: set tier=pro, no key/token
echo '{"tier": "pro"}' > /tmp/test-spoof.json
python3 -c "
import sys; sys.path.insert(0,'scripts')
import northstar_pro as pro
config = {'tier': 'pro'}
print('FAIL - paywall bypassed!' if pro.is_pro(config) else 'PASS - spoof rejected')
"
```
- [ ] Output says `PASS - spoof rejected`
