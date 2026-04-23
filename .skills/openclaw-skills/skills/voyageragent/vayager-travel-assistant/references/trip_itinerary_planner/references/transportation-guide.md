# Transportation Guide

Framework for analyzing and recommending transportation between and within
destinations. Extracted from production travel planning systems.

## Inter-City Transportation Decision Matrix

### Distance-based recommendation

| Distance (km) | Primary Choice      | Secondary Choice     | Notes                              |
|----------------|---------------------|----------------------|------------------------------------|
| 0 - 100        | Driving / Taxi      | Regional bus/train   | Door-to-door most convenient       |
| 100 - 300      | High-speed rail     | Driving              | Rail often faster than driving     |
| 300 - 800      | High-speed rail     | Short-haul flight    | Rail: no airport overhead          |
| 800 - 1500     | Flight              | Overnight train      | Flight saves a full day            |
| 1500+          | Flight              | -                    | Only viable option                 |
| Cross-border   | Flight              | Intl rail (if avail) | Check visa transit requirements    |

### Time overhead per transport mode

| Mode              | Overhead (beyond travel time)      |
|-------------------|------------------------------------|
| Flight            | 2.5 - 3.5 hours (check-in, security, boarding, baggage) |
| High-speed rail   | 30 - 45 minutes (station arrival, boarding) |
| Long-distance bus  | 15 - 30 minutes                   |
| Driving (own car) | 0 minutes (but parking at destination) |
| Ferry             | 30 - 60 minutes (check-in, boarding) |

### Cost comparison (general tiers)

| Mode          | Cost Level | Best For                           |
|---------------|------------|------------------------------------|
| Bus           | Lowest     | Budget travel, short routes        |
| Train (regular)| Low-Medium | Medium distance, scenic routes     |
| High-speed rail| Medium    | 300-800 km, time-sensitive         |
| Budget airline | Medium    | 800+ km, booked early             |
| Full-service airline | High | Long-haul, comfort priority      |
| Private car/taxi| High     | Groups, door-to-door, flexibility |

## Intra-City Transportation

### Mode selection by scenario

| Scenario                        | Recommended Mode                  |
|---------------------------------|-----------------------------------|
| City with metro system          | Metro + walking (primary)         |
| Attractions < 2 km apart        | Walking                           |
| With young children or elderly  | Taxi / ride-hailing               |
| Rural area or outskirts         | Rental car or local tour          |
| Night activity / late return    | Taxi / ride-hailing               |
| Group of 3-4 people             | Taxi (often same cost as transit) |
| Budget solo traveler            | Public transit + walking          |

### Metro/subway tips by region

- **East Asia** (Tokyo, Seoul, Shanghai): Excellent coverage, IC cards
  available, English signage in most stations
- **Europe** (London, Paris, Berlin): Good coverage in center, zone-based
  pricing, multi-day passes available
- **Southeast Asia** (Bangkok, Singapore, KL): Limited coverage, supplement
  with taxi/ride-hailing
- **Americas** (NYC, Mexico City): Reliable but check safety by line/time

## Transit Scheduling Rules

### Optimal transit times for itinerary placement

| Transit Type    | Best Schedule Slot           | Reason                          |
|-----------------|------------------------------|---------------------------------|
| Morning flight   | Depart 07:00-09:00          | Arrive by lunch, half-day free  |
| Afternoon flight | Depart 14:00-16:00          | Morning free, arrive by dinner  |
| Evening flight   | Avoid if possible            | Wastes an evening, fatigue      |
| Red-eye flight   | For long-haul only           | Saves a hotel night + full day  |
| HSR morning      | Depart 08:00-10:00           | No airport overhead, arrive by lunch |
| HSR evening      | Depart after 17:00           | Full day at origin, arrive for dinner |

### Connection time buffers

| Connection Type             | Minimum Buffer  |
|-----------------------------|-----------------|
| Domestic flight to flight    | 90 minutes     |
| International flight to flight| 2.5 hours     |
| Train to train               | 30 minutes     |
| Flight to train/hotel        | 2 hours (incl. baggage + transfer) |
| Train to hotel               | 45 minutes     |

## Luggage Strategy

| Trip Pattern             | Luggage Advice                          |
|--------------------------|----------------------------------------|
| Single-city stay         | Any luggage size; store at hotel        |
| Multi-city, same hotel   | Day bag only for city switches          |
| Multi-city, hotel changes| Carry-on preferred; use luggage forwarding services |
| Road trip                | Trunk storage; no weight concerns       |
| Budget airline multi-leg | Carry-on only to avoid per-leg fees     |

## Regional Transport Highlights

### East Asia
- Japan: JR Pass for multi-city rail; Suica/Pasmo IC cards for local transit
- China: High-speed rail network excellent; book on 12306 or Trip.com
- South Korea: KTX for inter-city; T-money card for Seoul transit

### Europe
- Eurail Pass for multi-country rail travel
- Budget airlines (Ryanair, EasyJet) for cross-country flights
- Flixbus for budget inter-city buses

### Southeast Asia
- Grab (ride-hailing) widely available across the region
- AirAsia for budget intra-region flights
- Boats/ferries for island hopping (Thailand, Indonesia, Philippines)

### North America
- Driving/road trips are the norm outside major metros
- Amtrak for scenic but slow rail options
- Domestic budget airlines (Southwest, JetBlue) for inter-city

*Note: This guide provides framework-level recommendations. 
Specific routes, schedules, and prices should be verified with current sources.*
