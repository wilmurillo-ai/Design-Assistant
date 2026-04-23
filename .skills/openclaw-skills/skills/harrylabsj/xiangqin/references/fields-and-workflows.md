# Fields and Workflows

## Core profile fields

Required fields for a minimally useful profile:

- nickname
- gender
- birthYear
- height
- location
- education
- occupation

Optional but recommended:

- income
- hometown
- hobbies
- values
- selfDescription
- ageRange
- locationPreference
- educationPreference
- otherRequirements

## Suggested workflow

1. Create or complete the user's own profile.
2. Check profile completeness.
3. If completeness is low, ask for missing fields before matching.
4. Run matching only after at least one other candidate profile exists.
5. When showing matches, explain that the score is rule-based.
6. If the user asks for first contact help, generate openers and topics.
7. If the user asks about meeting, provide date suggestions plus safety reminders.
8. If the user is already in contact, record progress and review history.

## Matching caveats

- Current matching logic is heuristic and local.
- It is not a recommendation engine trained on outcome data.
- It assumes a simplified binary-gender pairing model in the current implementation.
- Income comparison is coarse and may be unreliable if formats are inconsistent.
