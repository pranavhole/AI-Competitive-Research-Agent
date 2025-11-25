from typing import Dict, Any, List
import json
import textwrap
from datetime import datetime


class ReportGeneratorTool:
    """
    Tool for creating structured market intelligence reports from insights
    produced by DataAnalyzerTool.
    """

    def generate_report(self, insights: Dict[str, Any], title: str = "Market Intelligence Report",
                        format: str = "text") -> str:
        """
        format: "text" | "markdown" | "json"
        """
        if not insights:
            return "No insights provided."

        if format == "json":
            return json.dumps({"title": title, "generated_at": datetime.utcnow().isoformat(), "insights": insights}, indent=2)

        # Build human-readable sections
        lines: List[str] = []
        lines.append(title)
        lines.append(f"Generated: {datetime.utcnow().isoformat()}")

        summary = insights.get("summary", {})
        lines.append("\nSummary Statistics:")
        for k, stats in summary.items():
            if isinstance(stats, dict):
                lines.append(f"- {k}: count={stats.get('count')}, mean={_fmt(stats.get('mean'))}, median={_fmt(stats.get('median'))}, min={_fmt(stats.get('min'))}, max={_fmt(stats.get('max'))}")

        lines.append("\nTop Rankings:")
        for r in insights.get("rankings", []):
            lines.append(f"{r.get('rank')}. {r.get('name')} — revenue={_fmt(r.get('revenue'))}, market_share%={_fmt(r.get('market_share_pct'))}, growth%={_fmt(r.get('growth_pct'))}")

        top_growth = insights.get("top_growth", [])
        if top_growth:
            lines.append("\nFastest Growing Competitors:")
            for name, g in top_growth:
                lines.append(f"- {name}: growth_pct={_fmt(g)}")

        lines.append(f"\nTotal competitors analyzed: {insights.get('count_competitors', 0)}")

        body = "\n".join(lines)
        if format == "markdown":
            # Simple markdown conversion: wrap sections
            md = textwrap.dedent(f"""
            # {title}

            _Generated_: {datetime.utcnow().isoformat()}

            ## Summary Statistics
            """)
            for k, stats in summary.items():
                if isinstance(stats, dict):
                    md += f"\n- **{k}**: count={stats.get('count')}, mean={_fmt(stats.get('mean'))}, median={_fmt(stats.get('median'))}, min={_fmt(stats.get('min'))}, max={_fmt(stats.get('max'))}\n"

            md += "\n## Top Rankings\n"
            for r in insights.get("rankings", []):
                md += f"\n- **{r.get('rank')}. {r.get('name')}** — revenue={_fmt(r.get('revenue'))}, market_share%={_fmt(r.get('market_share_pct'))}, growth%={_fmt(r.get('growth_pct'))}\n"

            if top_growth:
                md += "\n## Fastest Growing Competitors\n"
                for name, g in top_growth:
                    md += f"\n- {name}: growth_pct={_fmt(g)}\n"

            md += f"\n\n**Total competitors analyzed**: {insights.get('count_competitors', 0)}\n"
            return md.strip()

        # default: plain text
        return body


def _fmt(value):
    if value is None:
        return "N/A"
    try:
        if isinstance(value, float):
            return f"{value:,.2f}"
        return str(value)
    except Exception:
        return str(value)