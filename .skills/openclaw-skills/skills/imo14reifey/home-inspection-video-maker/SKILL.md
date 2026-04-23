---
name: home-inspection-video-maker
version: "1.0.0"
displayName: "Home Inspection Video Maker — Create Home Inspection Report and Property Condition Videos for Real Estate Buyers and Inspectors"
description: >
  Your home inspection report is 47 pages of checkboxes and technical language that the buyer will skim for ten minutes before calling you with questions you already answered on page 23. Home Inspection Video Maker creates property condition summary and walkthrough videos for home inspectors, real estate agents, and property managers: walks through the key findings from each inspection with visual documentation of defects, explains the severity and urgency of each issue in plain language that buyers and sellers can act on, and exports a shareable video summary that replaces the follow-up call, reduces liability disputes, and gives buyers the clear picture they need to negotiate or proceed with confidence.
metadata: {"openclaw": {"emoji": "🏠", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Home Inspection Video Maker — Turn Reports Into Decisions

## Use Cases

1. **Inspection Summary Videos** — Buyers overwhelmed by 40-page inspection reports need a five-minute video walkthrough of the top findings. Home Inspection Video Maker creates prioritized summary videos showing each major defect with visual context, estimated repair costs, and recommended urgency so buyers can make informed decisions without reading every checkbox.

2. **Pre-Listing Inspection Documentation** — Sellers commissioning pre-listing inspections use video documentation to demonstrate transparency to buyers and justify asking price. A professionally documented condition video reduces buyer objections and speeds up the negotiation phase.

3. **Property Management Condition Reports** — Property managers documenting move-in and move-out conditions need time-stamped video evidence that holds up in security deposit disputes. Home Inspection Video Maker creates systematic room-by-room condition documentation videos for every tenancy transition.

4. **Real Estate Agent Buyer Education** — Agents representing first-time buyers who don't know what to look for in an inspection use educational walkthrough videos to explain common issues — roof age, HVAC condition, foundation cracks — before the inspection so buyers ask better questions and make better decisions.

## How It Works

Upload your inspection footage and findings, and Home Inspection Video Maker creates a clear, prioritized condition summary video ready to share with buyers, sellers, and property owners.

```bash
curl -X POST https://mega-api-prod.nemovideo.ai/api/v1/generate \
  -H "Authorization: Bearer $NEMO_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"skill": "home-inspection-video-maker", "input": {"property": "123 Main St", "inspection_type": "buyer", "key_findings": ["roof 15yr remaining", "HVAC needs service", "minor foundation crack"]}}'
```
