import Database from 'better-sqlite3';
import path from 'path';

// Note: The sqlite DB is located in /scraper/bis_standards.db
// We resolve the path relative to the project root (process.cwd())
const dbPath = path.join(process.cwd(), 'scraper', 'bis_standards.db');

export function getDb() {
  return new Database(dbPath, { readonly: true });
}

export function getAllStandards() {
  const db = getDb();
  try {
    return db.prepare(`
      SELECT 
        id, is_number, title, department_name, published_on, life_cycle_status 
      FROM standards 
      ORDER BY id ASC
    `).all();
  } finally {
    db.close();
  }
}

export function getStandardById(id: string) {
  const db = getDb();
  try {
    const standard = db.prepare('SELECT * FROM standards WHERE id = ?').get(id);
    
    if (!standard) return null;
    
    // Fetch relational data
    const standards_referred = db.prepare('SELECT * FROM standards_referred WHERE standard_id = ?').all(id);
    const gazette_documents = db.prepare('SELECT * FROM gazette_documents WHERE standard_id = ?').all(id);
    
    return {
      ...standard,
      standards_referred,
      gazette_documents
    };
  } finally {
    db.close();
  }
}
