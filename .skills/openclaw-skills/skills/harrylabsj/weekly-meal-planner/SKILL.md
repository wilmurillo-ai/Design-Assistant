---
name: meal-planner
description: Weekly meal planner - input people count, budget, taste preference → output 7-day menu with breakfast/lunch/dinner and shopping list
---

# Meal Planner

Weekly meal planning assistant for families.

## Input
- Number of people
- Daily budget (per person or total)
- Taste preference (light/spicy/sweet/balanced)

## Output
- 7-day menu (breakfast/lunch/dinner)
- Shopping list with estimated prices
- Budget summary

## Constraints
- ❌ No detailed recipe steps
- ❌ No food delivery recommendations
- ❌ No allergy detection

## Usage
```bash
python3 scripts/meal-planner.py --people 3 --budget 50 --taste light
```
