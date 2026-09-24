export interface ClauseData {
  id: string;
  source: string;
  title: string;
  excerpt: string;
}

/**
 * Empty dictionary: all clause data is generated dynamically from the live backend
 * and database without department-specific hardcoding.
 */
export const clauseFixtures: Record<string, ClauseData> = {};
