#!/usr/bin/env python3
"""
Tests for Cross-border Tax Compliance Navigator
"""

import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from handler import handle

def test_json_output():
    """Test that handler returns valid JSON."""
    result = handle("test input for tax compliance")
    
    # Parse JSON
    parsed = json.loads(result)
    
    # Check required fields
    assert "skill" in parsed, "Missing skill field"
    assert parsed["skill"] == "cb-tax-compliance-navigator", f"Wrong skill identifier: {parsed['skill']}"
    assert "input_analysis" in parsed, "Missing input_analysis field"
    assert "disclaimer" in parsed, "Missing disclaimer field"
    assert "tax_obligation_mapping" in parsed, "Missing tax_obligation_mapping field"
    assert "compliance_implementation_plan" in parsed, "Missing compliance_implementation_plan field"
    assert "risk_assessment" in parsed, "Missing risk_assessment field"
    
    print("✓ JSON test passed")
    return True

def test_disclaimer():
    """Test that disclaimer is present and appropriate."""
    result = handle("test")
    parsed = json.loads(result)
    
    disclaimer = parsed.get("disclaimer", "")
    assert disclaimer, "Disclaimer is empty"
    assert "descriptive" in disclaimer.lower(), "Disclaimer should mention descriptive nature"
    
    print("✓ Disclaimer test passed")
    return True

def test_input_differentiation():
    """Test that different inputs produce different outputs."""
    result1 = handle("VAT compliance for Germany")
    result2 = handle("GST registration for Australia")
    
    parsed1 = json.loads(result1)
    parsed2 = json.loads(result2)
    
    # They should not be identical
    assert json.dumps(parsed1, sort_keys=True) != json.dumps(parsed2, sort_keys=True), "Different inputs should produce different outputs"
    
    print("✓ Input differentiation test passed")
    return True

def test_jurisdiction_specific():
    """Test jurisdiction-specific functionality."""
    result = handle("tax compliance for Germany")
    parsed = json.loads(result)
    
    # Check for jurisdiction-specific fields
    tax_mapping = parsed.get("tax_obligation_mapping", {})
    assert "germany" in tax_mapping, "Missing Germany tax obligations"
    
    print("✓ Jurisdiction-specific test passed")
    return True

def test_differentiation_evidence():
    """Test that differentiation evidence is provided."""
    result = handle("tax compliance test")
    parsed = json.loads(result)
    
    # Check for differentiation evidence
    assert "differentiation_evidence" in parsed, "Missing differentiation_evidence field"
    evidence = parsed["differentiation_evidence"]
    
    # Should have some evidence fields
    assert len(evidence) > 0, "Differentiation evidence should not be empty"
    
    print("✓ Differentiation evidence test passed")
    return True

def run_all_tests():
    """Run all tests."""
    print("\\nRunning tests for cb-tax-compliance-navigator...")
    print("-" * 40)
    
    tests = [
        test_json_output,
        test_disclaimer,
        test_input_differentiation,
        test_jurisdiction_specific,
        test_differentiation_evidence
    ]
    
    passed = 0
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed: {str(e)}")
    
    print(f"\\n{passed}/{len(tests)} tests passed")
    return passed == len(tests)

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
