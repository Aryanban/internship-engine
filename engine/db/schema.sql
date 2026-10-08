-- Internship Engine Database Schema (SQLite)

CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    careers_url TEXT,
    ats_type TEXT, -- greenhouse, lever, ashby, manual
    ats_token TEXT,
    region TEXT, -- India, UAE & GCC, Singapore & APAC, Global Remote
    primary_hook TEXT, -- SEOForge, LeadForge, PlotBook, DholeraMap
    trigger_event TEXT,
    trigger_url TEXT,
    trigger_date TEXT,
    dsa_state TEXT DEFAULT 'unknown', -- confirmed_no_dsa, likely_no_dsa, unknown, dsa_likely
    priority INTEGER DEFAULT 2, -- 1 = High-priority, 2 = Candidate, 3 = Backlog
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_id INTEGER REFERENCES companies(id),
    external_id TEXT,
    title TEXT NOT NULL,
    normalized_title TEXT,
    location_raw TEXT,
    is_remote BOOLEAN DEFAULT 0,
    timezone_offset_hours REAL,
    apply_url TEXT NOT NULL,
    jd_raw TEXT,
    jd_hash TEXT UNIQUE,
    gate1_passed BOOLEAN DEFAULT 0,
    gate1_reason TEXT,
    gate2_role_fit INTEGER, -- 0-5
    gate2_ai_native_score INTEGER, -- 0-5
    gate2_dsa_risk TEXT,
    priority_computed TEXT, -- P1, P2, P3, SKIP
    status TEXT DEFAULT 'discovered', -- discovered, shortlisted, drafted, applied, replied, rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER REFERENCES jobs(id),
    company_id INTEGER REFERENCES companies(id),
    archetype TEXT, -- ai-agents, product-fullstack, systems-realtime
    contact_route TEXT, -- public_email, founder_dm, portal
    contact_recipient TEXT,
    email_subject TEXT,
    email_body TEXT,
    sent_at TIMESTAMP,
    followup_due TIMESTAMP,
    outcome TEXT DEFAULT 'pending', -- pending, replied_positive, replied_neutral, replied_negative, ghosted
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company_id);
CREATE INDEX IF NOT EXISTS idx_jobs_hash ON jobs(jd_hash);
CREATE INDEX IF NOT EXISTS idx_jobs_priority ON jobs(priority_computed);
