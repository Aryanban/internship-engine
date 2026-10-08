import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
"""
Internship Engine CLI Entrypoint
Commands:
  daily     - Run daily ingestion & build interactive cockpit (daily_digest.md)
  seeds     - Import companies from config/seeds.csv into local SQLite
  draft     - Generate a personalized outreach draft for a company
  status    - View pipeline summary counts
"""

import typer
import sqlite3
import csv
from pathlib import Path
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="Autonomous Internship Engine")
console = Console()

DB_PATH = Path(__file__).parent.parent / "data" / "jobs.sqlite3"
SCHEMA_PATH = Path(__file__).parent / "db" / "schema.sql"
SEEDS_PATH = Path(__file__).parent.parent / "config" / "seeds.csv"
DIGEST_PATH = Path(__file__).parent.parent / "output" / "daily_digest.md"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        with open(SCHEMA_PATH, "r") as f:
            conn.executescript(f.read())

@app.command()
def init():
    """Initialize the SQLite database schema."""
    init_db()
    console.print("[green]✓ Database initialized successfully at data/jobs.sqlite3[/green]")

@app.command()
def import_seeds():
    """Import companies from config/seeds.csv into SQLite."""
    init_db()
    if not SEEDS_PATH.exists():
        console.print("[red]Error: config/seeds.csv not found.[/red]")
        raise typer.Exit(code=1)

    count = 0
    with get_db() as conn:
        with open(SEEDS_PATH, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                conn.execute("""
                    INSERT INTO companies (name, careers_url, ats_type, ats_token, region, primary_hook, trigger_event, trigger_url, priority, dsa_state, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                        careers_url=excluded.careers_url,
                        ats_type=excluded.ats_type,
                        ats_token=excluded.ats_token,
                        region=excluded.region,
                        primary_hook=excluded.primary_hook,
                        trigger_event=excluded.trigger_event,
                        trigger_url=excluded.trigger_url,
                        priority=excluded.priority,
                        dsa_state=excluded.dsa_state,
                        notes=excluded.notes
                """, (
                    row["company"], row["careers_url"], row["ats"], row["ats_token"],
                    row["region"], row["primary_hook"], row["trigger_event"], row["trigger_url"],
                    int(row["priority"]), row["dsa_state"], row.get("notes", "")
                ))
                count += 1
    console.print(f"[green]✓ Successfully imported {count} companies from seeds.csv into registry.[/green]")

@app.command()
def list_companies():
    """List all registered companies in the local database."""
    init_db()
    with get_db() as conn:
        rows = conn.execute("SELECT name, region, ats_type, dsa_state, priority, primary_hook FROM companies ORDER BY priority ASC, name ASC").fetchall()

    table = Table(title="Target Companies Registry")
    table.add_column("Company", style="bold")
    table.add_column("Priority", justify="center")
    table.add_column("Region")
    table.add_column("ATS")
    table.add_column("DSA State")
    table.add_column("Primary Hook")

    for r in rows:
        p_badge = f"[bold red]P{r['priority']}[/bold red]" if r["priority"] == 1 else f"P{r['priority']}"
        table.add_row(r["name"], p_badge, r["region"], r["ats_type"], r["dsa_state"], r["primary_hook"])

    console.print(table)

@app.command()
def daily():
    """Run daily discovery & build the interactive daily_digest.md cockpit."""
    init_db()
    import_seeds()
    from engine.sources.ats_fetcher import fetch_greenhouse, fetch_lever, fetch_ashby
    from engine.gate1 import Gate1Filter
    import hashlib

    filter_engine = Gate1Filter()
    new_jobs_count = 0
    passed_gate1_count = 0

    with get_db() as conn:
        companies = conn.execute("SELECT * FROM companies").fetchall()
        for comp in companies:
            c_name = comp["name"]
            ats = comp["ats_type"]
            token = comp["ats_token"]
            if not token:
                continue

            fetched = []
            if ats == "greenhouse":
                fetched = fetch_greenhouse(token, c_name)
            elif ats == "lever":
                fetched = fetch_lever(token, c_name)
            elif ats == "ashby":
                fetched = fetch_ashby(token, c_name)

            for job in fetched:
                jd_hash = hashlib.sha256(f"{c_name}_{job.title}_{job.location}".encode()).hexdigest()
                eval_res = filter_engine.evaluate(job.title, job.location, job.jd_raw)

                cursor = conn.execute("""
                    INSERT OR IGNORE INTO jobs 
                    (company_id, external_id, title, location_raw, is_remote, apply_url, jd_raw, jd_hash, gate1_passed, gate1_reason, priority_computed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    comp["id"], job.external_id, job.title, job.location,
                    eval_res.is_remote, job.apply_url, job.jd_raw, jd_hash,
                    eval_res.passed, eval_res.reason,
                    "P1" if (eval_res.passed and comp["priority"] == 1) else ("P2" if eval_res.passed else "SKIP")
                ))
                if cursor.rowcount > 0:
                    new_jobs_count += 1
                    if eval_res.passed:
                        passed_gate1_count += 1

    # Generate daily_digest.md
    build_digest()
    console.print(f"[green]✓ Daily run completed. Processed {new_jobs_count} new postings. {passed_gate1_count} passed Gate 1.[/green]")
    console.print(f"[cyan]→ Daily Cockpit written to: output/daily_digest.md[/cyan]")

def build_digest():
    """Build the markdown cockpit file."""
    with get_db() as conn:
        p1_jobs = conn.execute("""
            SELECT j.title, j.location_raw, j.apply_url, c.name as company, c.region, c.primary_hook, c.trigger_event, c.trigger_url, c.dsa_state
            FROM jobs j
            JOIN companies c ON j.company_id = c.id
            WHERE j.priority_computed = 'P1'
            ORDER BY j.created_at DESC
        """).fetchall()

        all_companies = conn.execute("SELECT * FROM companies ORDER BY priority ASC, name ASC").fetchall()

    DIGEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DIGEST_PATH, "w", encoding="utf-8") as f:
        f.write("# 🚀 Autonomous Internship Engine — Global Daily Cockpit\n\n")
        f.write("> **Direct Overlap Focus: UAE/GCC (GST -1.5h), Singapore (SGT +2.5h), India (IST 0h), Global Remote**\n\n")
        f.write("## 🎯 Active Priority Matches (Gate 1 Passed)\n\n")

        if not p1_jobs:
            f.write("_No open intern postings currently detected via public ATS. See Target Company Queue below for proactive outreach._\n\n")
        else:
            for j in p1_jobs:
                f.write(f"### [{j['company']}] {j['title']}\n")
                f.write(f"- **Region**: {j['region']} (`{j['location_raw']}`)\n")
                f.write(f"- **DSA State**: `{j['dsa_state']}`\n")
                f.write(f"- **Trigger Event**: {j['trigger_event']} ([Source]({j['trigger_url']}))\n")
                f.write(f"- **Primary Proof Hook**: `{j['primary_hook']}`\n")
                f.write(f"- **Action**: [Apply via Official Portal]({j['apply_url']})\n\n")

        f.write("## 🏢 Curated Company Outreach Queue (First 30 Targets)\n\n")
        f.write("| Priority | Company | Region | Primary Hook | Trigger Event | DSA State |\n")
        f.write("| :---: | :--- | :--- | :--- | :--- | :---: |\n")
        for c in all_companies:
            f.write(f"| P{c['priority']} | **{c['name']}** | {c['region']} | `{c['primary_hook']}` | [{c['trigger_event']}]({c['trigger_url']}) | `{c['dsa_state']}` |\n")

if __name__ == "__main__":
    app()
