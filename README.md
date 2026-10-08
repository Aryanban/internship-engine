# Autonomous Internship Discovery & Application Engine

> **AI-Native, No-DSA, Multi-Hub Global Internship Pipeline**  
> Programmatic discovery, deterministic Gate 1 filtering, RenderCV single-page resume compilation, and 1-click personalized outreach.

---

## 🎯 Overview

The **Autonomous Internship Engine** automates the end-to-end internship search lifecycle for high-conviction software engineering roles across key global tech hubs:
- 🇮🇳 **India**: Bangalore, Delhi NCR, Hyderabad, Pune, Mumbai (IST, GMT+5:30)
- 🇦🇪 **UAE & GCC**: Dubai (DIFC, Hub71), Abu Dhabi, Riyadh (GST, GMT+4, -1.5h from IST)
- 🇸🇬 **Singapore & APAC**: Singapore, Tokyo, Hong Kong (SGT, GMT+8, +2.5h from IST)
- 🌍 **Global Remote (Anywhere / WFA)**: US/EU/Global remote teams with $\ge 4$ hours working overlap via contractor agreements (Deel/Wise).

## ⚡ Core Philosophy & Architecture

1. **Company-First Architecture**: Jobs attach to company profiles; DSA states (`confirmed_no_dsa`, `likely_no_dsa`, `unknown`, `dsa_likely`) live on companies, preventing redundant LeetCode filters.
2. **Fact Bank (`config/facts.yaml`)**: Ground-truth claims only, mapped to live proof URLs. Prohibits hallucination or dynamic keyword stuffing.
3. **Deterministic Gate 1 Pre-Filtering**: Sub-millisecond code filter evaluating level, role, residency blockers, and hard DSA keywords before touching any LLM.
4. **RenderCV Strict 1-Page Gate**: Compiles 3 static resume archetypes (`ai-agents`, `product-fullstack`, `systems-realtime`) via Typst, enforced by automated PDF page tests.
5. **Human on Every Send**: 90–130 word high-conviction drafts citing fresh trigger events ($\le 30$ days) with a strict volume cap of 10–15 sends/week.

---

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone the repository
git clone https://github.com/Aryanban/internship-engine.git
cd internship-engine

# Create virtual environment & install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Initialize Database & Seeds
```bash
# Initialize SQLite database
python engine/cli.py init

# Import target companies from config/seeds.csv
python engine/cli.py import-seeds

# View current company targets
python engine/cli.py list-companies
```

### 3. Run Daily Ingestion & Cockpit
```bash
# Ingest live postings from Greenhouse/Lever/Ashby & build daily_digest.md
python engine/cli.py daily
```

### 4. Compile Resumes (RenderCV / Typst)
```bash
# Build and validate all 3 single-page PDF archetypes
python engine/resume/render.py
```

### 5. Generate Personalized Outreach Drafts
```bash
# Generate batch drafts for all companies in registry
python engine/outreach/generator.py

# Or generate a single draft:
python engine/outreach/draft.py "Cursor"
```

### 6. Run Test Suite
```bash
pytest tests/
```

---

## 📁 Repository Structure

```text
internship-engine/
├── config/
│   ├── facts.yaml               # Canonical single source of truth for claims
│   ├── filters.yaml             # Gate 1 keyword rules & timezone parameters
│   ├── archetypes.yaml          # Ordering & selection rules for RenderCV archetypes
│   ├── seeds.csv                # Curated company registry (company, ATS token, region, hook)
│   └── profile.example.yaml     # Profile template (gitignored profile.yaml for PII)
├── engine/
│   ├── cli.py                   # Typer CLI entrypoint (init, daily, import-seeds, list)
│   ├── gate1.py                 # Deterministic Gate 1 filter (<1ms execution)
│   ├── gate2_rubric.py          # Structured evaluation rubric with SQLite caching
│   ├── db/
│   │   └── schema.sql           # SQLite schema: companies, jobs, applications
│   ├── sources/
│   │   └── ats_fetcher.py       # Public JSON endpoints (Greenhouse, Lever, Ashby)
│   ├── resume/
│   │   ├── compose.py           # RenderCV YAML composer from facts.yaml
│   │   └── render.py            # Typst PDF compiler with 1-page gate check
│   └── outreach/
│       ├── draft.py             # 90-130 word trigger-event draft generator
│       └── generator.py         # Batch draft generator for registry
├── output/
│   ├── daily_digest.md          # Daily interactive execution cockpit
│   ├── drafts/                  # Generated personalized outreach markdown files
│   └── resumes/                 # Generated 1-page PDF archetypes
├── tests/
│   ├── test_gate1.py            # Gate 1 deterministic filter test suite
│   └── test_resume_gate.py      # Automated 1-page PDF length enforcement
├── pytest.ini                   # Pytest configuration
├── requirements.txt             # Locked dependencies
└── README.md
```

---

## 🛡️ License

MIT License. Crafted by [Aryan Bansal](https://github.com/Aryanban).
