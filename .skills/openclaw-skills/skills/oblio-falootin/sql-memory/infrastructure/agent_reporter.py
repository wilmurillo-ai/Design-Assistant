#!/usr/bin/env python3
"""
agent_reporter.py - Unified reporting framework for all agents

Each agent inherits from this to generate consistent weekly reports on:
- Items processed (count + type)
- Data stored (what, where, confidence)
- Errors encountered (type, severity, count)
- Enrichment metrics (new patterns, connections, etc.)
- Quality signals (confidence levels, deduplication, anomalies)
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


class AgentReport:
    """Base report class for all agents."""

    def __init__(self, agent_name: str, report_week: str = None):
        """
        Initialize report.
        
        Args:
            agent_name: Name of the agent (e.g., 'stamps', 'facs', 'nlp', 'security')
            report_week: ISO week (YYYY-W##) or None for current week
        """
        self.agent_name = agent_name
        self.report_week = report_week or self._get_iso_week()
        self.timestamp = datetime.now().isoformat()
        
        # Core report sections
        self.processed = {}  # What was processed
        self.stored = {}  # What was stored (where, samples)
        self.errors = []  # Errors encountered
        self.enrichment = {}  # What we learned / added
        self.metrics = {}  # Quality metrics
        self.forecasts = []  # Next week's expectations
        
        # Paths
        self.reports_dir = Path("/mnt/c/Library/Reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_iso_week(self) -> str:
        """Get current ISO week string (YYYY-W##)."""
        now = datetime.now()
        iso = now.isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"
    
    def add_processed(self, category: str, count: int, details: str = ""):
        """Record what was processed."""
        self.processed[category] = {
            "count": count,
            "details": details
        }
    
    def add_stored(self, location: str, item_count: int, samples: List[str] = None, confidence: float = 1.0):
        """Record what was stored."""
        self.stored[location] = {
            "count": item_count,
            "samples": samples or [],
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
    
    def add_error(self, error_type: str, severity: str, message: str, count: int = 1):
        """Log an error."""
        self.errors.append({
            "type": error_type,
            "severity": severity,  # low, medium, high, critical
            "message": message,
            "count": count,
            "timestamp": datetime.now().isoformat()
        })
    
    def add_enrichment(self, metric: str, value: Any, description: str = ""):
        """Record what we enriched / learned."""
        self.enrichment[metric] = {
            "value": value,
            "description": description
        }
    
    def add_metric(self, metric_name: str, value: float, unit: str = ""):
        """Add a quality metric."""
        self.metrics[metric_name] = {
            "value": value,
            "unit": unit
        }
    
    def add_forecast(self, forecast: str):
        """Add a forecast for next week."""
        self.forecasts.append(forecast)
    
    def generate(self) -> Dict:
        """Generate the final report dict."""
        return {
            "metadata": {
                "agent": self.agent_name,
                "week": self.report_week,
                "generated": self.timestamp
            },
            "processed": self.processed,
            "stored": self.stored,
            "errors": self.errors,
            "enrichment": self.enrichment,
            "metrics": self.metrics,
            "forecasts": self.forecasts
        }
    
    def save_json(self) -> str:
        """Save report as JSON."""
        report = self.generate()
        filename = f"{self.agent_name}_report_{self.report_week}.json"
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return str(filepath)
    
    def save_markdown(self) -> str:
        """Save report as human-readable Markdown."""
        report = self.generate()
        
        lines = [
            f"# {self.agent_name.upper()} Weekly Report",
            f"**Week:** {self.report_week}",
            f"**Generated:** {self.timestamp}",
            "",
            "---",
            ""
        ]
        
        # Processed
        if self.processed:
            lines.append("## 📥 Processed")
            for category, data in self.processed.items():
                lines.append(f"- **{category}**: {data['count']} items")
                if data['details']:
                    lines.append(f"  - {data['details']}")
            lines.append("")
        
        # Stored
        if self.stored:
            lines.append("## 💾 Stored")
            for location, data in self.stored.items():
                lines.append(f"- **{location}**: {data['count']} items (confidence: {data['confidence']:.2f})")
                if data['samples']:
                    lines.append(f"  - Samples: {', '.join(data['samples'][:3])}")
            lines.append("")
        
        # Enrichment
        if self.enrichment:
            lines.append("## ✨ Enrichment")
            for metric, data in self.enrichment.items():
                lines.append(f"- **{metric}**: {data['value']}")
                if data['description']:
                    lines.append(f"  - {data['description']}")
            lines.append("")
        
        # Metrics
        if self.metrics:
            lines.append("## 📊 Quality Metrics")
            for metric, data in self.metrics.items():
                unit_str = f" {data['unit']}" if data['unit'] else ""
                lines.append(f"- **{metric}**: {data['value']:.2f}{unit_str}")
            lines.append("")
        
        # Errors
        if self.errors:
            lines.append("## ⚠️ Errors")
            for error in self.errors:
                severity_emoji = {"low": "🟡", "medium": "🟠", "high": "🔴", "critical": "⛔"}
                emoji = severity_emoji.get(error['severity'], "❓")
                lines.append(f"- {emoji} **{error['type']}** ({error['count']}x): {error['message']}")
            lines.append("")
        
        # Forecasts
        if self.forecasts:
            lines.append("## 🔮 Next Week Forecast")
            for forecast in self.forecasts:
                lines.append(f"- {forecast}")
            lines.append("")
        
        filename = f"{self.agent_name}_report_{self.report_week}.md"
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w') as f:
            f.write("\n".join(lines))
        
        return str(filepath)
    
    def save_all(self) -> tuple:
        """Save both JSON and Markdown versions."""
        json_path = self.save_json()
        md_path = self.save_markdown()
        return json_path, md_path


class WeeklyReportAggregator:
    """Aggregates reports from all agents into a dashboard."""
    
    def __init__(self, week: str = None):
        self.week = week or self._get_iso_week()
        self.reports_dir = Path("/mnt/c/Library/Reports")
        self.reports_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_iso_week(self) -> str:
        now = datetime.now()
        iso = now.isocalendar()
        return f"{iso[0]}-W{iso[1]:02d}"
    
    def aggregate(self) -> Dict:
        """Load all reports from this week and aggregate."""
        pattern = f"*_report_{self.week}.json"
        report_files = list(self.reports_dir.glob(pattern))
        
        aggregated = {
            "week": self.week,
            "timestamp": datetime.now().isoformat(),
            "agents": {},
            "summary": {
                "total_processed": 0,
                "total_stored": 0,
                "total_errors": 0,
                "enrichment_count": 0
            }
        }
        
        for report_file in report_files:
            with open(report_file) as f:
                report = json.load(f)
            
            agent_name = report['metadata']['agent']
            aggregated['agents'][agent_name] = report
            
            # Update summary
            for data in report['processed'].values():
                aggregated['summary']['total_processed'] += data['count']
            for data in report['stored'].values():
                aggregated['summary']['total_stored'] += data['count']
            aggregated['summary']['total_errors'] += len(report['errors'])
            aggregated['summary']['enrichment_count'] += len(report['enrichment'])
        
        return aggregated
    
    def save_dashboard(self) -> str:
        """Save aggregated dashboard as Markdown."""
        agg = self.aggregate()
        
        lines = [
            "# Weekly Agent Dashboard",
            f"**Week:** {self.week}",
            f"**Generated:** {agg['timestamp']}",
            "",
            "---",
            "",
            "## 📈 Summary",
            f"- **Total Processed:** {agg['summary']['total_processed']:,} items",
            f"- **Total Stored:** {agg['summary']['total_stored']:,} items",
            f"- **Total Errors:** {agg['summary']['total_errors']}",
            f"- **Enrichments:** {agg['summary']['enrichment_count']}",
            "",
            "---",
            ""
        ]
        
        # Per-agent summary
        lines.append("## 🤖 Agent Reports")
        for agent_name, report in agg['agents'].items():
            lines.append(f"\n### {agent_name.upper()}")
            
            processed_count = sum(d['count'] for d in report['processed'].values())
            stored_count = sum(d['count'] for d in report['stored'].values())
            error_count = len(report['errors'])
            enrichment_count = len(report['enrichment'])
            
            lines.append(f"- **Processed:** {processed_count}")
            lines.append(f"- **Stored:** {stored_count}")
            lines.append(f"- **Errors:** {error_count}")
            lines.append(f"- **Enrichments:** {enrichment_count}")
            
            if report['enrichment']:
                lines.append("  - **Key findings:**")
                for metric, data in list(report['enrichment'].items())[:3]:
                    lines.append(f"    - {metric}: {data['value']}")
        
        filename = f"dashboard_{self.week}.md"
        filepath = self.reports_dir / filename
        
        with open(filepath, 'w') as f:
            f.write("\n".join(lines))
        
        return str(filepath)


if __name__ == "__main__":
    # Test: Create sample reports
    
    # Stamps report
    stamps_report = AgentReport("stamps")
    stamps_report.add_processed("images_scanned", 47, "JPG + PNG from InBox")
    stamps_report.add_stored(
        "knowledge-base/stamps",
        44,
        samples=["JP-001-1960s", "US-002-1950s", "GB-003-1940s"],
        confidence=0.92
    )
    stamps_report.add_enrichment("duplicates_detected", 3, "Cross-referenced with existing catalog")
    stamps_report.add_enrichment("variants_found", 2, "Same series, different colors")
    stamps_report.add_metric("confidence_avg", 0.92, "%")
    stamps_report.add_error("format_error", "low", "1 BMP file skipped (unsupported)", 1)
    stamps_report.add_forecast("Expect 30-50 new submissions next week based on InBox queue")
    stamps_report.save_all()
    print(f"✅ Stamps report saved")
    
    # FACS report
    facs_report = AgentReport("facs")
    facs_report.add_processed("video_frames", 12847, "From training videos")
    facs_report.add_stored(
        "knowledge-base/facs",
        284,
        samples=["smile_AU12", "fear_AU5_AU20", "contempt_AU14"],
        confidence=0.87
    )
    facs_report.add_enrichment("micro_expressions", 5, "New subtle patterns identified")
    facs_report.add_enrichment("emotion_distribution", "neutral 65%, happy 23%, sad 12%", "")
    facs_report.add_metric("confidence_avg", 0.87, "%")
    facs_report.add_error("detection_failure", "low", "Face not detected in 234 frames", 234)
    facs_report.add_forecast("Continue training on edge cases (partial faces, angles)")
    facs_report.save_all()
    print(f"✅ FACS report saved")
    
    # NLP report
    nlp_report = AgentReport("nlp")
    nlp_report.add_processed("pdf_files", 12, "From Queued/")
    nlp_report.add_processed("text_chunks", 1247, "Extracted + chunked")
    nlp_report.add_stored(
        "knowledge-base/nlp",
        1247,
        samples=["chunk_001_art_history", "chunk_024_business", "chunk_156_science"],
        confidence=0.89
    )
    nlp_report.add_enrichment("entities_found", 89, "People, places, concepts extracted")
    nlp_report.add_enrichment("topics_detected", 5, "Top: art, business, technology, history, science")
    nlp_report.add_enrichment("new_domains", 3, "Expanded knowledge in: glass art, dye chemistry, postal history")
    nlp_report.add_metric("confidence_avg", 0.89, "%")
    nlp_report.add_error("parse_error", "low", "2 PDFs unreadable (scanned image + corrupt)", 2)
    nlp_report.add_forecast("Expect 15-20 new PDFs; focus on dye chemistry + art history")
    nlp_report.save_all()
    print(f"✅ NLP report saved")
    
    # Security report
    sec_report = AgentReport("security")
    sec_report.add_processed("checks_executed", 23, "System health + access + config")
    sec_report.add_stored(
        "knowledge-base/security",
        1,
        samples=["audit_log_2026_W10"],
        confidence=0.99
    )
    sec_report.add_enrichment("violations_found", 2, "Medium: Ollama endpoint unencrypted (LAN only), Low: SQL backup stale")
    sec_report.add_metric("system_health", 98, "%")
    sec_report.add_metric("check_pass_rate", 0.95, "%")
    sec_report.add_error("endpoint_unreachable", "medium", "DEAUS Ollama (10.0.0.110) not responding (1 check)", 1)
    sec_report.add_forecast("Continue baseline monitoring; plan for TLS wrap on Ollama")
    sec_report.save_all()
    print(f"✅ Security report saved")
    
    # Generate dashboard
    agg = WeeklyReportAggregator()
    agg.save_dashboard()
    print(f"✅ Dashboard saved")
    print(f"\n📁 Reports in: {agg.reports_dir}")
