---
name: city-council-promo-video
version: "1.0.0"
displayName: "City Council Promo Video — Create Municipal Government and City Council Public Communication and Community Outreach Videos"
description: >
  Your city just approved a $12 million park renovation, launched a new recycling program, and opened a senior services center — and the residents who would benefit most found out from a neighbor, not from the city. City Council Promo Video creates public communication and community outreach videos for municipal governments, city councils, and local agencies: explains new programs and services in plain language that residents actually understand, documents infrastructure projects and community investments that demonstrate the value of local government to taxpayers, and exports videos for city websites, NextDoor, local Facebook groups, and the public meeting screens where residents form their opinions about how well their city is being run.
metadata: {"openclaw": {"emoji": "🏛️", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# City Council Promo Video — Connect Government to the Community It Serves

## Use Cases

1. **Program and Service Announcements** — New permit processes, utility assistance programs, park hours, and public transit changes all need clear video communication. City Council Promo Video creates plain-language service announcement videos for city websites, social media, and the cable access channels that still reach older residents who don't use social media.

2. **Infrastructure Project Updates** — Road construction, utility upgrades, and public building renovations affect residents for months. Short project update videos showing progress, explaining disruptions, and communicating timelines reduce constituent complaints and build public support for necessary improvements.

3. **Budget and Policy Transparency** — City councils that communicate budget decisions through accessible video build more public trust than those that publish PDF reports. Create annual budget overview videos and policy explainer videos that make civic decision-making understandable to residents without a public administration background.

4. **Community Event and Meeting Promotion** — Town halls, public comment periods, community cleanups, and local elections all need promotional videos that reach residents where they are. City Council Promo Video creates event promotion videos for the city's social channels that increase civic participation.

## How It Works

Describe the program, project, or policy you need to communicate, and City Council Promo Video creates a clear, accessible public communication video ready for every channel your municipality uses to reach residents.

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"skill": "city-council-promo-video", "input": {"municipality": "City of Riverside", "topic": "new recycling program launch", "audience": "all residents", "channels": ["website", "facebook", "nextdoor"]}}'
```
