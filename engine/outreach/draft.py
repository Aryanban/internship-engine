"""
Outreach Draft Generator
Generates personalized, high-conviction 90-130 word cold outreach drafts
citing fresh company trigger events and verified proof-of-work repositories.
"""

from typing import Optional, Dict
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "jobs.sqlite3"
DRAFTS_DIR = Path(__file__).parent.parent.parent / "output" / "drafts"

TEMPLATES = {
    "ai_founder": """Subject: {trigger_subject} + an 18-tool MCP server I built

Hi {recipient_name},

{trigger_sentence}

I'm a 3rd-year CS student at IIIT-Delhi who builds production AI-agent infrastructure:
• SEOForge (github.com/Aryanban/seoforge): 18-tool Model Context Protocol (MCP) server with 156 passing Vitest tests.
• LeadForge (github.com/Aryanban/leadforge): High-throughput Playwright pipelines replacing $100+/mo third-party SaaS subscriptions.

I work in IST and I'm available for Summer 2027 (and selective part-time/contractor work before that). Happy to do a take-home build round or paid trial if that's how you evaluate candidates.

Resume: https://www.webforge.me/resume/ai-agents.pdf · Portfolio: https://www.webforge.me/
GitHub: https://github.com/Aryanban

Best,
Aryan Bansal | IIIT-Delhi
""",

    "proptech_founder": """Subject: Full-Stack Systems / 60 FPS GIS & Web Worker Architecture

Hi {recipient_name},

{trigger_sentence}

Given your focus on real estate intelligence and spatial systems, here is relevant working code:
• DholeraMap (dholeramap.com): Commercial 60 FPS GIS engine rendering 10k+ parcels using custom binary geometry and background Web Worker spatial indexing.
• PlotBook (plotbook.webforge.me): Digitized 362+ layout blueprints with an imperative 60 FPS GPU canvas camera, WebSocket sync, and sub-5ms search.

I'm a 3rd-year CS student at IIIT-Delhi. With direct working-hour overlap (GST/SGT/IST), I can collaborate in real-time as an international contractor.

Resume: https://www.webforge.me/resume/systems-realtime.pdf · Portfolio: https://www.webforge.me/
GitHub: https://github.com/Aryanban

Best,
Aryan Bansal | IIIT-Delhi
"""
}

def generate_draft_for_company(company_name: str, recipient_name: str = "Hiring Team") -> str:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    comp = conn.execute("SELECT * FROM companies WHERE LOWER(name) = LOWER(?)", (company_name,)).fetchone()
    if not comp:
        raise ValueError(f"Company '{company_name}' not found in registry.")

    hook = comp["primary_hook"]
    template_key = "proptech_founder" if hook in ["DholeraMap", "PlotBook"] else "ai_founder"
    tpl = TEMPLATES[template_key]

    trigger_subject = f"{comp['name']}'s {comp['trigger_event'][:40]}"
    trigger_sentence = f"Saw your recent update regarding {comp['trigger_event']} ({comp['trigger_url']}) — loved the velocity your team is shipping with."

    draft_text = tpl.format(
        recipient_name=recipient_name,
        trigger_subject=trigger_subject,
        trigger_sentence=trigger_sentence
    )

    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    filename = DRAFTS_DIR / f"{company_name.lower().replace(' ', '_')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Outreach Draft: {comp['name']}\n")
        f.write(f"- **Region**: {comp['region']}\n")
        f.write(f"- **DSA State**: `{comp['dsa_state']}`\n")
        f.write(f"- **Trigger Event**: [{comp['trigger_event']}]({comp['trigger_url']})\n")
        f.write(f"- **Primary Proof Hook**: `{comp['primary_hook']}`\n\n---\n\n")
        f.write("```text\n")
        f.write(draft_text)
        f.write("```\n")

    return str(filename)

if __name__ == "__main__":
    import sys
    c = sys.argv[1] if len(sys.argv) > 1 else "Cursor"
    path = generate_draft_for_company(c)
    print(f"Draft written to: {path}")
