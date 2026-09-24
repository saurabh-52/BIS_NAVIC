"""
BIS NAVIC — Query Analyzer
Analyzes user queries using an LLM to extract structured information:
  - Possible departments / groups
  - Query intent (standard lookup, certification, testing, hallmarking, etc.)
  - Metadata hints (committee, IS number, keywords)
  - Optimized search terms for hybrid retrieval

This module is DEPARTMENT-AGNOSTIC: it auto-discovers available departments,
groups, and committees from the local database and builds the analysis prompt
dynamically. Adding a new department = just scrape its data, no code changes.
"""

import os
import json
import time
from typing import Optional
from dataclasses import dataclass, field, asdict
from dotenv import load_dotenv

load_dotenv()


# ─── Query Intent Types ───
INTENT_TYPES = [
    "standard_lookup",       # Looking for a specific standard or set of standards
    "certification_info",    # Asking about certification process, requirements
    "testing_requirements",  # Asking about testing procedures, labs, methods
    "hallmarking",           # Hallmarking-related queries
    "compliance_check",      # Checking if a product/process complies with BIS standards
    "regulation_info",       # Asking about regulations, rules, guidelines
    "product_specification", # Asking about specifications for a product
    "general_knowledge",     # General information about BIS, departments, committees
    "comparison",            # Comparing standards, products, or processes
    "licensing",             # Asking about BIS licensing (ISI mark, etc.)
]


@dataclass
class QueryAnalysis:
    """Structured output of the Query Analyzer."""
    original_query: str
    intent: str                              # Primary intent from INTENT_TYPES
    confidence: float                        # 0.0 - 1.0 confidence in analysis
    scheme: str = "isi"                      # "isi" | "crs" | "hallmark" | "ecomark" | "fmcs" | "general"
    product_name: str = ""                   # Clean identified product/process name
    departments: list[str] = field(default_factory=list)   # Matched department names
    groups: list[str] = field(default_factory=list)        # Matched group names
    committees: list[str] = field(default_factory=list)    # Matched committee names
    search_keywords: list[str] = field(default_factory=list)  # Optimized search terms
    metadata_hints: dict = field(default_factory=dict)     # Extra hints (IS number, product type, etc.)
    reasoning: str = ""                      # Brief explanation of the analysis
    analysis_time: float = 0.0               # Time taken for analysis (seconds)

    def to_dict(self) -> dict:
        return asdict(self)


