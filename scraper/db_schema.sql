-- BIS Standards Scraper — SQLite Schema

-- Main Standards Table
CREATE TABLE IF NOT EXISTS standards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    raw_standard_id INTEGER UNIQUE,
    encrypted_id TEXT UNIQUE NOT NULL,
    is_number TEXT NOT NULL,
    title TEXT,
    published_on TEXT,
    type_of_standard TEXT,
    no_of_revisions INTEGER,
    no_of_amendments INTEGER,
    language TEXT,
    pdf_document TEXT,
    hindi_document TEXT,
    life_cycle_status TEXT,
    department_name TEXT,
    department_id INTEGER,
    technical_committee_name TEXT,
    technical_committee_id INTEGER,
    
    -- Classification Details
    group_name TEXT,
    sub_group_name TEXT,
    sub_sub_group_name TEXT,
    sector_name TEXT,
    sub_sector_name TEXT,
    sub_sub_sector_name TEXT,
    certification TEXT,
    relevant_ministry TEXT,
    sustainable_development_goals TEXT,
    short_title TEXT,
    ics_code TEXT,
    degree_of_equivalence TEXT,
    equivalent_international_standard TEXT,
    risk_level TEXT,
    reaffirmation_year TEXT,
    
    -- Metadata
    source_url TEXT,
    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Cross-references (Standards Referred)
CREATE TABLE IF NOT EXISTS standards_referred (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    standard_id INTEGER NOT NULL,
    is_type INTEGER, -- 1 for Indian, 2 for International
    referred_standard_number TEXT,
    referred_standard_name TEXT,
    referred_encrypted_id TEXT,
    FOREIGN KEY (standard_id) REFERENCES standards(id) ON DELETE CASCADE
);

-- Amendments
CREATE TABLE IF NOT EXISTS amendments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    standard_id INTEGER NOT NULL,
    amendment_number TEXT,
    document TEXT,
    published_on TEXT,
    FOREIGN KEY (standard_id) REFERENCES standards(id) ON DELETE CASCADE
);

-- Gazette Documents
CREATE TABLE IF NOT EXISTS gazette_documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    standard_id INTEGER NOT NULL,
    so_number TEXT,
    amendment_number TEXT,
    document TEXT,
    FOREIGN KEY (standard_id) REFERENCES standards(id) ON DELETE CASCADE
);

-- Licences
CREATE TABLE IF NOT EXISTS licences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    standard_id INTEGER NOT NULL,
    licence_number TEXT,
    firm_name TEXT,
    address TEXT,
    status TEXT,
    FOREIGN KEY (standard_id) REFERENCES standards(id) ON DELETE CASCADE
);

-- Product Manuals
CREATE TABLE IF NOT EXISTS product_manuals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    standard_id INTEGER NOT NULL,
    title TEXT,
    document TEXT,
    FOREIGN KEY (standard_id) REFERENCES standards(id) ON DELETE CASCADE
);

-- Laboratories
CREATE TABLE IF NOT EXISTS laboratories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    standard_id INTEGER NOT NULL,
    lab_name TEXT,
    address TEXT,
    scope TEXT,
    FOREIGN KEY (standard_id) REFERENCES standards(id) ON DELETE CASCADE
);

-- Corrigendums
CREATE TABLE IF NOT EXISTS corrigendums (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    standard_id INTEGER NOT NULL,
    title TEXT,
    document TEXT,
    FOREIGN KEY (standard_id) REFERENCES standards(id) ON DELETE CASCADE
);
