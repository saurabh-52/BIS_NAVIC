"""
BIS NAVIC — Local FastAPI Backend (v3)
Architecture:
  Query → Query Analyzer → Hybrid Retrieval → Relevant Chunks → LLM Answer

Uses a generic, department-agnostic Query Analyzer to determine intent,
departments, and search strategy. No hardcoded department prompts.
"""

import os
import sys
import json
import time
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Ensure Windows terminal doesn't crash on unicode/emojis
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

load_dotenv()

from local_search import LocalStandardsSearch
from query_analyzer import QueryAnalyzer, QueryAnalysis

app = FastAPI(title="BIS NAVIC AI Backend (Local v3)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Initialize search engine ──
print("Initializing Local Standards Search Engine...")
search_engine = LocalStandardsSearch()

# Build index if not already built
stats = search_engine.get_stats()
if stats["total_indexed"] == 0:
    print("Building search index from raw store...")
    build_result = search_engine.build_index()
    print(f"Indexed {build_result['indexed']} standards from {len(build_result['departments'])} departments")
else:
    print(f"Search index ready: {stats['total_indexed']} standards indexed")
    print(f"Departments: {json.dumps(stats['departments'], indent=2)}")

# ── Initialize Azure OpenAI ──
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
        print(f"Azure OpenAI connected: {azure_deployment}")
    else:
        print("WARNING: Azure OpenAI not configured. Will return raw search results only.")
except ImportError:
    print("WARNING: openai package not installed. Will return raw search results only.")

# ── Initialize Query Analyzer ──
print("Initializing Query Analyzer...")
query_analyzer = QueryAnalyzer(
    azure_client=azure_client,
    azure_deployment=azure_deployment,
)
print("Query Analyzer ready.")


class QueryRequest(BaseModel):
    query: str
    department: Optional[str] = None


class ClauseData(BaseModel):
    id: str
    source: str
    title: str
    excerpt: str


class RecommendedStandard(BaseModel):
    isCode: str
    title: str
    type: str  # "Mandatory" | "Related" | "Voluntary"
    description: str


class RoadmapStep(BaseModel):
    step: int
    title: str
    description: str
    time: str
    cost: str
    portal: str


class FeeTier(BaseModel):
    application: str
    annual: str


class FeeStructure(BaseModel):
    msme: FeeTier
    large: FeeTier
    importer: FeeTier


class PipelineResult(BaseModel):
    answer: str
    product: str
    category: str
    scheme: str
    scheme_label: str
    scheme_badge_color: str
    agent_name: str
    is_code: str
    is_code_title: str
    clause_data: Optional[ClauseData] = None
    recommended_standards: list[RecommendedStandard] = []
    roadmap_steps: list[RoadmapStep] = []
    fees: FeeStructure
    portal_url: str
    portal_name: str
    factory_inspection: bool
    r_number: bool
    contexts_used: list[dict]
    metrics: dict
    tokens: dict
    triage_info: dict


# ── Answer Generation Prompt (generic, not department-specific) ──
ANSWER_SYSTEM_PROMPT = """You are an expert AI assistant for Bureau of Indian Standards (BIS) compliance.
Answer the user's question using ONLY the provided context from real BIS standards data.

CRITICAL RULES:
1. For every factual claim, cite the IS Number (e.g., [IS 19467:2026]).
2. Accurately describe each standard — include IS number, title, committee, and publication date when available.
3. Mention the relevant department(s) and sectional committee(s) where applicable.
4. If no relevant standards are found in the context, say "I could not find specific standards matching your query in our database."
5. Do NOT make up or hallucinate any IS numbers, titles, or details. Only use what is in the context.
6. Be concise but informative. Group related standards together when they share a common theme.
7. If the user is asking about certification/testing/hallmarking, provide relevant procedural information based on the standards found.
8. Adapt your response tone to the query intent — technical queries get precise answers, general queries get overview answers."""


def hybrid_search(query: str, analysis: QueryAnalysis, limit: int = 10) -> tuple[list[dict], list[dict]]:
    """
    Perform hybrid retrieval using the Query Analyzer's output.
    Returns: (direct_results, closest_matches)
    """
    all_found = []
    seen_ids = set()

    def add_results(new_results):
        for r in new_results:
            sid = r["standard_number"]
            if sid not in seen_ids:
                seen_ids.add(sid)
                all_found.append(r)

    # Strategy 1: Direct IS number lookup
    is_number = analysis.metadata_hints.get("is_number")
    if is_number:
        direct = search_engine.search(is_number, limit=3)
        add_results(direct)

    # Strategy 2: Department-filtered search with optimized keywords
    search_query = " ".join(analysis.search_keywords) if analysis.search_keywords else query

    if analysis.departments:
        for dept in analysis.departments:
            dept_results = search_engine.search(search_query, department=dept, limit=limit)
            add_results(dept_results)

    # Strategy 3: Broad search (no department filter) — catches cross-department results
    broad_results = search_engine.search(search_query, limit=limit)
    add_results(broad_results)

    # Strategy 4: If analyzer identified specific committees, also search by committee name
    if analysis.committees:
        for committee in analysis.committees:
            committee_results = search_engine.search(committee, limit=5)
            add_results(committee_results)

    # Strategy 5: Also search with the original query in case keywords missed something
    if search_query != query:
        original_results = search_engine.search(query, limit=5)
        add_results(original_results)

    # Separate into direct results vs closest matches
    if analysis.departments:
        # User query clearly matched a known department in database
        direct = [r for r in all_found if any(d.lower() in (r.get("department_name") or "").lower() for d in analysis.departments)]
        closest = [r for r in all_found if r not in direct][:3]
        return direct[:limit], closest
    else:
        # Check if any standard in database substantively matches the product keywords
        import re
        prod_words = [w.lower() for w in re.findall(r'[a-zA-Z]{4,}', (analysis.product_name or query))]
        # Exclude common non-discriminative words
        prod_words = [pw for pw in prod_words if pw not in {"need", "certification", "standards", "standard", "india", "import", "requirements", "compliance", "during", "rules", "regulations"}]
        
        direct = []
        if prod_words:
            for r in all_found:
                name_lower = (r.get("standard_name") or "").lower()
                num_lower = (r.get("standard_number") or "").lower()
                if any(pw in name_lower or pw in num_lower for pw in prod_words):
                    direct.append(r)

        if direct:
            return direct[:limit], []
        else:
            # If no direct matches in database, return top 3 closest matches from database
            closest = all_found[:3]
            for r in closest:
                r["is_closest_match"] = True
            return [], closest


def generate_answer_with_ai(
    query: str,
    direct_standards: list[dict],
    analysis: QueryAnalysis,
    closest_standards: list[dict] = None
) -> tuple[str, dict]:
    """
    Use Azure OpenAI to generate a grounded answer.
    Handles both direct matches and 'no direct information' cases transparently.
    """
    if not azure_client:
        return format_raw_answer(query, direct_standards, closest_standards), {"prompt": 0, "completion": 0, "total": 0}

    # Case 1: Direct standards found in database
    if direct_standards:
        context_parts = []
        for i, std in enumerate(direct_standards[:8]):
            parts = [f"[Doc {i+1}] IS Number: {std['standard_number']}"]
            parts.append(f"Title: {std['standard_name']}")
            parts.append(f"Department: {std['department_name']}")
            parts.append(f"Committee: {std['committee_name']}")
            parts.append(f"Group: {std['group_name']}")
            if std.get("sub_sub_group_name"):
                parts.append(f"Sub-group: {std['sub_sub_group_name']}")
            parts.append(f"Type: {std['type_of_standard']}")
            if std.get("published_on"):
                parts.append(f"Published: {std['published_on']}")
            if std.get("ministry_name"):
                parts.append(f"Ministry: {std['ministry_name']}")
            context_parts.append(" | ".join(parts))

        context_text = "\n".join(context_parts)
        analysis_context = f"""
Query Analysis:
- Intent: {analysis.intent}
- Scheme: {analysis.scheme}
- Product: {analysis.product_name}
- Departments: {', '.join(analysis.departments) if analysis.departments else 'Not determined'}
- Topic: {analysis.metadata_hints.get('topic_area', 'Not determined')}"""

        user_content = f"{analysis_context}\n\nContext from BIS Standards Database:\n{context_text}\n\nUser Query: {query}"

    # Case 2: No direct standards found in database for this product
    else:
        closest_info = ""
        if closest_standards:
            closest_parts = []
            for i, std in enumerate(closest_standards[:3]):
                closest_parts.append(f"- Closest Indexed Standard {i+1}: {std['standard_number']} — {std['standard_name']} ({std['department_name']})")
            closest_info = "Closest Standards Found in Local Index:\n" + "\n".join(closest_parts)

        prod_label = analysis.product_name or query
        user_content = f"""Query Analysis:
- Intent: {analysis.intent}
- Scheme: {analysis.scheme}
- Product: {prod_label}

STATUS: No direct Indian Standard matching this specific product is currently indexed in the local standards database.

{closest_info}

User Query: {query}

INSTRUCTIONS FOR YOUR ANSWER:
1. Clearly state upfront: "There is currently no specific standard information for '{prod_label}' in our local standards database."
2. Briefly describe the general BIS regulatory mechanism applicable to this domain (e.g. CRS scheme for electronics/IT, ISI Mark Scheme-I for general manufactured goods, Eco-Mark for environmental products, Hallmarking for precious metals).
3. If closest indexed standards were listed above, mention them as the closest available matches in the database.
4. Recommend searching the official BIS Standards Portal at https://manakonline.in to find standards across all 15 Division Councils.
5. Keep your tone professional, concise, and helpful."""

    try:
        response = azure_client.chat.completions.create(
            model=azure_deployment,
            messages=[
                {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            temperature=0.3,
            max_tokens=1000,
        )

        tokens = {
            "prompt": response.usage.prompt_tokens,
            "completion": response.usage.completion_tokens,
            "total": response.usage.total_tokens,
        }

        return response.choices[0].message.content, tokens

    except Exception as e:
        print(f"Azure OpenAI error: {e}")
        return format_raw_answer(query, direct_standards, closest_standards), {"prompt": 0, "completion": 0, "total": 0}


def format_raw_answer(query: str, direct_standards: list[dict], closest_standards: list[dict] = None) -> str:
    """Format a plain text answer when AI is unavailable."""
    if not direct_standards:
        lines = [f"There is currently no specific standard information for '{query}' in our local standards database.\n"]
        if closest_standards:
            lines.append("Closest related standards in our database:")
            for std in closest_standards[:3]:
                lines.append(f"• **{std['standard_number']}** — {std['standard_name']} ({std['department_name']})")
        lines.append("\nPlease check the official BIS portal (https://manakonline.in) for standards across all 15 Division Councils.")
        return "\n".join(lines)

    lines = [f"Found {len(direct_standards)} relevant BIS standard(s) for your query:\n"]
    for std in direct_standards[:5]:
        lines.append(f"• **{std['standard_number']}** — {std['standard_name']}")
        lines.append(f"  Department: {std['department_name']} | Committee: {std['committee_name']}")
        if std.get("published_on"):
            lines.append(f"  Published: {std['published_on']}")
        lines.append("")

    return "\n".join(lines)


# ── Generic, Dynamic UI Data Generators (No department-specific hardcoding) ──

def get_scheme_metadata(scheme: str) -> dict:
    scheme_clean = (scheme or "isi").lower()
    if scheme_clean == "crs":
        return {
            "scheme": "crs",
            "scheme_label": "SCHEME-II — CRS Registration (Compulsory Registration)",
            "scheme_badge_color": "#3B82F6",
            "portal_url": "https://crsbis.in",
            "portal_name": "CRSBIS Portal",
            "factory_inspection": False,
            "r_number": True,
        }
    elif scheme_clean == "hallmark":
        return {
            "scheme": "hallmark",
            "scheme_label": "HALLMARKING — Precious Metals Purity Certification",
            "scheme_badge_color": "#EAB308",
            "portal_url": "https://manakonline.in",
            "portal_name": "Manakonline",
            "factory_inspection": False,
            "r_number": False,
        }
    elif scheme_clean == "ecomark":
        return {
            "scheme": "ecomark",
            "scheme_label": "ECO MARK — Environmental Standards & Eco-Labelling",
            "scheme_badge_color": "#10B981",
            "portal_url": "https://ecomark.gov.in",
            "portal_name": "ECO Mark Portal",
            "factory_inspection": True,
            "r_number": False,
        }
    elif scheme_clean == "fmcs":
        return {
            "scheme": "fmcs",
            "scheme_label": "SCHEME-I (FMCS) — Foreign Manufacturers Certification",
            "scheme_badge_color": "#8B5CF6",
            "portal_url": "https://manakonline.in",
            "portal_name": "Manakonline",
            "factory_inspection": True,
            "r_number": False,
        }
    else:  # "isi" or default
        return {
            "scheme": "isi",
            "scheme_label": "SCHEME-I — ISI Mark (Standard Certification)",
            "scheme_badge_color": "#F97316",
            "portal_url": "https://manakonline.in",
            "portal_name": "Manakonline",
            "factory_inspection": True,
            "r_number": False,
        }


def determine_agent_name(analysis: QueryAnalysis, top_std: Optional[dict]) -> str:
    import re
    # 1. If analysis clearly identified a department from query, prioritize that
    if analysis.departments and len(analysis.departments) > 0:
        clean_dept = re.sub(r'\(.*?\)', '', analysis.departments[0]).strip()
        clean_dept = " ".join(w.capitalize() for w in clean_dept.split())
        if clean_dept.lower().endswith("department"):
            clean_dept = clean_dept[:-10].strip()
        return f"{clean_dept} Compliance Agent"

    # 2. If scheme is specialized (CRS, Hallmark, Eco-Mark, FMCS), use scheme specialist
    if analysis.scheme == "crs":
        return "CRS Registration Specialist Agent"
    elif analysis.scheme == "hallmark":
        return "Hallmark Assaying Specialist Agent"
    elif analysis.scheme == "ecomark":
        return "Eco-Mark Compliance Specialist Agent"
    elif analysis.scheme == "fmcs":
        return "FMCS Foreign Manufacturers Agent"

    # 3. If standard was matched from a department
    if top_std and top_std.get("department_name"):
        clean_dept = re.sub(r'\(.*?\)', '', top_std["department_name"]).strip()
        clean_dept = " ".join(w.capitalize() for w in clean_dept.split())
        if clean_dept.lower().endswith("department"):
            clean_dept = clean_dept[:-10].strip()
        return f"{clean_dept} Compliance Agent"

    return "BIS Compliance Specialist Agent"


def generate_roadmap_steps(scheme: str, product: str, is_code: str, portal_url: str) -> list[RoadmapStep]:
    if scheme == "crs":
        return [
            RoadmapStep(
                step=1,
                title="Product Categorization & Standard Review",
                description=f"Map {product} against the CRS schedule and verify applicability of {is_code}.",
                time="1–2 days",
                cost="—",
                portal=""
            ),
            RoadmapStep(
                step=2,
                title="BIS Recognized Lab Testing",
                description=f"Submit test samples to an accredited BIS laboratory to generate formal test reports per {is_code}.",
                time="3–5 weeks",
                cost="₹50,000–₹1,20,000",
                portal="lab-finder"
            ),
            RoadmapStep(
                step=3,
                title="Portal Account & Application Filing",
                description="Register manufacturing facility on the CRSBIS portal and upload technical test reports.",
                time="1–2 days",
                cost="₹1,000",
                portal=portal_url
            ),
            RoadmapStep(
                step=4,
                title="Conformity Verification & Scrutiny",
                description="BIS technical officers scrutinize lab test parameters and manufacturer affidavits.",
                time="2–3 weeks",
                cost="—",
                portal=""
            ),
            RoadmapStep(
                step=5,
                title="Grant of R-Number & Standard Marking",
                description="BIS issues unique Registration Number (R-Number). Affix standard mark with R-Number on product packaging.",
                time="1 week",
                cost="—",
                portal=""
            )
        ]
    elif scheme == "hallmark":
        return [
            RoadmapStep(
                step=1,
                title="Jeweller Portal Registration",
                description="Register retail or manufacturing entity on Manakonline with business registration and GST credentials.",
                time="1–2 days",
                cost="₹1,000",
                portal=portal_url
            ),
            RoadmapStep(
                step=2,
                title="Assaying & Hallmarking Centre (AHC) Tie-up",
                description="Select a BIS-recognized Assaying and Hallmarking Centre for testing and laser inscription.",
                time="2–3 days",
                cost="—",
                portal="lab-finder"
            ),
            RoadmapStep(
                step=3,
                title="Fire Assay / XRF Purity Testing",
                description=f"Submit lots to AHC for metallurgical analysis and purity assessment under {is_code}.",
                time="1–2 days",
                cost="₹45/article",
                portal=""
            ),
            RoadmapStep(
                step=4,
                title="Laser Inscription of HUID",
                description="AHC laser-engraves the BIS logo, purity fineness, and unique 6-character alphanumeric HUID.",
                time="Same day",
                cost="—",
                portal=""
            ),
            RoadmapStep(
                step=5,
                title="BIS Care App Verification & Retail Sale",
                description="Verified items enter retail inventory; consumers can verify authenticity on BIS Care app.",
                time="Immediate",
                cost="—",
                portal=""
            )
        ]
    elif scheme == "ecomark":
        return [
            RoadmapStep(
                step=1,
                title="Environmental & Standard Qualification",
                description=f"Validate that {product} meets both {is_code} performance criteria and Eco-Mark environmental parameters.",
                time="1–2 weeks",
                cost="—",
                portal=""
            ),
            RoadmapStep(
                step=2,
                title="Ecological Testing & Parameter Assay",
                description="Conduct laboratory tests for resource conservation, recyclability, and absence of hazardous chemicals.",
                time="3–4 weeks",
                cost="₹30,000–₹80,000",
                portal="lab-finder"
            ),
            RoadmapStep(
                step=3,
                title="Online Eco-Mark Application Filing",
                description="Submit application along with lifecycle emissions assessment and raw material declarations.",
                time="1–2 days",
                cost="₹1,000",
                portal=portal_url
            ),
            RoadmapStep(
                step=4,
                title="Facility Environmental Audit",
                description="BIS inspecting officers verify factory environmental management and waste reduction measures.",
                time="3–4 weeks",
                cost="₹7,000",
                portal=""
            ),
            RoadmapStep(
                step=5,
                title="Eco-Mark License Grant & Labeling",
                description="Certificate of Marking License granted with authorization to display the Eco-Mark alongside ISI Mark.",
                time="2–3 weeks",
                cost="—",
                portal=""
            )
        ]
    else:  # ISI / General / FMCS
        return [
            RoadmapStep(
                step=1,
                title="Standard & Process Classification",
                description=f"Classify {product} and review full technical specifications prescribed under {is_code}.",
                time="1–3 days",
                cost="—",
                portal=""
            ),
            RoadmapStep(
                step=2,
                title="In-House QC & Testing Infrastructure",
                description=f"Establish required in-house testing equipment and quality assurance procedures as dictated by {is_code}.",
                time="2–4 weeks",
                cost="Varies",
                portal=""
            ),
            RoadmapStep(
                step=3,
                title="Laboratory Sample Testing",
                description="Send reference samples to BIS-approved laboratory for independent testing across all standard parameters.",
                time="2–4 weeks",
                cost="₹20,000–₹60,000",
                portal="lab-finder"
            ),
            RoadmapStep(
                step=4,
                title="Application Submission (Form V)",
                description="Submit formal application on Manakonline with factory layout, quality manual, and preliminary test reports.",
                time="1–2 days",
                cost="₹1,000",
                portal=portal_url
            ),
            RoadmapStep(
                step=5,
                title="BIS Factory Inspection & Sampling",
                description="BIS technical auditor conducts on-site factory verification and draws independent counter-samples for testing.",
                time="3–6 weeks",
                cost="₹7,000",
                portal=""
            ),
            RoadmapStep(
                step=6,
                title="License Grant (CM/L)",
                description="Upon satisfactory factory audit and lab results, BIS issues Certificate of Marking License (CM/L).",
                time="1–2 weeks",
                cost="—",
                portal=""
            )
        ]


def generate_fees(scheme: str) -> FeeStructure:
    if scheme == "crs":
        return FeeStructure(
            msme=FeeTier(application="₹1,000", annual="₹2,000"),
            large=FeeTier(application="₹1,000", annual="₹5,000"),
            importer=FeeTier(application="₹1,000", annual="₹10,000"),
        )
    elif scheme == "hallmark":
        return FeeStructure(
            msme=FeeTier(application="₹0", annual="₹1,500"),
            large=FeeTier(application="₹0", annual="₹5,000"),
            importer=FeeTier(application="N/A", annual="N/A"),
        )
    elif scheme == "ecomark":
        return FeeStructure(
            msme=FeeTier(application="₹1,000", annual="₹3,000"),
            large=FeeTier(application="₹1,000", annual="₹8,000"),
            importer=FeeTier(application="₹1,000", annual="₹15,000"),
        )
    else:  # ISI / General / FMCS
        return FeeStructure(
            msme=FeeTier(application="₹1,000", annual="₹3,500"),
            large=FeeTier(application="₹1,000", annual="₹7,000"),
            importer=FeeTier(application="₹1,000", annual="₹12,000"),
        )


def generate_clause_data(top_std: Optional[dict], product: str, has_direct_match: bool = True) -> Optional[ClauseData]:
    if not top_std or not has_direct_match:
        return None

    is_num = top_std.get("standard_number", "IS Standard")
    dept = top_std.get("department_name", "Bureau of Indian Standards")
    committee = top_std.get("committee_name", "Technical Committee")
    title = top_std.get("standard_name", "Standard Specification")

    return ClauseData(
        id=f"clause-{is_num.lower().replace(' ', '-')}",
        source=f"{is_num} — {dept}",
        title=f"Conformity & Technical Parameters: {title}",
        excerpt=f"Under **{is_num}**, formulated by **{committee}** ({dept}), all manufacturing units and commercial distributors must ensure that product samples conform to mandated safety, purity, physical, and chemical thresholds. Compliance verification requires maintaining formal test records, traceable lot numbering, and compliance with periodic testing schedules."
    )


def generate_recommended_standards(results: list[dict], is_closest: bool = False) -> list[RecommendedStandard]:
    standards = []
    for idx, r in enumerate(results[:6]):
        dept = r.get("department_name") or "BIS"
        comm = r.get("committee_name") or ""
        std_type = r.get("type_of_standard") or "Standard"

        if is_closest:
            desc = f"Closest indexed standard in local database (from {dept})."
            tier = "Closest Match"
        else:
            desc = f"Standard formulated by {comm} under {dept} ({std_type})." if comm else f"Official Indian Standard specification under {dept}."
            tier = "Mandatory" if idx == 0 else ("Related" if idx < 3 else "Voluntary")

        standards.append(RecommendedStandard(
            isCode=r["standard_number"],
            title=r["standard_name"],
            type=tier,
            description=desc,
        ))
    return standards


@app.post("/ask", response_model=PipelineResult)
async def ask_pipeline(req: QueryRequest):
    """
    Main query endpoint.
    Flow: Query → Analyzer → Hybrid Retrieval → LLM Answer → Dynamic Roadmap
    """
    query = req.query
    metrics = {}
    t_start = time.time()

    # ── Step 1: Query Analysis ──
    t_analysis_start = time.time()
    analysis = query_analyzer.analyze(query)
    metrics["analysis_time"] = round(time.time() - t_analysis_start, 4)

    print(f"\n{'='*60}")
    print(f"Query: \"{query}\"")
    print(f"  Intent: {analysis.intent} (conf: {analysis.confidence})")
    print(f"  Scheme: {analysis.scheme} | Product: {analysis.product_name}")
    print(f"  Departments: {analysis.departments}")
    print(f"  Groups: {analysis.groups}")
    print(f"  Committees: {analysis.committees}")
    print(f"  Keywords: {analysis.search_keywords}")
    print(f"  Hints: {analysis.metadata_hints}")
    print(f"  Reasoning: {analysis.reasoning}")
    print(f"{'='*60}\n")

    # Override department if explicitly provided in request
    if req.department:
        analysis.departments = [req.department]

    # ── Step 2: Hybrid Retrieval ──
    t_search_start = time.time()
    direct_results, closest_results = hybrid_search(query, analysis, limit=10)
    metrics["search_time"] = round(time.time() - t_search_start, 4)
    has_direct_match = len(direct_results) > 0
    active_results = direct_results if has_direct_match else closest_results
    metrics["results_found"] = len(direct_results)
    metrics["closest_results_found"] = len(closest_results)

    # Collect triage metadata from results
    departments_found = list(set(r["department_name"] for r in active_results if r.get("department_name")))
    committees_found = list(set(r["committee_name"] for r in active_results if r.get("committee_name")))

    triage_info = {
        "query_analysis": analysis.to_dict(),
        "initial_groups_searched": [{"group": g, "confidence": analysis.confidence} for g in analysis.groups],
        "fallback_triggered": not has_direct_match,
        "fallback_groups_searched": [],
        "max_initial_similarity": 1.0 if has_direct_match else (0.5 if closest_results else 0.0),
        "departments_matched": departments_found,
        "committees_matched": committees_found,
        "source": "local_hybrid_retrieval",
    }

    # ── Step 3: Generate Answer ──
    t_gen_start = time.time()
    answer, tokens = generate_answer_with_ai(query, direct_results, analysis, closest_results)
    metrics["answer_generation_time"] = round(time.time() - t_gen_start, 4)

    # ── Step 4: Format contexts for frontend ──
    contexts_used = []
    for r in active_results[:5]:
        contexts_used.append({
            "id": r["standard_number"],
            "text": f"{r['standard_name']} | Committee: {r['committee_name']} | Type: {r['type_of_standard']}",
            "is_number": r["standard_number"],
            "clause": "Full Standard Metadata",
            "namespace": r.get("group_name", "Unknown"),
            "pinecone_score": 0.0,
            "rerank_score": abs(r.get("relevance_rank", 0)),
        })

    # ── Step 5: Dynamically assemble full structured compliance roadmap ──
    top_std = direct_results[0] if has_direct_match else (closest_results[0] if closest_results else None)
    scheme_meta = get_scheme_metadata(analysis.scheme)
    agent_name = determine_agent_name(analysis, top_std if has_direct_match else None)

    product = analysis.product_name or (top_std["standard_name"][:40] if (top_std and has_direct_match) else query[:35])

    # Dynamic generic category assignment
    category = "Bureau of Indian Standards"
    if analysis.departments and len(analysis.departments) > 0:
        category = analysis.departments[0]
    elif analysis.scheme == "crs":
        category = "Electronics & Information Technology (CRS)"
    elif analysis.scheme == "hallmark":
        category = "Precious Metals & Hallmarking"
    elif analysis.scheme == "ecomark":
        category = "Environment & Eco-Mark"
    elif analysis.scheme == "fmcs":
        category = "Foreign Manufacturers Certification (FMCS)"
    elif top_std and has_direct_match and (top_std.get("department_name") or top_std.get("group_name")):
        category = top_std.get("department_name") or top_std.get("group_name")

    # Dynamic generic IS code selection
    if has_direct_match and top_std:
        is_code = top_std["standard_number"]
        is_code_title = top_std["standard_name"]
    elif top_std and not has_direct_match:
        is_code = f"{top_std['standard_number']} (Closest Match)"
        is_code_title = f"{top_std['standard_name']} [Indexed in database]"
    else:
        is_code = analysis.metadata_hints.get("is_number") or ("IS 13252 (Part 1)" if analysis.scheme == "crs" else "IS Standard Specification")
        is_code_title = f"Indian Standard Specification for {product}"

    clause_data = generate_clause_data(top_std, product, has_direct_match=has_direct_match)
    recommended_standards = generate_recommended_standards(active_results, is_closest=not has_direct_match)
    roadmap_steps = generate_roadmap_steps(analysis.scheme, product, is_code, scheme_meta["portal_url"])
    fees = generate_fees(analysis.scheme)

    metrics["total_latency"] = round(time.time() - t_start, 4)

    return PipelineResult(
        answer=answer,
        product=product,
        category=category,
        scheme=scheme_meta["scheme"],
        scheme_label=scheme_meta["scheme_label"],
        scheme_badge_color=scheme_meta["scheme_badge_color"],
        agent_name=agent_name,
        is_code=is_code,
        is_code_title=is_code_title,
        clause_data=clause_data,
        recommended_standards=recommended_standards,
        roadmap_steps=roadmap_steps,
        fees=fees,
        portal_url=scheme_meta["portal_url"],
        portal_name=scheme_meta["portal_name"],
        factory_inspection=scheme_meta["factory_inspection"],
        r_number=scheme_meta["r_number"],
        contexts_used=contexts_used,
        metrics=metrics,
        tokens=tokens,
        triage_info=triage_info,
    )


@app.get("/stats")
async def get_stats():
    """Return index and store statistics."""
    return search_engine.get_stats()


@app.get("/health")
async def health():
    """Health check endpoint."""
    stats = search_engine.get_stats()
    return {
        "status": "ok",
        "indexed_standards": stats["total_indexed"],
        "departments": stats["departments"],
        "azure_openai": azure_client is not None,
        "query_analyzer_metadata": query_analyzer.get_metadata_summary(),
    }


@app.post("/rebuild-index")
async def rebuild_index():
    """Rebuild the search index from raw store."""
    result = search_engine.build_index()
    return {"status": "ok", "result": result}


@app.post("/analyze")
async def analyze_query(req: QueryRequest):
    """Debug endpoint: see how the Query Analyzer interprets a query."""
    analysis = query_analyzer.analyze(req.query)
    return analysis.to_dict()


if __name__ == "__main__":
    import uvicorn
    print("\n  Starting BIS NAVIC Local Backend v3 on http://127.0.0.1:8001")
    print("   Endpoints: POST /ask, POST /analyze, GET /stats, GET /health, POST /rebuild-index\n")
    uvicorn.run(app, host="127.0.0.1", port=8001)