class QueryAnalyzer:
    """
    LLM-powered Query Analyzer for BIS NAVIC.
    
    Auto-discovers available departments, groups, and committees from
    the local standards database, then uses a high-level prompt template
    to analyze any incoming query.
    """

    def __init__(self, azure_client=None, azure_deployment: str = None, db_path: str = None):
        self.azure_client = azure_client
        self.azure_deployment = azure_deployment

        # Auto-discover available metadata from the database
        self._departments = []
        self._groups = []
        self._committees = []
        self._discover_metadata(db_path)

        # Build the system prompt once (reused for every query)
        self._system_prompt = self._build_system_prompt()

    def _discover_metadata(self, db_path: str = None):
        """
        Read the local search database to discover all available
        departments, groups, and committees. This makes the analyzer
        fully dynamic — when new departments are scraped, they are
        automatically included.
        """
        import sqlite3

        if db_path is None:
            db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "local_search.db")

        if not os.path.exists(db_path):
            print(f"[QueryAnalyzer] WARNING: DB not found at {db_path}. No metadata discovered.")
            return

        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row

            # Departments with counts
            rows = conn.execute("""
                SELECT department_name, COUNT(*) as cnt 
                FROM standards_data 
                GROUP BY department_name 
                ORDER BY cnt DESC
            """).fetchall()
            self._departments = [{"name": r["department_name"], "count": r["cnt"]} for r in rows]

            # Groups
            rows = conn.execute("SELECT DISTINCT group_name FROM standards_data WHERE group_name != ''").fetchall()
            self._groups = [r["group_name"] for r in rows]

            # Committees
            rows = conn.execute("SELECT DISTINCT committee_name FROM standards_data WHERE committee_name != ''").fetchall()
            self._committees = [r["committee_name"] for r in rows]

            conn.close()

            print(f"[QueryAnalyzer] Discovered: {len(self._departments)} departments, "
                  f"{len(self._groups)} groups, {len(self._committees)} committees")

        except Exception as e:
            print(f"[QueryAnalyzer] WARNING: Could not discover metadata: {e}")

    def _build_system_prompt(self) -> str:
        """
        Build a generic, high-level system prompt that instructs the LLM
        how to analyze queries. The prompt includes dynamically discovered
        metadata so it adapts as new departments are added.
        """
        dept_list = json.dumps([d["name"] for d in self._departments], indent=2) if self._departments else "[]"
        group_list = json.dumps(self._groups, indent=2) if self._groups else "[]"
        committee_list = json.dumps(self._committees, indent=2) if self._committees else "[]"
        intent_list = json.dumps(INTENT_TYPES, indent=2)

        return f"""You are a Query Analyzer for BIS NAVIC — an AI-powered Bureau of Indian Standards (BIS) compliance assistant.

Your job is to analyze a user's natural language query and extract structured information that will be used to search a database of Indian Standards.

## AVAILABLE METADATA IN OUR DATABASE

### Departments (with number of standards indexed):
{json.dumps(self._departments, indent=2)}

### Groups (broad categories under which standards are organized):
{group_list}

### Committees (sectional committees that author the standards):
{committee_list}

### Query Intent Types:
{intent_list}

## YOUR TASK

Given a user query, return a JSON object with the following structure:

{{
  "intent": "<primary intent from the intent types list>",
  "confidence": <0.0 to 1.0 — how confident you are in this analysis>,
  "scheme": "<applicable BIS scheme: 'isi' | 'crs' | 'hallmark' | 'ecomark' | 'fmcs' | 'general'>",
  "product_name": "<clean concise name of the product, technology, or topic queried>",
  "departments": ["<matching department names from the list above>"],
  "groups": ["<matching group names from the list above>"],
  "committees": ["<matching committee names from the list above>"],
  "search_keywords": ["<optimized keywords for full-text search — include synonyms, technical terms, and IS numbers if mentioned>"],
  "metadata_hints": {{
    "is_number": "<specific IS number if mentioned, e.g., 'IS 1234', else null>",
    "product_type": "<product category if identifiable, e.g., 'tablets', 'equipment', 'textiles', else null>",
    "topic_area": "<broad topic or subject area, else null>"
  }},
  "reasoning": "<1-2 sentence explanation of why you classified it this way>"
}}

## RULES

1. Use ONLY the department, group, and committee names from the lists above. Do NOT invent new ones.
2. If the query doesn't clearly match any department, return an empty departments list — don't guess.
3. If the query mentions a specific IS number (e.g., IS 12345), extract it into metadata_hints.is_number.
4. For search_keywords, include:
   - Key product/process terms from the query
   - Relevant technical synonyms and domain-specific terminology
   - Variations of the product, test, or standard being queried
   - Do NOT include generic stop words (the, is, a, an, etc.)
5. Scheme selection rules:
   - "crs": Electronics, IT equipment, smartwatches, laptops, LED lighting, solar inverters, batteries, phones.
   - "hallmark": Gold, silver, jewellery, precious metals.
   - "ecomark": Environment-friendly products, emissions, carbon footprint, biodegradable products, recycled materials.
   - "fmcs": Specifically for foreign/overseas manufacturers exporting goods to India.
   - "isi": General manufactured products, cement, steel, safety equipment, food, pharmaceuticals, packaged water, chemicals, consumer goods.
   - "general": General standards questions, cross-sector queries, or organizational questions.
6. product_name: Clean, capitalized title of the product or subject queried (max 4-5 words).
7. If the query could relate to multiple departments or groups, include ALL relevant ones.
8. Always return valid JSON. No markdown formatting, no code blocks — just the raw JSON object.
9. If you are unsure, set confidence lower (e.g., 0.4-0.6) rather than guessing wrongly.
10. The "intent" field should be the MOST LIKELY intent, not a list."""

    def analyze(self, query: str) -> QueryAnalysis:
        """
        Analyze a user query and return structured QueryAnalysis.
        Falls back to keyword extraction if LLM is unavailable.
        """
        t_start = time.time()

        if not self.azure_client:
            # Fallback: simple keyword-based analysis
            result = self._fallback_analyze(query)
            result.analysis_time = round(time.time() - t_start, 4)
            return result

        try:
            response = self.azure_client.chat.completions.create(
                model=self.azure_deployment,
                messages=[
                    {"role": "system", "content": self._system_prompt},
                    {"role": "user", "content": query}
                ],
                temperature=0.1,  # Low temperature for consistent structured output
                max_tokens=500,
                response_format={"type": "json_object"},
            )

            raw = response.choices[0].message.content
            parsed = json.loads(raw)

            prod = parsed.get("product_name") or parsed.get("metadata_hints", {}).get("product_type") or query[:35]

            result = QueryAnalysis(
                original_query=query,
                intent=parsed.get("intent", "general_knowledge"),
                confidence=float(parsed.get("confidence", 0.5)),
                scheme=parsed.get("scheme", "isi"),
                product_name=prod,
                departments=parsed.get("departments", []),
                groups=parsed.get("groups", []),
                committees=parsed.get("committees", []),
                search_keywords=parsed.get("search_keywords", []),
                metadata_hints=parsed.get("metadata_hints", {}),
                reasoning=parsed.get("reasoning", ""),
                analysis_time=round(time.time() - t_start, 4),
            )

            # Validate: ensure returned values actually exist in our metadata
            result.departments = [d for d in result.departments if d in [x["name"] for x in self._departments]]
            result.groups = [g for g in result.groups if g in self._groups]
            result.committees = [c for c in result.committees if c in self._committees]

            return result

        except Exception as e:
            print(f"[QueryAnalyzer] LLM analysis failed: {e}")
            result = self._fallback_analyze(query)
            result.analysis_time = round(time.time() - t_start, 4)
            return result

    def _fallback_analyze(self, query: str) -> QueryAnalysis:
        """
        Simple keyword-based fallback when LLM is unavailable.
        Uses heuristics to guess department, scheme, and intent.
        """
        import re
        query_lower = query.lower()

        # Intent detection by keywords
        intent = "standard_lookup"
        if any(w in query_lower for w in ["certif", "certified", "certification"]):
            intent = "certification_info"
        elif any(w in query_lower for w in ["test", "testing", "lab", "laboratory"]):
            intent = "testing_requirements"
        elif any(w in query_lower for w in ["hallmark", "gold", "silver", "jewel"]):
            intent = "hallmarking"
        elif any(w in query_lower for w in ["comply", "compliance", "compliant"]):
            intent = "compliance_check"
        elif any(w in query_lower for w in ["regulation", "rule", "guideline", "act"]):
            intent = "regulation_info"
        elif any(w in query_lower for w in ["specification", "spec"]):
            intent = "product_specification"
        elif any(w in query_lower for w in ["license", "licensing", "isi mark", "bis mark"]):
            intent = "licensing"
        elif any(w in query_lower for w in ["compare", "comparison", "difference", "vs"]):
            intent = "comparison"

        # Scheme detection
        scheme = "isi"
        if any(w in query_lower for w in ["smartwatch", "wearable", "laptop", "computer", "phone", "battery", "led", "bulb", "lamp", "it equipment", "electronics"]):
            scheme = "crs"
        elif any(w in query_lower for w in ["gold", "silver", "jewel", "hallmark", "bullion"]):
            scheme = "hallmark"
        elif any(w in query_lower for w in ["eco", "environment", "carbon", "emission", "greenhouse", "recycled"]):
            scheme = "ecomark"
        elif any(w in query_lower for w in ["foreign", "overseas", "import"]):
            scheme = "fmcs"

        # Department matching: dynamically match against discovered departments from database
        departments = []
        for d in self._departments:
            dept_name = d["name"]
            # Extract significant words from department name (>3 characters)
            words = [w.lower() for w in re.findall(r'[a-zA-Z]{4,}', dept_name)]
            if any(w in query_lower for w in words):
                departments.append(dept_name)

        # Extract IS number if present
        is_match = re.search(r'IS\s*(\d+)', query, re.IGNORECASE)
        metadata_hints = {}
        if is_match:
            metadata_hints["is_number"] = f"IS {is_match.group(1)}"

        # Extract keywords (remove stop words)
        stop_words = {"the", "is", "a", "an", "of", "for", "in", "on", "to", "and", "or",
                       "what", "which", "how", "are", "there", "any", "about", "can", "do",
                       "does", "i", "me", "my", "it", "its", "be", "been", "being", "have",
                       "has", "had", "this", "that", "these", "those", "with", "from", "by"}
        tokens = re.sub(r'[^\w\s]', ' ', query).split()
        search_keywords = [t for t in tokens if t.lower() not in stop_words and len(t) > 1]

        product_name = metadata_hints.get("product_type") or re.sub(r'[^\w\s-]', '', query).strip()[:35]

        return QueryAnalysis(
            original_query=query,
            intent=intent,
            confidence=0.4,  # Low confidence for fallback
            scheme=scheme,
            product_name=product_name,
            departments=departments,
            groups=[],
            committees=[],
            search_keywords=search_keywords,
            metadata_hints=metadata_hints,
            reasoning="Fallback keyword analysis (LLM unavailable)",
        )

    def get_metadata_summary(self) -> dict:
        """Return the discovered metadata (useful for debugging / health checks)."""
        return {
            "departments": self._departments,
            "groups": self._groups,
            "committees": self._committees,
            "intent_types": INTENT_TYPES,
        }


# ─── CLI for testing ───
if __name__ == "__main__":
    import sys

    # Initialize with Azure OpenAI if available
    azure_client = None
    azure_deployment = None
    try:
        from openai import AzureOpenAI
        api_key = os.environ.get("AZURE_OPENAI_API_KEY")
        endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        if api_key and endpoint:
            azure_client = AzureOpenAI(
                api_key=api_key,
                api_version=os.environ.get("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
                azure_endpoint=endpoint,
            )
            azure_deployment = os.environ.get("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4.1-mini")
    except ImportError:
        pass

    analyzer = QueryAnalyzer(azure_client=azure_client, azure_deployment=azure_deployment)

    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "What are the BIS standards for ayurvedic medicines?"

    print(f"\nQuery: \"{query}\"\n")
    result = analyzer.analyze(query)
    print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
