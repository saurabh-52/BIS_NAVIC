export const mockQueries: Record<string, MockQueryResult> = {
  "general": {
    id: "q-general-001",
    query: "BIS Standard Inquiry",
    product: "Product Not Indexed in Database",
    category: "Bureau of Indian Standards",
    persona: "manufacturer",
    scheme: "isi",
    schemeLabel: "STANDARD INQUIRY — General BIS Framework",
    schemeBadgeColor: "#64748B",
    reasons: [
      "No specific Indian Standard matching this product is currently indexed in the local database.",
      "Please verify whether the product falls under mandatory BIS certification or voluntary standards on the official portal.",
      "You can search across all published BIS Sectional Committees at manakonline.in."
    ],
    agentName: "BIS Compliance Specialist Agent",
    isCode: "No Direct Match in Database",
    isCodeTitle: "No matching standard currently indexed in local repository",
    clauseRef: "General Quality & Safety Guidelines",
    clauseDetail: "No specific clause reference available in local index.",
    portalUrl: "https://manakonline.in",
    portalName: "Manakonline Portal",
    rNumber: false,
    factoryInspection: false,
    steps: [
      { step: 1, title: "Search Official BIS Portal", description: "Search the official BIS Standards Portal (manakonline.in) for published standards in your domain.", time: "Immediate", cost: "—", portal: "https://manakonline.in" },
      { step: 2, title: "Identify Sectional Committee", description: "Determine which BIS Division Council and Sectional Committee governs this product category.", time: "1–2 days", cost: "—", portal: "" },
      { step: 3, title: "Check Testing Lab Scope", description: "Check if BIS-recognized testing laboratories exist for testing parameters of this category.", time: "1–2 days", cost: "—", portal: "lab-finder" }
    ],
    fees: {
      msme: { application: "₹1,000", annual: "Varies" },
      large: { application: "₹1,000", annual: "Varies" },
      importer: { application: "₹1,000", annual: "Varies" }
    },
    labs: ["npl", "stqc"]
  }
};

export const mockLabs: MockLab[] = [
  {
    id: "stqc",
    name: "STQC Directorate, Electronics Test & Development Centre",
    city: "Delhi",
    state: "Delhi",
    distance: "12 km",
    nabl: true,
    bisRecognized: true,
    available: true,
    testScopes: ["IT Equipment", "Electronics", "LED", "Telecom"],
    turnaround: "3–6 weeks",
    feeRange: "₹50,000–₹2,00,000",
    contact: "+91-11-2436-3084",
    lat: 28.6139,
    lng: 77.2090
  },
  {
    id: "npl",
    name: "National Physical Laboratory (NPL)",
    city: "New Delhi",
    state: "Delhi",
    distance: "8 km",
    nabl: true,
    bisRecognized: true,
    available: true,
    testScopes: ["Physical Testing", "Chemical", "Electronics", "Material Science"],
    turnaround: "2–4 weeks",
    feeRange: "₹15,000–₹1,00,000",
    contact: "+91-11-4560-8441",
    lat: 28.6353,
    lng: 77.1722
  },
  {
    id: "sgs",
    name: "SGS India Pvt. Ltd.",
    city: "Gurgaon",
    state: "Haryana",
    distance: "22 km",
    nabl: true,
    bisRecognized: true,
    available: false,
    testScopes: ["Electronics", "Consumer Products", "Automotive", "LED", "Telecom"],
    turnaround: "4–8 weeks",
    feeRange: "₹60,000–₹2,50,000",
    contact: "+91-124-677-4100",
    lat: 28.4595,
    lng: 77.0266
  }
];

export const mockVerification = {
  isi: {
    cmlNumber: "CM/L-2345678",
    product: "Safety Helmet — Type A",
    brand: "SafeGuard India",
    isCode: "IS 2925:1984",
    licenseNumber: "CM/L-2345678",
    status: "valid" as const,
    expiry: "Dec 2028",
    manufacturer: "SafeGuard Industries Pvt. Ltd.",
    factoryAddress: "Plot 45, Industrial Area, Faridabad, Haryana"
  },
  hallmark: {
    huid: "AB12CD",
    product: "22K Gold Necklace",
    brand: "Tanishq",
    isCode: "IS 1417:2016",
    purity: "22K (916)",
    status: "valid" as const,
    jeweller: "Titan Company Ltd.",
    ahc: "Government of India Mint, Mumbai",
    stampDate: "15 Aug 2025"
  }
};

export const mockHistory: HistoryItem[] = [
  { id: "h1", query: "BIS Product Certification Process", scheme: "isi", timestamp: "2 hours ago", queryKey: "general" },
  { id: "h2", query: "Indian Standards Verification Guidelines", scheme: "crs", timestamp: "5 hours ago", queryKey: "general" },
  { id: "h3", query: "Standard Mark Licensing Procedure", scheme: "isi", timestamp: "1 day ago", queryKey: "general" }
];

// Types
export interface MockQueryResult {
  id: string;
  query: string;
  product: string;
  category: string;
  persona: string;
  scheme: string;
  schemeLabel: string;
  schemeBadgeColor: string;
  reasons: string[];
  agentName: string;
  isCode: string;
  isCodeTitle: string;
  clauseRef: string;
  clauseDetail: string;
  clauseFixtureId?: string;
  clauseData?: {
    id: string;
    source: string;
    title: string;
    excerpt: string;
  };
  portalUrl: string;
  portalName: string;
  rNumber: boolean;
  factoryInspection: boolean;
  steps: RoadmapStep[];
  fees: FeeStructure;
  labs: string[];
  recommendedStandards?: {
    isCode: string;
    title: string;
    type: "Mandatory" | "Voluntary" | "Related";
    description: string;
  }[];
}

export interface RoadmapStep {
  step: number;
  title: string;
  description: string;
  time: string;
  cost: string;
  portal: string;
}

export interface FeeStructure {
  msme: { application: string; annual: string };
  large: { application: string; annual: string };
  importer: { application: string; annual: string };
}

export interface MockLab {
  id: string;
  name: string;
  city: string;
  state: string;
  distance: string;
  nabl: boolean;
  bisRecognized: boolean;
  available: boolean;
  testScopes: string[];
  turnaround: string;
  feeRange: string;
  contact: string;
  lat: number;
  lng: number;
}

export interface HistoryItem {
  id: string;
  query: string;
  scheme: string;
  timestamp: string;
  queryKey: string;
}

export interface PipelineStage {
  id: number;
  label: string;
  detail: string;
  status: "pending" | "running" | "done";
  agentName?: string;
}
