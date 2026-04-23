# Web Research Skill

**Purpose:** Generate structured research reports with source citations from web searches and fetches.

**Usage:** `python3 scripts/research.py "<research question>"`

## When to Use

- Freelance web research projects (€25-100/report)
- Competitive analysis requests
- Market research summaries
- Technical topic deep-dives
- Fact-checking and verification
- Topic overviews for clients

## Workflow

1. **Parse question** — extract key topics, entities, and scope
2. **Generate queries** — create 3-5 search variants covering different angles
3. **Execute searches** — use web_search for each query variant
4. **Fetch results** — use web_fetch to extract content from top URLs
5. **Synthesize** — combine findings into structured report
6. **Cite sources** — include original URLs and dates
7. **Store** — save report to workspace/research/

## Report Format

All reports follow `references/report_template.md` structure:
- Executive summary (3-5 bullets)
- Key findings (numbered)
- Data points with sources
- Limitations and gaps
- Related questions for follow-up

## Quality Rules

- Cross-reference at least 2 sources per major claim
- Flag outdated information (>2 years old for fast-moving topics)
- Distinguish between opinion and verified data
- Include URL for every citation
- Note when sources conflict

## Output

Reports saved to: `workspace/research/web-research-YYYY-MM-DD-<topic>.md`

## Skill Dependencies

- web_search tool
- web_fetch tool
- write tool (for report generation)
- exec tool (for running the pipeline)
