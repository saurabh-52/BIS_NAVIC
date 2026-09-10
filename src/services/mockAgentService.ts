import { mockQueries, MockQueryResult, PipelineStage } from './mockData';

/**
 * Mock Agent Service — simulates the exact 6-stage pipeline from the architecture slide.
 * Pipeline stages and agent names match the pitch deck verbatim.
 */

// Maps query text to a mock data key using keyword matching
function resolveQueryKey(query: string): string {
  const q = query.toLowerCase();
  if (q.includes('smartwatch') || q.includes('smart watch') || q.includes('wearable')) return 'smartwatch';
  if (q.includes('water') || q.includes('drinking') || q.includes('packaged')) return 'water';
  if (q.includes('led') || q.includes('bulb') || q.includes('lamp') || q.includes('light')) return 'led';
  if (q.includes('gold') || q.includes('jewel') || q.includes('hallmark')) return 'gold';
  if (q.includes('eco') || q.includes('detergent') || q.includes('soap') || q.includes('clean')) return 'ecomark';
  if (q.includes('laptop') || q.includes('computer') || q.includes('import')) return 'smartwatch'; // fallback to CRS
  if (q.includes('helmet') || q.includes('verify') || q.includes('isi mark')) return 'water'; // ISI verification
  // Default fallback
  return 'smartwatch';
}

// Returns the 6 pipeline stages with correct labels from the deck
function buildPipelineStages(agentName: string): PipelineStage[] {
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

/**
 * Main entrypoint — runComplianceQuery
 * Simulates the 6-stage agentic pipeline with staggered timing.
 * Returns stages via callback for animated UI rendering.
 */
export async function runComplianceQuery(
  query: string,
  persona: string,
  language: string,
  onStageUpdate: (stages: PipelineStage[]) => void
): Promise<MockQueryResult> {
  const queryKey = resolveQueryKey(query);
  const result = mockQueries[queryKey];

  if (!result) {
    throw new Error(`No mock data found for query: ${query}`);
  }

  const stages = buildPipelineStages(result.agentName);

  // Simulate staggered pipeline execution (~2.5s total)
  const delays = [300, 400, 600, 500, 400, 300]; // ms per stage

  for (let i = 0; i < stages.length; i++) {
    // Mark current stage as running
    stages[i].status = "running";
    onStageUpdate([...stages]);

    await sleep(delays[i]);

    // Mark stage as done
    stages[i].status = "done";
    onStageUpdate([...stages]);
  }

  return { ...result, persona };
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
