---
skill: cb-customer-service-localizer
name: International Customer Service Localizer
type: descriptive
version: 1.0.0
description: Customer service adaptation for international audiences
author: Golden Bean (OpenClaw)
created: 2026-04-22
category: customer-service
language: en
tags: ["customer-service", "localization", "multilingual", "support", "international"]
outputs: json
requires_api: false
safety_boundary: Descriptive cross-border e-commerce planning only. No code execution, API calls, network requests, bookings, or real-time data. Does not provide professional advice. Verify information with official sources and qualified professionals.
---

# International Customer Service Localizer

## Overview

International Customer Service Localizer (Customer service adaptation for international audiences). This skill provides a structured framework for localizing customer service operations for international markets. It covers multilingual support strategies, cultural service adaptation, channel selection, and quality management for cross-border customer service.

The framework helps businesses deliver culturally appropriate customer experiences across different markets while maintaining operational efficiency and service quality standards.

## Trigger Keywords

- "international customer service"
- "multilingual support localization"
- "cross-border customer experience"
- "global customer service strategy"
- "cultural service adaptation"
- "international support channels"

## Workflow

1. **Input Analysis**: Parse user input to extract target markets, service channels, and business parameters
2. **Localization Framework**: Generate culture-specific service adaptation recommendations
3. **Multilingual Planning**: Develop language support strategy and resource planning
4. **Channel Optimization**: Design market-appropriate service channels
5. **Output Delivery**: Return comprehensive JSON with analysis and recommendations

## Output Modules

### Service Localization Framework
- Communication style adaptation by culture
- Etiquette and protocol considerations
- Response time expectations by market
- Escalation process cultural adaptation
- Service recovery approach by culture

### Multilingual Support Plan
- Language coverage strategy and prioritization
- Translation vs localization approach
- Native speaker requirements and hiring
- AI and automation for language support
- Quality assurance for multilingual support

### Cultural Service Adaptation
- Greeting and opening style by culture
- Formality level adjustment recommendations
- Problem-solving approach by cultural context
- Complaint handling cultural differences
- Appreciation and follow-up cultural norms

### Channel Optimization
- Preferred support channels by market
- Social media customer service platforms
- Self-service portal localization
- Phone support cultural considerations
- Chat and messaging platform preferences

## Safety & Limitations

### Safety Boundaries
- **No Professional Advice**: Provides informational frameworks only. Does not replace HR or customer service professionals.
- **No Real-Time Data**: Based on general frameworks, not current staffing or platform availability.
- **No Service Delivery**: No actual customer service or support capabilities.
- **No Code Execution**: Pure descriptive implementation. No shell commands or network requests.
- **Descriptive Only**: Provides planning frameworks and guidance only.

### Limitations
- Cultural generalizations may not apply to all customer segments
- Language availability varies by market and changes over time
- Staffing costs and availability differ significantly by market
- Technology platform capabilities vary by region
- Service quality standards differ across cultures

## Example Prompts

### Level 1: Basic Inquiry
"How to localize customer service for international markets?"

### Level 2: Specific Scenario
"Multilingual support strategy for Japanese and German customers"

### Level 3: Complex Planning
"Multi-market customer service localization for US, EU, and Asia with omnichannel support"

### Level 4: Detailed Case
"US e-commerce company setting up customer service in France, Germany, and Japan with 24/7 multilingual chat support"

## Acceptance Criteria

### Functional Requirements
- Returns valid JSON structure from handle() function
- Includes input_analysis field with parsed input information
- Contains proper disclaimer with safety boundaries
- Provides customer-service-specific localization framework
- Differentiated from other cross-border e-commerce skills

### Quality Requirements
- Clear and structured output
- Comprehensive framework coverage
- Actionable implementation guidance
- Proper safety boundaries enforced
- Input differentiation verified through tests

## Integration

### Complementary Skills
- Works with cb-cultural-marketing-framework for consistent cultural approach
- Integrates with cb-returns-management-system for returns communication
- Supports cb-market-entry-strategist for market-specific service planning

### Input/Output Flow
- Accepts natural language input via handle() function
- Returns structured JSON for system integration
- Can be chained with related skills for multi-faceted analysis

## Version History

### v1.0.0 (2026-04-22)
- Initial release
- Service localization framework
- Multilingual support planning
- Cultural service adaptation
- Channel optimization guidance
- Input parsing and parameter extraction
- JSON output with input_analysis and disclaimer
- Safety boundaries and limitations documentation
- Test coverage with 5 tests per skill

## Technical Details

### Handler Interface


### Dependencies
- None (pure Python standard library only)

### File Structure
- handler.py: Main handler implementation
- tests/test_handler.py: Unit tests (5 tests)
- SKILL.md: This documentation file
- skill.json: Skill metadata and configuration
- ACCEPTANCE.md: Acceptance criteria documentation
- .claw/identity.json: Identity and authorship information

### Test Coverage
- JSON output validation test
- Disclaimer presence and content test
- Input differentiation test
- Customer-service-specific functionality test
- Differentiation evidence test
