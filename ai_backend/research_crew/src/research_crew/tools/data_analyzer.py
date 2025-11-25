from typing import List, Dict, Any, Optional
from collections import defaultdict
import statistics


class DataAnalyzerTool:
    """
    Tool for analyzing competitor data and generating structured insights.

    Expected input format (list of dicts), each dict example:
    {
        "name": "Competitor A",
        "revenue": 12_000_000,
        "growth_pct": 8.5,
        "employees": 120,
        "market_share_pct": 4.2,
        "sentiment_score": 0.1,   # optional, -1..1
        "notes": "free text"
    }
    """

    def analyze(self, competitors: List[Dict[str, Any]], top_n: int = 5) -> Dict[str, Any]:
        if not competitors:
            return {"error": "no data provided", "summary": {}, "rankings": []}

        # Normalize numeric keys and compute basic stats
        numeric_fields = defaultdict(list)
        for c in competitors:
            for key in ("revenue", "growth_pct", "employees", "market_share_pct", "sentiment_score"):
                val = c.get(key)
                if isinstance(val, (int, float)):
                    numeric_fields[key].append(val)

        summary = {}
        for key, vals in numeric_fields.items():
            try:
                summary[key] = {
                    "count": len(vals),
                    "mean": statistics.mean(vals),
                    "median": statistics.median(vals),
                    "min": min(vals),
                    "max": max(vals),
                }
            except statistics.StatisticsError:
                summary[key] = {"count": 0}

        # Rank competitors primarily by revenue, fallback to market_share_pct, then growth
        def score_comp(c: Dict[str, Any]) -> float:
            revenue = float(c.get("revenue") or 0)
            share = float(c.get("market_share_pct") or 0)
            growth = float(c.get("growth_pct") or 0)
            # Weighted scoring: revenue (0.6), market share (0.25), growth (0.15)
            return revenue * 0.6 + share * 1_000_000 * 0.25 + growth * 1_000_000 * 0.15

        ranked = sorted(competitors, key=score_comp, reverse=True)

        rankings = []
        for i, c in enumerate(ranked[:top_n], start=1):
            rankings.append({
                "rank": i,
                "name": c.get("name"),
                "revenue": c.get("revenue"),
                "market_share_pct": c.get("market_share_pct"),
                "growth_pct": c.get("growth_pct"),
                "score": score_comp(c),
            })

        # Detect simple trends (example: who is growing fastest)
        growth_list = [(c.get("name"), c.get("growth_pct") or 0) for c in competitors]
        growth_list.sort(key=lambda x: x[1], reverse=True)
        top_growth = growth_list[:3]

        insights = {
            "summary": summary,
            "rankings": rankings,
            "top_growth": top_growth,
            "count_competitors": len(competitors),
        }
        return insights