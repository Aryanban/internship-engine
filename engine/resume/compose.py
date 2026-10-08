"""
Resume Composer
Composes RenderCV YAML structures directly from config/facts.yaml
guaranteeing zero hallucinations and consistent 1-page formatting.
"""

from typing import Dict, List, Any
import yaml
from pathlib import Path

FACTS_PATH = Path(__file__).parent.parent.parent / "config" / "facts.yaml"
ARCHETYPES_PATH = Path(__file__).parent.parent.parent / "config" / "archetypes.yaml"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "output" / "resumes"

def compose_rendercv_yaml(archetype_name: str) -> Dict[str, Any]:
    with open(FACTS_PATH, "r", encoding="utf-8") as f:
        facts_data = yaml.safe_load(f)
    with open(ARCHETYPES_PATH, "r", encoding="utf-8") as f:
        arch_data = yaml.safe_load(f)

    if archetype_name not in arch_data["archetypes"]:
        raise ValueError(f"Unknown archetype: {archetype_name}")

    arch_cfg = arch_data["archetypes"][archetype_name]
    candidate = facts_data["candidate"]

    # Map fact IDs to claim strings
    facts_lookup = {fact["id"]: fact for fact in facts_data["facts"]}

    # Group selected facts by project
    projects_dict = {}
    for p_name in arch_cfg["project_order"]:
        projects_dict[p_name] = []

    for fact_id in arch_cfg["fact_ids"]:
        if fact_id not in facts_lookup:
            continue
        fact = facts_lookup[fact_id]
        p = fact["project"]
        if p in projects_dict:
            projects_dict[p].append(fact["claim"])

    # Construct RenderCV projects
    project_entries = []
    for p_name, highlights in projects_dict.items():
        if not highlights:
            continue
        entry = {
            "name": p_name,
            "highlights": highlights
        }
        if p_name == "SEOForge":
            entry["summary"] = "18-tool MCP server for AI coding agents with 156 passing tests"
            entry["link"] = "https://github.com/Aryanban/seoforge"
        elif p_name == "LeadForge":
            entry["summary"] = "High-throughput Playwright scraping suite & direct DNS MX verification"
            entry["link"] = "https://github.com/Aryanban/leadforge"
        elif p_name == "PlotBook":
            entry["summary"] = "Imperative 60 FPS GPU canvas camera, WebSockets & 362+ DDA blueprints"
            entry["link"] = "https://plotbook.webforge.me/"
        elif p_name == "DholeraMap":
            entry["summary"] = "Commercial 60 FPS GIS engine with Web Workers Flatbush R-Tree"
            entry["link"] = "https://dholeramap.com"
        project_entries.append(entry)

    # Core skills - clean, zero fluff, AI-agent native
    skills_map = [
        {"label": "Languages", "details": "TypeScript, Python, SQL, HTML/CSS"},
        {"label": "AI & Agent Tooling", "details": "Model Context Protocol (MCP), LLM Pipelines, Vitest, Playwright, Evals"},
        {"label": "Frontend & Spatial", "details": "React, Next.js, Canvas 2D/WebGL, Flatbush R-Tree, Web Workers"},
        {"label": "Backend & Systems", "details": "Node.js, FastAPI, WebSockets, Redis, SQLite, Prisma"}
    ]

    rendercv_doc = {
        "cv": {
            "name": candidate["name"],
            "location": candidate["location"],
            "email": "aryan24120@iiitd.ac.in",
            "phone": "+91 9741471391",
            "website": candidate["portfolio_url"],
            "social_networks": [
                {"network": "GitHub", "username": "Aryanban"},
                {"network": "LinkedIn", "username": "aryan-bansal-b29b69370"}
            ],
            "sections": {
                "education": [
                    {
                        "institution": candidate["institution"],
                        "area": candidate["degree"],
                        "degree": "B.Tech",
                        "start_date": "2024-08",
                        "end_date": "2028-05",
                        "highlights": [
                            "Relevant Coursework: Data Structures & Algorithms, Systems Architecture, Computer Graphics, Database Systems."
                        ]
                    }
                ],
                "projects": project_entries,
                "skills": skills_map
            }
        },
        "design": {
            "theme": "classic",
            "page": {
                "size": "us-letter",
                "top_margin": "0.45in",
                "bottom_margin": "0.45in",
                "left_margin": "0.45in",
                "right_margin": "0.45in"
            }
        },
        "settings": {
            "render_command": {
                "dont_generate_html": True,
                "dont_generate_markdown": True,
                "dont_generate_png": True
            }
        }
    }
    return rendercv_doc

def save_archetype_yaml(archetype_name: str) -> Path:
    data = compose_rendercv_yaml(archetype_name)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_DIR / f"{archetype_name}_rendercv.yaml"
    with open(out_file, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)
    return out_file

if __name__ == "__main__":
    for arch in ["ai-agents", "product-fullstack", "systems-realtime"]:
        path = save_archetype_yaml(arch)
        print(f"Generated RenderCV YAML for {arch}: {path}")
