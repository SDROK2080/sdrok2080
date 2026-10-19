"""
KMC-HSSD Database Initialization and Schema Management
Database: SQLite3 (compatible with standard SQL, migrations, and PostgreSQL syntax)
Entities:
- users
- researcher_profiles
- institutions
- research_ideas
- projects
- proposals
- tasks
- milestones
- research_documents
- publications
- datasets
- experiments
- analysis_runs
- collaborations
- funding_opportunities
- learning_resources
- ethics_records
- impact_indicators
- notifications
- audit_logs
"""

import sqlite3
import os
import json
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "rigi_nexus.db")

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'researcher', -- 'administrator', 'researcher', 'student', 'supervisor', 'reviewer', 'guest'
    institution TEXT,
    avatar TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS researcher_profiles (
    user_id TEXT PRIMARY KEY,
    title TEXT,
    bio TEXT,
    orcid_id TEXT,
    department TEXT,
    field_of_study TEXT,
    research_interests TEXT, -- JSON array
    h_index INTEGER DEFAULT 0,
    total_citations INTEGER DEFAULT 0,
    website TEXT,
    google_scholar TEXT,
    available_for_collab INTEGER DEFAULT 1,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS institutions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    country TEXT NOT NULL,
    type TEXT, -- University, Laboratory, Research Institute, NGO
    website TEXT,
    verified INTEGER DEFAULT 1
);

CREATE TABLE IF NOT EXISTS research_ideas (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    problem_statement TEXT,
    research_gap TEXT,
    research_questions TEXT, -- JSON array
    hypotheses TEXT, -- JSON array
    objectives TEXT,
    significance TEXT,
    theoretical_framework TEXT,
    sdg_alignment TEXT, -- JSON array (e.g. ['SDG 3: Good Health', 'SDG 13: Climate Action'])
    status TEXT DEFAULT 'draft', -- 'draft', 'in_review', 'converted_to_proposal', 'archived'
    is_sample INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS proposals (
    id TEXT PRIMARY KEY,
    idea_id TEXT,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    abstract TEXT,
    methodology TEXT,
    expected_outcomes TEXT,
    budget_estimate REAL DEFAULT 0,
    duration_months INTEGER DEFAULT 12,
    ethics_required INTEGER DEFAULT 0,
    status TEXT DEFAULT 'draft', -- 'draft', 'submitted', 'under_review', 'approved', 'rejected'
    reviewer_comments TEXT,
    is_sample INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(idea_id) REFERENCES research_ideas(id)
);

CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT, -- 'Health Sciences', 'AI & Computing', 'Climate & Environment', etc.
    stage TEXT DEFAULT 'idea', -- 'idea', 'proposal', 'ethics_review', 'data_collection', 'data_analysis', 'manuscript', 'published', 'impact_assessment'
    progress_percentage INTEGER DEFAULT 0,
    start_date DATE,
    target_end_date DATE,
    lead_researcher TEXT,
    collaborators_count INTEGER DEFAULT 1,
    is_sample INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    title TEXT NOT NULL,
    assigned_to TEXT,
    status TEXT DEFAULT 'todo', -- 'todo', 'in_progress', 'completed'
    priority TEXT DEFAULT 'medium', -- 'low', 'medium', 'high', 'urgent'
    due_date DATE,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS milestones (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    due_date DATE,
    completed INTEGER DEFAULT 0,
    completed_at DATE,
    FOREIGN KEY(project_id) REFERENCES projects(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS datasets (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    user_id TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    data_json TEXT NOT NULL, -- Store raw tabular records for analysis
    columns_json TEXT NOT NULL, -- JSON array of column metadata
    row_count INTEGER DEFAULT 0,
    is_sample INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS analysis_runs (
    id TEXT PRIMARY KEY,
    dataset_id TEXT NOT NULL,
    project_id TEXT,
    user_id TEXT NOT NULL,
    analysis_type TEXT NOT NULL, -- 'descriptive', 'correlation', 'regression', 'hypothesis_test'
    parameters TEXT, -- JSON params
    results_json TEXT NOT NULL, -- Full verified mathematical and statistical output
    interpretation TEXT,
    limitations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(dataset_id) REFERENCES datasets(id)
);

CREATE TABLE IF NOT EXISTS experiments (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    model_type TEXT NOT NULL, -- 'epidemic_sir', 'carbon_climate', 'projectile_physics', 'logistic_growth'
    parameters_json TEXT NOT NULL,
    results_json TEXT NOT NULL,
    hypotheses TEXT,
    conclusions TEXT,
    is_sample INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS publications (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    authors TEXT NOT NULL,
    journal_or_conf TEXT NOT NULL,
    publication_year INTEGER NOT NULL,
    doi TEXT,
    abstract TEXT,
    status TEXT DEFAULT 'published', -- 'draft', 'submitted', 'in_revision', 'published'
    citation_count INTEGER DEFAULT 0,
    open_access INTEGER DEFAULT 1,
    sdg_alignment TEXT,
    pdf_url TEXT,
    is_sample INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS learning_resources (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL, -- 'Methodology', 'Data Science', 'Publication', 'Ethics', 'Funding'
    resource_type TEXT NOT NULL, -- 'course', 'guide', 'video', 'dataset', 'book'
    author_or_source TEXT NOT NULL,
    description TEXT,
    url TEXT,
    tags TEXT, -- JSON array
    is_sample INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS funding_opportunities (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    agency TEXT NOT NULL,
    amount_usd TEXT NOT NULL,
    deadline DATE NOT NULL,
    eligibility TEXT,
    discipline TEXT,
    official_link TEXT,
    verified_date DATE,
    status TEXT DEFAULT 'active'
);

CREATE TABLE IF NOT EXISTS collaborations (
    id TEXT PRIMARY KEY,
    requester_id TEXT NOT NULL,
    receiver_id TEXT NOT NULL,
    project_title TEXT NOT NULL,
    proposal_message TEXT,
    status TEXT DEFAULT 'pending', -- 'pending', 'accepted', 'declined'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(requester_id) REFERENCES users(id),
    FOREIGN KEY(receiver_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS ethics_records (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    user_id TEXT NOT NULL,
    status TEXT DEFAULT 'under_review', -- 'approved', 'under_review', 'conditional_approval'
    protocol_num TEXT UNIQUE,
    irb_committee TEXT,
    informed_consent_verified INTEGER DEFAULT 0,
    data_privacy_compliant INTEGER DEFAULT 0,
    vulnerable_populations INTEGER DEFAULT 0,
    responsible_ai_checklist INTEGER DEFAULT 1,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS impact_indicators (
    id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    sdg_target TEXT NOT NULL,
    impact_type TEXT NOT NULL, -- 'policy', 'technology_transfer', 'community_benefit', 'education', 'environmental'
    description TEXT NOT NULL,
    evidence_url TEXT,
    beneficiaries_count INTEGER DEFAULT 0,
    verified INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_id) REFERENCES projects(id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    type TEXT DEFAULT 'info', -- 'info', 'success', 'warning', 'collab'
    is_read INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    action TEXT NOT NULL,
    entity TEXT NOT NULL,
    entity_id TEXT,
    details TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.executescript(SCHEMA_SQL)
    conn.commit()
    conn.close()
    print(f"Database schema initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
