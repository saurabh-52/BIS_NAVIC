import { mockQueries, MockQueryResult, PipelineStage } from './mockData';

/**
 * Mock Agent Service — simulates the exact 6-stage pipeline from the architecture slide.
 * Pipeline stages and agent names match the pitch deck verbatim.
 */

// Department-agnostic fallback key — no department hardcoding
function resolveQueryKey(_query: string): string {
  return 'general';
}

// Returns the 6 pipeline stages with generic label
export function buildPipelineStages(agentName: string = "BIS Compliance Agent"): PipelineStage[] {
  return [
    {
      id: 1,
      label: "Query & Persona Input",
      detail: "Capturing product description, intent, persona, language",
      status: "pending"
    },
    {
      id: 2,
      label: "Intent & Triage Classifier",
      detail: `Routing to ${agentName}`,
      status: "pending"
    },
    {
      id: 3,
      label: "Hybrid RAG & Vector Retrieval",
      detail: "searching 20,000+ IS standards in vector DB",
      status: "pending"
    },
    {
      id: 4,
      label: "Multi-Agent Reasoning",
      detail: `${agentName} evaluating scheme eligibility, testing requirements, fees`,
      status: "pending"
    },
    {
      id: 5,
      label: "Clause Citation & Verification",
      detail: "verifying clause references",
      status: "pending"
    },
    {
      id: 6,
      label: "Roadmap & Voice Output",
      detail: "Generating compliance roadmap",
      status: "pending"
    }
  ];
}

export interface ComplianceQueryResult {
  data: MockQueryResult;
  stages: PipelineStage[];
}

const BACKEND_URL = "/api/ask";

/**
 * Main entrypoint — runComplianceQuery
 * Calls the real FastAPI backend (/api/ask) if available, with real-time pipeline stage updates.
 * Strictly completes each stage before moving to the next one in animation.
 */
