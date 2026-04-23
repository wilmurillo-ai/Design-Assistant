#!/usr/bin/env python3
"""
Cross-border Tax Compliance Navigator
"""

import json
import sys

def parse_input(user_input: str):
    """Parse user input."""
    input_lower = user_input.lower()
    
    parsed = {
        "original_input": user_input,
        "input_preview": user_input[:100],
        "word_count": len(user_input.split()),
    }
    
    # Extract regions
    if "germany" in input_lower:
        parsed["jurisdictions"] = ["germany"]
    if "france" in input_lower:
        parsed["jurisdictions"] = parsed.get("jurisdictions", []) + ["france"]
    if "uk" in input_lower or "britain" in input_lower:
        parsed["jurisdictions"] = parsed.get("jurisdictions", []) + ["uk"]
    if "australia" in input_lower:
        parsed["jurisdictions"] = parsed.get("jurisdictions", []) + ["australia"]
    
    # Extract tax type
    if "vat" in input_lower:
        parsed["tax_type"] = "vat"
    elif "gst" in input_lower:
        parsed["tax_type"] = "gst"
    
    return parsed

def generate_tax_obligations(parsed_input):
    """Generate tax obligations."""
    obligations = {}
    jurisdictions = parsed_input.get("jurisdictions", [])
    
    for jurisdiction in jurisdictions:
        if jurisdiction == "germany":
            obligations["germany"] = {
                "registration_threshold": "€22,000 annual sales",
                "filing_frequency": "Monthly/quarterly",
                "vat_rates": {"standard": "19%", "reduced": "7%"}
            }
        elif jurisdiction == "france":
            obligations["france"] = {
                "registration_threshold": "€35,000 for EU businesses",
                "filing_frequency": "Monthly",
                "vat_rates": {"standard": "20%", "reduced": ["5.5%", "10%"]}
            }
    
    return obligations

def generate_compliance_plan(parsed_input):
    """Generate compliance plan."""
    return {
        "phase_1_assessment": {
            "duration": "2-4 weeks",
            "activities": [
                "Determine registration requirements",
                "Assess sales volume against thresholds",
                "Identify product tax classifications"
            ]
        },
        "phase_2_registration": {
            "duration": "4-8 weeks",
            "activities": [
                "Prepare registration documents",
                "Submit applications",
                "Obtain tax identification numbers"
            ]
        }
    }

def generate_risk_assessment(parsed_input):
    """Generate risk assessment."""
    return {
        "high_risk_scenarios": ["Missing registration deadlines"],
        "medium_risk_scenarios": ["Incorrect tax rate application"],
        "low_risk_scenarios": ["Minor filing errors"],
        "mitigation_strategies": ["Use tax automation software"]
    }

def handle(user_input: str) -> str:
    """Standard OpenClaw handler interface."""
    parsed = parse_input(user_input)
    
    response = {
        "skill": "cb-tax-compliance-navigator",
        "name": "Cross-border Tax Compliance Navigator",
        "input_analysis": parsed,
        "tax_obligation_mapping": generate_tax_obligations(parsed),
        "compliance_implementation_plan": generate_compliance_plan(parsed),
        "risk_assessment": generate_risk_assessment(parsed),
        "differentiation_evidence": {
            "jurisdiction_count": len(parsed.get("jurisdictions", [])),
            "tax_type_specific": parsed.get("tax_type") is not None
        },
        "recommendations": [
            "Start compliance planning early",
            "Consult with local tax advisors",
            "Maintain proper documentation"
        ],
        "disclaimer": "Descriptive cross-border e-commerce planning only. No professional advice."
    }
    
    return json.dumps(response, indent=2)

if __name__ == "__main__":
    input_text = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    print(handle(input_text))
