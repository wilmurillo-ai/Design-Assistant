#!/usr/bin/env python3
"""
Web Research Pipeline
Automated research: search → fetch → synthesize → report

Usage: python3 research.py "<research question>"
"""

import sys
import json
from datetime import datetime

def parse_question(query):
    """Extract key topics and entities from research question."""
    # Simple keyword extraction for pipeline purposes
    topics = query.strip().split()
    return {
        "original": query,
        "topics": topics[:5],
        "date": datetime.now().strftime("%Y-%m-%d")
    }

def generate_queries(parsed):
    """Generate 3-5 search query variants."""
    base = " ".join(parsed["topics"][:3])
    return [
        f'"{base}"',
        f'{base} 2025 OR 2026',
        f'{parsed["topics"][0]} trends analysis',
        f'{parsed["topics"][-1]} market data',
    ]

def build_report(parsed, findings, sources):
    """Build a structured report from findings."""
    date = parsed["date"]
    report = f"""# Research Report: {parsed['topics'][0]}

**Date:** {date}
**Researcher:** Claw (OpenClaw Agent)
**Duration:** ~{len(findings)} min
**Sources:** {len(sources)} web searches, {len([f for f in findings if 'url' in f])} pages fetched

## Executive Summary

{chr(10).join([f'- {f["summary"]}' for f in findings[:5]])}

## Key Findings

"""
    for i, f in enumerate(findings, 1):
        report += f"""
### {i}. {f.get('title', f.get('summary', 'Finding {i}'))}

{f.get('details', 'No details available.')}
"""

    report += """
## Limitations

- Information may be outdated or incomplete
- Sources should be verified independently
- AI-synthesized content — factual claims require human review

---
**Sources:**
"""
    for i, s in enumerate(sources, 1):
        report += f"""
{i}. {s.get('title', 'Unknown source')} — {s.get('url', 'No URL')} (accessed {date})
"""
    return report

def main():
    if len(sys.argv) < 2:
        print("Usage: research.py '<research question>'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    parsed = parse_question(query)
    queries = generate_queries(parsed)

    print(f"Research question: {query}")
    print(f"Generated queries: {len(queries)}")
    print(f"Queries: {', '.join(queries)}")

    # Pipeline steps: web_search → web_fetch → synthesize → report
    # In actual use, the agent orchestrates these via tool calls
    # This script documents the pipeline structure
    print("\nPipeline:")
    print("  1. Execute web_search for each query variant")
    print("  2. Fetch content from top results (web_fetch)")
    print("  3. Synthesize findings using framework")
    print("  4. Generate report from template")
    print(f"  5. Save to workspace/research/web-research-{parsed['date']}-{parsed['topics'][0]}.md")

if __name__ == "__main__":
    main()