export async function runComplianceQuery(
  query: string,
  persona: string,
  language: string,
  onStageUpdate: (stages: PipelineStage[]) => void
): Promise<MockQueryResult> {
  const fallbackKey = resolveQueryKey(query);
  const fallbackResult = mockQueries[fallbackKey] || mockQueries["general"];
  
  // 1. Build initial stages: all in 'pending' status
  const stages = buildPipelineStages(fallbackResult.agentName);
  onStageUpdate([...stages]);

  // 2. Start the backend fetch in the background immediately
  const backendPromise = (async () => {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 45000);

      const resp = await fetch(BACKEND_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
        signal: controller.signal
      });
      clearTimeout(timeoutId);

      if (resp.ok) {
        const data = await resp.json();
        console.log("[runComplianceQuery] Live AI Response Received:", data);
        return data;
      } else {
        console.warn(`[runComplianceQuery] Backend error status ${resp.status}`);
      }
    } catch (err) {
      console.warn("[runComplianceQuery] FastAPI backend not reachable or timed out, using fallback:", err);
    }
    return null;
  })();

  /**
   * Helper: Execute a stage sequentially
   * - Step 1: Set status to "running", emit update, wait for running work duration.
   * - Step 2: Set status to "done", emit update (checkmark appears).
   * - Step 3: CRITICAL PAUSE: Wait for the completion animation to visibly finish
   *   (checkmark pop + connector line draw) BEFORE moving to the next tracker.
   */
  const executeStage = async (
    stageIndex: number,
    runDurationMs: number,
    completionPauseMs: number,
    detailOverride?: string
  ) => {
    stages[stageIndex].status = "running";
    if (detailOverride) {
      stages[stageIndex].detail = detailOverride;
    }
    onStageUpdate([...stages]);
    await sleep(runDurationMs);

    stages[stageIndex].status = "done";
    onStageUpdate([...stages]);

    // Visibly hold on the completed stage before the next stage begins
    await sleep(completionPauseMs);
  };

  // Stage 1: Query & Persona Input
  await executeStage(0, 600, 450);

  // Stage 2: Intent & Triage Classifier
  await executeStage(1, 650, 450);

  // Stage 3: Hybrid RAG & Vector Retrieval
  await executeStage(2, 700, 450);

  // Stage 4: Multi-Agent Reasoning
  // Start running stage 4 while awaiting backend response
  stages[3].status = "running";
  onStageUpdate([...stages]);

  const liveData = await backendPromise;

  // Dynamically enrich stage detail if backend returned analyzer data
  if (liveData?.triage_info?.query_analysis?.departments?.length) {
    const dept = liveData.triage_info.query_analysis.departments[0];
    stages[3].detail = `${dept} evaluating scheme eligibility, testing requirements, fees`;
  } else if (liveData?.triage_info?.departments_matched?.length) {
    stages[3].detail = `${liveData.triage_info.departments_matched[0]} evaluating scheme eligibility and requirements`;
  }
  onStageUpdate([...stages]);

  await sleep(650);
  stages[3].status = "done";
  onStageUpdate([...stages]);
  await sleep(450);

  // Stage 5: Clause Citation & Verification
  const firstDoc = liveData?.contexts_used?.[0];
  const citationDetail = firstDoc?.is_number
    ? `Verifying clause references for ${firstDoc.is_number}`
    : "Verifying clause references and grounding";
  await executeStage(4, 600, 450, citationDetail);

  // Stage 6: Roadmap & Voice Output
  await executeStage(5, 500, 350, "Generating compliance roadmap");

  // If live backend answered, format it into MockQueryResult directly from dynamic backend
  if (liveData && liveData.answer) {
    const isNumber = liveData.is_code || fallbackResult.isCode;
    const hasClause = Boolean(liveData.clause_data);
    const clauseText = hasClause
      ? `${isNumber}, Clause-Level Grounding`
      : "No specific standard clause in local index";
    const clauseDetailText = hasClause
      ? `Real-time AI Grounding · Citing ${isNumber} directly from BIS Standards Database.`
      : "No direct standard in local database · Refer to official BIS portal for specifications.";

    // Dynamic standards from backend
    const dynamicStandards = (liveData.recommended_standards && liveData.recommended_standards.length > 0)
      ? liveData.recommended_standards
      : (liveData.contexts_used || []).map((ctx: any, idx: number) => {
          const parts = (ctx.text || "").split("|");
          const title = parts[0]?.trim() || ctx.is_number;
          const committee = parts[1]?.replace("Committee:", "")?.trim() || "";
          const stdType = parts[2]?.replace("Type:", "")?.trim() || "Standard";

          return {
            isCode: ctx.is_number || ctx.id,
            title: title,
            type: (idx === 0 ? "Mandatory" : idx === 1 ? "Related" : "Voluntary") as "Mandatory" | "Related" | "Voluntary",
            description: committee
              ? `Standard formulated by ${committee} (${stdType}).`
              : `Official Indian Standard specification (${stdType}).`,
          };
        });

    return {
      id: `live-${Date.now()}`,
      query,
      product: liveData.product || (query.length > 35 ? query.substring(0, 35) + "..." : query),
      category: liveData.category || fallbackResult.category,
      persona,
      scheme: liveData.scheme || fallbackResult.scheme,
      schemeLabel: liveData.scheme_label || fallbackResult.schemeLabel,
      schemeBadgeColor: liveData.scheme_badge_color || fallbackResult.schemeBadgeColor,
      reasons: [
        liveData.answer,
        hasClause
          ? `Retrieved from BIS database under ${liveData.category || 'Indian Standards'}.`
          : "Standard not found in local index; regulatory scheme guidance applied.",
        "Verified with cross-encoder reranking and regulatory analysis."
      ],
      agentName: liveData.agent_name || fallbackResult.agentName,
      isCode: isNumber,
      isCodeTitle: liveData.is_code_title || fallbackResult.isCodeTitle,
      clauseRef: clauseText,
      clauseDetail: clauseDetailText,
      clauseData: liveData.clause_data,
      portalUrl: liveData.portal_url || fallbackResult.portalUrl,
      portalName: liveData.portal_name || fallbackResult.portalName,
      rNumber: liveData.r_number ?? fallbackResult.rNumber,
      factoryInspection: liveData.factory_inspection ?? fallbackResult.factoryInspection,
      steps: (liveData.roadmap_steps && liveData.roadmap_steps.length > 0) ? liveData.roadmap_steps : fallbackResult.steps,
      fees: liveData.fees || fallbackResult.fees,
      labs: fallbackResult.labs,
      recommendedStandards: dynamicStandards.length > 0 ? dynamicStandards : undefined,
    };
  }

  // Otherwise return fallback
  return { ...fallbackResult, persona, query };
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function jsonStringify(obj: any): string {
  return JSON.stringify(obj);
}
