---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 30450220228ecd9f9c798523d5929f5d95147efa9bf3982053785d1009c285cea7cceca8022100adc9344d57e7a07dd6d12b8f918fb8bea8de18c8a3828596d7aa5d4c56338f70
    ReservedCode2: 3045022100f0d944ca32b54a4043a45841fde72690b31d19cd2f6976b04fdb83e8d53b1ba802200d2eeecfb52a0afdf5df638c777856e5450b88862d63dde1b4d860d2a3d8d3c0
---

# CCFI Data Skill

China Export Container Freight Index (CCFI) data lookup.

## Features

- Query CCFI historical data
- Get latest CCFI index
- View statistics (high/low/average)

## Usage

### Query latest data
```
CCFI latest
```

### Query historical data
```
CCFI 2025
CCFI January 2024
```

### Query statistics
```
CCFI stats
```

### Query date range
```
CCFI 2025-01-01 to 2025-12-31
```

## Data Source

- Ministry of Transport of China
- Tencent Cloud Database

## API Endpoints

- `http://106.54.203.43/ccfi` - Historical data
- `http://106.54.203.43/ccfi/latest` - Latest data
- `http://106.54.203.43/ccfi/stats` - Statistics
