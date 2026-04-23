# Itinerary Output Template

This document defines the standard output format for trip itineraries.

## Trip Overview Block

```
## Trip Overview

| Item          | Details                              |
|---------------|--------------------------------------|
| Destinations  | {city1} -> {city2} -> ...            |
| Dates         | {start_date} to {end_date} ({N} days)|
| Travelers     | {description}                        |
| Pace          | {relaxed / moderate / intensive}     |
| Est. Budget   | {currency} {amount} per person       |
```

## Day-by-Day Block

Each day follows this structure:

```
### Day {N}: {City} - {Theme of the Day}

**Morning (08:00-12:00)**
- {Activity 1}: {brief description} ({duration})
- {Activity 2}: {brief description} ({duration})
- Tip: {practical advice}

**Lunch (12:00-13:30)**
- {Restaurant/area recommendation}: {what to try}

**Afternoon (13:30-17:30)**
- {Activity 3}: {brief description} ({duration})
- {Activity 4}: {brief description} ({duration})

**Dinner (17:30-19:00)**
- {Dining recommendation}: {what to try}

**Evening (19:00-21:30)**
- {Evening activity}: {brief description}

**Accommodation**: {area/type recommendation}

**Transit note**: {if applicable, inter-city travel details}
```

## Transit Day Template

For days primarily spent on inter-city travel:

```
### Day {N}: {Origin} -> {Destination} (Transit Day)

**Morning**
- Check out from hotel
- {Transit mode} to {destination} (depart {time}, arrive {time})

**Afternoon**
- Arrive and check in at {area}
- Explore the hotel neighborhood
- {One light activity near accommodation}

**Evening**
- {Dinner spot near hotel}
- Rest and prepare for tomorrow's itinerary
```

## First Day Template (Late Arrival)

```
### Day 1: Arrive in {City}

**Afternoon/Evening**
- Arrive at {airport/station}, transfer to hotel ({transit advice})
- Check in at {accommodation area}
- Explore the neighborhood on foot
- {Dinner recommendation}: {local specialty to start the trip}
- Early rest to adjust
```

## Last Day Template

```
### Day {N}: {City} - Departure

**Morning (until {checkout_time})**
- Hotel checkout, store luggage if needed
- {One nearby activity or last-minute shopping}
- {Brunch/lunch recommendation}

**Afternoon**
- Transfer to {airport/station} ({allow X hours before departure})
- Departure

**Reminder**: Keep boarding pass, passport, and essentials accessible.
```

## Budget Summary Block

```
## Budget Estimation (per person)

| Category        | Est. Cost ({currency}) | Notes                    |
|-----------------|------------------------|--------------------------|
| Flights/Train   | {amount}               | {route details}          |
| Accommodation   | {amount}               | {N} nights x {per night} |
| Local Transport  | {amount}              | Metro, taxi, etc.        |
| Meals           | {amount}               | {per day} x {N} days     |
| Activities      | {amount}               | Tickets, tours, etc.     |
| Miscellaneous   | {amount}               | Shopping, tips, SIM card |
| **Total**       | **{total}**            |                          |

*Prices are estimates based on {budget_level} level. 
Verify current rates before booking.*
```

## Checklist Block

```
## Pre-Trip Checklist

See [Travel Checklist](travel-checklist.md) for a complete preparation guide.
```

## Compact Table Format (for trips > 7 days)

Use this summary before day-by-day details:

```
## Itinerary At-a-Glance

| Day | Date       | City      | Highlights                    | Transport      |
|-----|------------|-----------|-------------------------------|----------------|
| 1   | {date}     | {city}    | Arrival, {activity}           | Flight         |
| 2   | {date}     | {city}    | {highlight1}, {highlight2}    | Metro          |
| ... | ...        | ...       | ...                           | ...            |
| N   | {date}     | {city}    | Departure                     | Flight         |
```
