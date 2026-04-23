---
skill: cb-tax-compliance-navigator
name: Cross-border Tax Compliance Navigator
type: descriptive
version: 1.0.0
description: International tax obligations and VAT/GST compliance framework
author: Golden Bean (OpenClaw)
created: 2026-04-22
category: tax
language: en
tags: ["tax", "compliance", "vat", "gst", "international", "ecommerce"]
outputs: json
requires_api: false
safety_boundary: Descriptive cross-border e-commerce planning only. No code execution, API calls, network requests, bookings, or real-time data. Does not provide professional advice. Verify information with official sources and qualified professionals.
---

# Cross-border Tax Compliance Navigator

## Overview

Cross-border Tax Compliance Navigator (International tax obligations and VAT/GST compliance framework). This skill provides a structured framework for planning and implementing cross-border tax compliance strategies in international e-commerce contexts. It is designed for businesses expanding into new markets and needing guidance on tax-related considerations.

The framework covers market assessment, regulatory compliance, implementation planning, and ongoing management. It focuses on practical, actionable guidance that businesses can adapt to their specific circumstances.

## Trigger Keywords

- "cross-border tax compliance"
- "international VAT/GST framework"
- "tax obligations for e-commerce"
- "multi-jurisdiction tax requirements"
- "VAT registration thresholds"
- "cross-border tax planning"

## Workflow

1. **Input Analysis**: Parse user input to extract target markets, business parameters, and specific tax requirements
2. **Tax Obligation Mapping**: Generate jurisdiction-specific tax obligations based on extracted parameters
3. **Compliance Planning**: Create a structured compliance implementation plan with phases and activities
4. **Risk Assessment**: Identify high, medium, and low-risk scenarios with mitigation strategies
5. **Output Delivery**: Return a comprehensive JSON response with analysis, recommendations, and disclaimers

## Output Modules

### Tax Obligation Mapping
- Jurisdiction-specific VAT/GST registration requirements and thresholds
- Tax rate structures including standard, reduced, and zero rates
- Filing frequency, deadlines, and electronic filing requirements
- Special rules including distance selling, one-stop-shop, and reverse charge
- Registration processes and responsible authorities

### Compliance Implementation Plan
- Phase 1 Assessment: Determine requirements per target market
- Phase 2 Registration: Prepare documentation and submit applications
- Phase 3 Systems: Implement tax calculation and collection systems
- Phase 4 Reporting: Establish filing processes and ongoing compliance

### Risk Assessment
- High-risk scenarios including audit probability and penalty structures
- Medium-risk scenarios including complexity and error likelihood
- Low-risk scenarios with mitigation strategies
- Jurisdiction-specific mitigation recommendations

### Safety & Compliance
- Professional disclaimers and limitations clearly stated
- Guidance on when to seek professional tax advice
- Information verification recommendations

## Safety & Limitations

### Safety Boundaries
- **No Professional Advice**: Provides informational frameworks only. Does not replace qualified tax professionals.
- **No Real-Time Data**: Based on general frameworks, not current regulations. Regulations change frequently.
- **No Transactions**: No payment processing, tax calculations, or financial transactions.
- **No Code Execution**: Pure descriptive implementation. No shell commands or network requests.
- **Descriptive Only**: Provides planning frameworks and guidance only.

### Limitations
- Tax regulations may become outdated and require verification
- Business-specific factors may alter applicable requirements
- Jurisdiction-specific nuances may not be fully captured
- Does not include tax treaty considerations
- Product classification nuances may affect applicable rates

## Example Prompts

### Level 1: Basic Inquiry
"What are my tax obligations for selling in Germany?"

### Level 2: Specific Scenario
"US LLC selling digital products to EU customers via own website"

### Level 3: Complex Planning
"Multi-market expansion to Germany, France, UK, Australia with mixed physical/digital goods"

### Level 4: Detailed Case
"US corporation selling physical goods to Germany and France with Euro 100k annual sales"

## Acceptance Criteria

### Functional Requirements
- Returns valid JSON structure from handle() function
- Includes input_analysis field with parsed input information
- Contains proper disclaimer with safety boundaries
- Provides skill-specific tax obligation mapping
- Differentiated from other cross-border e-commerce skills

### Quality Requirements
- Clear and structured output
- Comprehensive framework coverage
- Actionable implementation guidance
- Proper safety boundaries enforced
- Input differentiation verified through tests

## Integration

### Complementary Skills
- Works with cb-compliance-framework for broader compliance coverage
- Integrates with cb-market-entry-strategist for market-specific planning
- Supports cb-multi-currency-pricing for tax-inclusive pricing strategies

### Input/Output Flow
- Accepts natural language input via handle() function
- Returns structured JSON for system integration
- Can be chained with related skills for multi-faceted analysis

## Version History

### v1.0.0 (2026-04-22)
- Initial release
- Basic tax obligation mapping for key markets
- Compliance implementation framework with phases
- Risk assessment with jurisdiction-specific considerations
- Input parsing and parameter extraction
- JSON output with input_analysis and disclaimer
- Safety boundaries and limitations documentation
- Test coverage with 6 tests per skill

## Technical Details

### Handler Interface


### Dependencies
- None (pure Python standard library only)

### File Structure
- handler.py: Main handler implementation
- tests/test_handler.py: Unit tests (6 tests)
- SKILL.md: This documentation file
- skill.json: Skill metadata and configuration
- ACCEPTANCE.md: Acceptance criteria documentation
- .claw/identity.json: Identity and authorship information

### Test Coverage
- JSON output validation test
- Disclaimer presence and content test
- Input differentiation test
- Jurisdiction-specific functionality test
- Product category-specific test
- Differentiation evidence test
