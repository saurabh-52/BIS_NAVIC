export const mockQueries: Record<string, MockQueryResult> = {
  "smartwatch": {
    id: "q-smartwatch-001",
    query: "I want to sell smartwatches in India",
    product: "Smartwatch / Wearable Electronics",
    category: "Electronics — IT & AV Equipment",
    persona: "manufacturer",
    scheme: "crs",
    schemeLabel: "SCHEME-II — CRS Registration",
    schemeBadgeColor: "#3B82F6",
    reasons: [
      "Product is categorized as 'IT Equipment' under electronics.",
      "Requires compulsory registration (CRS) rather than full ISI certification.",
      "Self-declaration of conformity to IS 13252 is applicable."
    ],
    agentName: "CRS Agent",
    isCode: "IS 13252 (Part 1):2010",
    isCodeTitle: "Information Technology Equipment — Safety — Part 1: General Requirements",
    clauseRef: "IS 13252 (Part 1):2010, Cl. 4.2 — Marking Requirements",
    clauseDetail: "Clause-Level Grounding · Cross-checked against BIS gazette.",
    clauseFixtureId: "is-13252-4.2",
    portalUrl: "https://crsbis.in",
    portalName: "CRSBIS",
    rNumber: true,
    factoryInspection: false,
    steps: [
      { step: 1, title: "Product Classification", description: "Identify your product under the relevant IS standard and CRS schedule entry. Smartwatches fall under IT equipment (IS 13252).", time: "1–2 days", cost: "—", portal: "" },
      { step: 2, title: "Lab Testing", description: "Submit product samples to a BIS-recognized lab for testing against IS 13252 (Part 1). Get test reports for safety compliance.", time: "3–6 weeks", cost: "₹50,000–₹1,50,000", portal: "lab-finder" },
      { step: 3, title: "Application Filing", description: "Register on crsbis.in portal and file CRS application with test reports, product details, and manufacturer information.", time: "1–2 days", cost: "₹1,000", portal: "https://crsbis.in" },
      { step: 4, title: "R-Number Issuance", description: "Upon successful verification, BIS issues a unique R-Number (Registration Number) for your product model.", time: "2–4 weeks", cost: "—", portal: "" },
      { step: 5, title: "Product Marking", description: "Affix the BIS Standard Mark with R-Number on your product, packaging, and documentation before sale in India.", time: "1 day", cost: "—", portal: "" }
    ],
    fees: {
      msme: { application: "₹1,000", annual: "₹2,000" },
      large: { application: "₹1,000", annual: "₹5,000" },
      importer: { application: "₹1,000", annual: "₹10,000" }
    },
    labs: ["stqc", "npl", "sgs"]
  },
  "water": {
    id: "q-water-001",
    query: "I want to sell packaged drinking water",
    product: "Packaged Drinking Water",
    category: "Food & Beverages — Packaged Water",
    persona: "manufacturer",
    scheme: "isi",
    schemeLabel: "SCHEME-I — ISI Mark (CM/L)",
    schemeBadgeColor: "#F97316",
    reasons: [
      "Product falls under Food & Beverages mandatory certification.",
      "Requires factory infrastructure audit and continuous monitoring.",
      "Public health and safety product category."
    ],
    agentName: "ISI Agent",
    isCode: "IS 14543:2016",
    isCodeTitle: "Packaged Drinking Water (Other Than Packaged Natural Mineral Water) — Specification",
    clauseRef: "IS 14543:2016, Cl. 6.1 — Microbiological Requirements",
    clauseDetail: "Clause-Level Grounding · Cross-checked against BIS gazette.",
    clauseFixtureId: "is-14543-6.1",
    portalUrl: "https://manakonline.in",
    portalName: "Manakonline",
    rNumber: false,
    factoryInspection: true,
    steps: [
      { step: 1, title: "Product Classification", description: "Your product falls under mandatory ISI Mark certification. Packaged drinking water requires IS 14543:2016 compliance.", time: "1 day", cost: "—", portal: "" },
      { step: 2, title: "Factory Infrastructure", description: "Ensure your manufacturing facility meets BIS factory requirements including testing lab, quality control systems.", time: "2–4 weeks", cost: "Varies", portal: "" },
      { step: 3, title: "Lab Testing", description: "Get water samples tested at BIS-recognized labs for chemical, microbiological, and physical parameters per IS 14543.", time: "2–3 weeks", cost: "₹15,000–₹30,000", portal: "lab-finder" },
      { step: 4, title: "Application Filing (Form V)", description: "Apply on manakonline.in with test reports, factory layout, process flow, and Form V for ISI Mark license.", time: "1–2 days", cost: "₹1,000", portal: "https://manakonline.in" },
      { step: 5, title: "Factory Inspection", description: "BIS officer conducts on-site factory inspection to verify compliance with IS standards and quality systems.", time: "4–8 weeks", cost: "—", portal: "" },
      { step: 6, title: "CM/L Issuance", description: "Upon successful inspection, BIS issues Certificate of Marking License (CM/L) to use ISI Mark on your product.", time: "1–2 weeks", cost: "—", portal: "" }
    ],
    fees: {
      msme: { application: "₹1,000", annual: "₹2,000" },
      large: { application: "₹1,000", annual: "₹10,000" },
      importer: { application: "N/A", annual: "N/A" }
    },
    labs: ["npl", "sgs"]
  },
  "led": {
    id: "q-led-001",
    query: "How do I certify LED bulbs?",
    product: "LED Bulbs / LED Luminaires",
    category: "Electronics — Lighting Equipment",
    persona: "manufacturer",
    scheme: "crs",
    schemeLabel: "SCHEME-II — CRS Registration",
    schemeBadgeColor: "#3B82F6",
    reasons: [
      "Product is a lighting electronic component.",
      "Must undergo photobiological safety testing.",
      "Regulated under CRS Scheme-II for consumer safety."
    ],
    agentName: "CRS Agent",
    isCode: "IS 16102 (Part 1):2018",
    isCodeTitle: "Self-Ballasted LED Lamps for General Lighting Services — Safety Requirements",
    clauseRef: "IS 16102 (Part 1):2018, Cl. 7.1 — Photobiological Safety Classification",
    clauseDetail: "Clause-Level Grounding · Cross-checked against BIS gazette.",
    clauseFixtureId: "is-16102-7.1",
    portalUrl: "https://crsbis.in",
    portalName: "CRSBIS",
    rNumber: true,
    factoryInspection: false,
    steps: [
      { step: 1, title: "Product Classification", description: "LED bulbs fall under CRS mandatory registration. Identify specific type (self-ballasted, tube, luminaire) for correct IS standard.", time: "1 day", cost: "—", portal: "" },
      { step: 2, title: "Lab Testing", description: "Submit LED samples to a BIS-recognized lab for testing against IS 16102 safety and performance parameters.", time: "4–6 weeks", cost: "₹40,000–₹1,00,000", portal: "lab-finder" },
      { step: 3, title: "Application Filing", description: "File CRS registration on crsbis.in with test reports and product specifications.", time: "1–2 days", cost: "₹1,000", portal: "https://crsbis.in" },
      { step: 4, title: "R-Number Issuance", description: "BIS issues R-Number for your LED product model upon verification.", time: "2–4 weeks", cost: "—", portal: "" },
      { step: 5, title: "Product Marking", description: "Mark products with BIS Standard Mark and R-Number before retail distribution.", time: "1 day", cost: "—", portal: "" }
    ],
    fees: {
      msme: { application: "₹1,000", annual: "₹2,000" },
      large: { application: "₹1,000", annual: "₹5,000" },
      importer: { application: "₹1,000", annual: "₹10,000" }
    },
    labs: ["stqc", "npl", "sgs"]
  },
  "gold": {
    id: "q-gold-001",
    query: "I want to hallmark gold jewellery",
    product: "Gold Jewellery / Gold Artifacts",
    category: "Precious Metals — Gold Hallmarking",
    persona: "manufacturer",
    scheme: "hallmark",
    schemeLabel: "Hallmarking Scheme",
    schemeBadgeColor: "#EAB308",
    reasons: [
      "Product is precious metal (Gold jewellery).",
      "Requires unique HUID laser engraving.",
      "Purity verification is mandatory."
    ],
    agentName: "Hallmark Agent",
    isCode: "IS 1417:2016",
    isCodeTitle: "Gold and Gold Alloys — Jewellery/Artefacts — Fineness and Marking",
    clauseRef: "IS 1417:2016, Cl. 5.2 — Hallmark Components (BIS Mark, Purity, AHC Mark, HUID)",
    clauseDetail: "Clause-Level Grounding · Cross-checked against BIS gazette.",
    clauseFixtureId: "is-1417-6",
    portalUrl: "https://bis.gov.in",
    portalName: "BIS Care",
    rNumber: false,
    factoryInspection: false,
    steps: [
      { step: 1, title: "Jeweller Registration", description: "Register as a BIS-certified jeweller on the BIS portal. Mandatory for all jewellers selling hallmarked gold.", time: "1–2 days", cost: "₹1 lakh (refundable deposit)", portal: "https://bis.gov.in" },
      { step: 2, title: "Submit Articles to AHC", description: "Submit gold jewellery articles to a BIS-recognized Assaying & Hallmarking Centre (AHC) for purity testing.", time: "1–3 days", cost: "₹35–₹45 per article", portal: "" },
      { step: 3, title: "Purity Testing & Assaying", description: "AHC tests gold purity using XRF or fire assay method as per IS 1417:2016. Tests for 14K, 18K, 20K, 22K, 24K.", time: "1–2 days", cost: "Included in AHC fee", portal: "" },
      { step: 4, title: "HUID Stamping", description: "Upon passing purity test, each article gets a unique 6-digit alphanumeric HUID (Hallmark Unique Identification) stamped.", time: "Same day", cost: "—", portal: "" },
      { step: 5, title: "Hallmark Verification", description: "Consumers can verify HUID via BIS Care app or website to confirm purity, jeweller details, and AHC information.", time: "Instant", cost: "Free", portal: "https://bis.gov.in" }
    ],
    fees: {
      msme: { application: "₹1 lakh (deposit)", annual: "—" },
      large: { application: "₹1 lakh (deposit)", annual: "—" },
      importer: { application: "N/A", annual: "N/A" }
    },
    labs: []
  },
  "ecomark": {
    id: "q-eco-001",
    query: "I want an Eco Mark for my detergent",
    product: "Detergent / Cleaning Products",
    category: "Chemicals — Environmental Labelling",
    persona: "manufacturer",
    scheme: "ecomark",
    schemeLabel: "Eco Mark Scheme",
    schemeBadgeColor: "#10B981",
    reasons: [
      "Product claims environmental friendliness.",
      "Requires testing against both safety and ecological criteria.",
      "Voluntary certification but provides market advantage."
    ],
    agentName: "Eco Mark Agent",
    isCode: "IS 4837",
    isCodeTitle: "Ecolabelling Criteria for Soaps and Detergents",
    clauseRef: "IS 4837, Cl. 3.1 — Biodegradability & Phosphate Limits",
    clauseDetail: "Clause-Level Grounding · Cross-checked against BIS gazette.",
    portalUrl: "https://bis.gov.in",
    portalName: "BIS Portal",
    rNumber: false,
    factoryInspection: true,
    steps: [
      { step: 1, title: "Product Classification", description: "Identify your product under relevant Eco Mark criteria. Detergents must meet IS 4837 environmental benchmarks.", time: "1 day", cost: "—", portal: "" },
      { step: 2, title: "Environmental Compliance", description: "Ensure product meets biodegradability, phosphate limits, and CPCB environmental standards for Eco Mark eligibility.", time: "2–4 weeks", cost: "Varies", portal: "" },
      { step: 3, title: "Lab Testing", description: "Get products tested at recognized lab for environmental parameters — biodegradability, toxicity, packaging recyclability.", time: "3–4 weeks", cost: "₹20,000–₹50,000", portal: "lab-finder" },
      { step: 4, title: "Application Filing", description: "Submit Eco Mark application to BIS with test reports, environmental compliance docs, and product specifications.", time: "1–2 days", cost: "₹1,000", portal: "https://bis.gov.in" },
      { step: 5, title: "Factory Inspection & CPCB Coordination", description: "BIS may coordinate with CPCB for factory environmental audit. Voluntary scheme but adds significant market credibility.", time: "4–8 weeks", cost: "—", portal: "" },
      { step: 6, title: "Eco Mark Certification", description: "Upon approval, authorized to use Eco Mark earthen pot symbol on product packaging. Renewable annually.", time: "2–4 weeks", cost: "—", portal: "" }
    ],
    fees: {
      msme: { application: "₹1,000", annual: "₹2,000" },
      large: { application: "₹1,000", annual: "₹5,000" },
      importer: { application: "N/A", annual: "N/A" }
    },
    labs: ["npl"]
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
  { id: "h1", query: "Sell smartwatches in India", scheme: "crs", timestamp: "2 hours ago", queryKey: "smartwatch" },
  { id: "h2", query: "Certify LED bulbs", scheme: "crs", timestamp: "5 hours ago", queryKey: "led" },
  { id: "h3", query: "Packaged drinking water", scheme: "isi", timestamp: "1 day ago", queryKey: "water" },
  { id: "h4", query: "Hallmark gold jewellery", scheme: "hallmark", timestamp: "2 days ago", queryKey: "gold" }
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
  portalUrl: string;
  portalName: string;
  rNumber: boolean;
  factoryInspection: boolean;
  steps: RoadmapStep[];
  fees: FeeStructure;
  labs: string[];
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
