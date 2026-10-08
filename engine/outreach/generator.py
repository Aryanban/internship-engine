"""
Batch Outreach Generator
Generates personalized, high-conviction outreach packages for all P1/P2 companies
in the database, matching the optimal archetype, regional context, and trigger events.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import sqlite3
from pathlib import Path
from engine.outreach.draft import generate_draft_for_company

DB_PATH = Path(__file__).parent.parent.parent / "data" / "jobs.sqlite3"
DRAFTS_DIR = Path(__file__).parent.parent.parent / "output" / "drafts"

def generate_all_seed_drafts():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    companies = conn.execute("SELECT name, priority, region, primary_hook FROM companies ORDER BY priority ASC, name ASC").fetchall()
    
    generated = []
    for c in companies:
        name = c["name"]
        try:
            path = generate_draft_for_company(name)
            generated.append((name, c["priority"], c["region"], c["primary_hook"], path))
        except Exception as e:
            print(f"Skipping {name}: {e}")
            
    print(f"\n✓ Generated {len(generated)} personalized outreach drafts in output/drafts/")
    return generated

if __name__ == "__main__":
    generate_all_seed_drafts()
