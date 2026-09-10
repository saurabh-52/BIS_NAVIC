# BIS NAVIC — Frontend Prototype Build Prompt (v2)
**Smart India Hackathon 2026 · Problem ID: SIH26107**
**Team: Nomadic Devs (Team ID 73869) · Theme: Smart Automation · Category: Software**

> Rewritten to be pixel-consistent with the team's pitch deck (Technical Approach, Feasibility & Viability, Impact & Benefits slides), so nothing a judge saw on the projector is missing from the live demo.

---

## ROLE
You are a 15-year full-stack engineer and repeat SIH-winning mentor. Build a complete, production-grade **frontend prototype** for BIS NAVIC — an AI-powered compliance assistant that helps MSMEs, startups, importers, and consumers navigate India's BIS certification framework (ISI Mark, CRS, Hallmarking, FMCS) without reading a single legal PDF.

This prototype will be **demoed live to judges immediately after the pitch deck**. Every number, agent name, and workflow step shown in the deck must appear, unmodified, inside the app. Consistency between slide and screen is a scoring criterion, not a nice-to-have.

---

## TECH STACK
- **Next.js 14+ (App Router)** — this also gets you the PWA-readiness your Feasibility slide already promises ("Progressive Web App (PWA) & Voice UI... low-tier mobile devices in rural areas") for near-free, via `next-pwa` / a manifest + service worker, instead of bolting a PWA onto a Vite SPA later
- Tailwind CSS
- Framer Motion (animations)
- Zustand (lightweight global state — persona, language, active query, history, theme)
- Lucide React (icons)
- Next.js file-based routing (App Router) — landing (`/`) → app shell (`/app`) → deep-linkable roadmap results (`/app/roadmap/[queryId]`) so a generated roadmap can be shared as a real URL, not just an in-memory state — a nice, cheap "wow" for judges if you demo on two devices
- Mock data + a **mock service layer** shaped exactly like the real backend contract (see "Mock Service Layer" below) so the FastAPI/LangGraph backend can be swapped in later with zero component changes

**Next.js-specific rules for whoever builds this:**
- Mark every interactive component (`QueryInput`, `AgentPipelineLog`, `RoadmapStepper`, `LabFinderPanel`, anything touching Zustand/Framer Motion/`localStorage`-free in-memory state) with `"use client"` at the top of the file. Server Components by default is fine for static shells (Navbar wrapper, page layout, footer) but everything with animation or state needs the directive or the build will error.
- Keep the Zustand store itself in a client-only module and initialize it inside a client component provider wrapper in `app/layout.tsx` — don't try to read/write store state from a Server Component.
- The mock service layer functions (`runComplianceQuery`, etc.) should be plain async functions callable from client components directly (they're mocks, not real fetches) — no need for Next.js Route Handlers/API routes unless you want to simulate real network latency, in which case wrap them in a `/app/api/*/route.ts` handler that just returns the same mock JSON after a short `setTimeout`, which also makes the later swap to a real FastAPI backend a one-line change (just repoint the fetch URL).
- Use `next/image` for any static imagery (lab logos, placeholder map) and `next/font` for Inter instead of a Google Fonts `<link>` tag, since both are already-solved problems in Next.js and skipping them just to match a generic React tutorial is wasted effort.

---

## COLOR PALETTE & BRANDING
- Primary: Deep Navy `#0A1628`
- Accent: Saffron/Orange `#F97316`
- Success: Emerald `#10B981`
- Background: `#F8FAFC`
- Card bg: `#FFFFFF`
- Danger: `#EF4444`
- Font: Inter (Google Fonts)
- Logo: compass/navigation icon + "BIS NAVIC" wordmark (matches deck slide 6 logo)
- Tagline: **"Making Indian Standards & Certification Seamless & Instant"** (use the deck's exact tagline, not a paraphrase, for slide-to-app consistency)

---

## FOLDER STRUCTURE (Next.js App Router — for engineering credibility, not just "one file")
```
app/
  layout.tsx                 root layout: fonts, Zustand provider, global toasts
  page.tsx                   Landing page ("/")
  app/
    layout.tsx                app-shell layout: Navbar + split panel frame
    page.tsx                  default/empty roadmap state ("/app")
    roadmap/[queryId]/page.tsx   deep-linkable roadmap result
  api/
    query/route.ts            optional: wraps mockAgentService with simulated latency
components/
  landing/          Hero, PersonaCards, StatsBar, ImpactStrip
  shell/             Navbar, PersonaBadge, LanguageToggle, ThemeToggle
  chat/              QueryInput, ExampleChips, VoiceButton, HistoryList     ("use client")
  pipeline/          AgentPipelineLog (animated agent trace)               ("use client")
  roadmap/           TriageCard, SchemeBadge, ISCodeCard, ClauseCitation,
                     RoadmapStepper, FeeTable, PortalLinksGrid, ExportPdfButton
  labfinder/         LabFinderPanel, LabCard, MapPlaceholder               ("use client")
  verify/            ConsumerVerifyForm, VerifyResultCard
  knowledgegraph/    ProductStandardLabGraph (small force/line graph viz)
  auth/              OtpLoginModal                                        ("use client")
  shared/            Toast, SkeletonCard, WhatsAppCTA
store/               useAppStore.ts (Zustand) + StoreProvider.tsx ("use client")
services/            mockAgentService.ts, mockData.ts
data/                isCodes.json, labs.json, fees.json, historySeed.json
i18n/                en.json, hi.json (+ stub keys for mr/ta/te)
```

---

## MOCK SERVICE LAYER (critical — do not skip)
Create `services/mockAgentService.ts` exposing one async function, `runComplianceQuery(query, persona, language)`, that **internally simulates the exact 6-stage pipeline from the architecture slide**, in this order, with these labels (must match verbatim — this is what judges will have just seen on-screen):

1. `Query & Persona Input` — capture product description, intent, persona, language
2. `Intent & Triage Classifier` — routes to the correct sub-agent (ISI / CRS / Hallmarking / FMCS / Lab Finder)
3. `Hybrid RAG & Vector Retrieval` — "searching 20,000+ IS standards in vector DB"
4. `Multi-Agent Reasoning` — the specific named agent (see below) evaluates scheme eligibility, testing requirements, fees
5. `Clause Citation & Verification` — cross-checks against BIS gazette clauses (this stage must visibly appear in the UI as "verifying clause references" — it's the source of your "100% Source-Backed" claim)
6. `Roadmap & Voice Output` — generates the final roadmap and (mock) speaks it aloud

The **agent names must match the architecture slide exactly**: `Triage Agent`, `ISI Agent`, `CRS Agent`, `Hallmark Agent`, `Lab Finder Agent` — plus `Eco Mark Agent` and `FMCS Agent` to cover the two schemes the Zone-3 box doesn't explicitly enumerate but the Scheme Classification Agent bullet requires. Do not invent generic names like "Scheme Expert," "Data Agent," or a single catch-all "Expert Agent."

> **Deck note (fix alongside the prototype, not just in code):** your deck currently contains two slightly different versions of this pipeline. The small "BIS NAVIC End-to-End Workflow" box (top-right of the Solution/Approach slide) labels step 3 as one generic "Expert Agent — ISI/CRS/Hall" and puts it *before* Hybrid RAG. The larger "Implementation Process" box (Technical Approach slide) instead has Hybrid RAG *before* the reasoning step, and your architecture + innovation slides both describe separate specialized agents rather than one generic Expert Agent. Retrieve-then-reason is the technically correct order and "specialized agents" is the stronger claim — this prompt builds it that way — so update the small workflow box on the Solution slide to match before your final run-through, or a sharp judge will catch the mismatch between your own two slides.

---

## PAGES / SCREENS

### 1. Landing Page (Hero)
- Full-width hero, animated navy-to-dark-blue gradient, subtle particle/grid background
- Headline: "Navigate BIS Certification. Instantly."
- Subhead: "AI-powered guidance for IS codes, schemes, fees & labs — in plain English or Hindi."
- 3 persona CTA cards: 🏭 Manufacturer / 📦 Importer / 👤 Consumer
- Stats bar: "20,000+ IS Standards" | "5 Certification Schemes" | "500+ Recognized Labs" | "10+ Indian Languages"
- **NEW — Impact Strip** (directly reuses the deck's Impact & Benefits numbers so the pitch and product tell the same story): "70% Faster Compliance Discovery" · "60% Less Helpdesk Load" · "100% Consumer Trust via Instant Verification" · "Zero Compliance Mistakes for Startups"
- Footer CTA: small WhatsApp icon + "Get roadmap updates on WhatsApp" (decorative — matches the deck's adoption strategy of "Simple UI + Guided Onboarding... WhatsApp integration")

### 2. OTP Login (new, matches Feasibility slide's "OTP & BIS Portal API integration")
- Lightweight modal, not a full page: mobile number → mock OTP (any 4 digits works) → success toast → routes into app shell
- Skippable with a "Continue as Guest" link so the demo never blocks

### 3. Main App Shell
Split layout — LEFT 35% chat/input, RIGHT 65% dynamic roadmap output
- Top navbar: BIS NAVIC logo | Persona badge (color-coded) | Language toggle (EN/HI/MR/TA/TE) | "New Query" | Dark mode toggle

### 4. Left Panel — Chat Input
- Persona chip: 🟠 Manufacturer / 🔵 Importer / 🟢 Consumer
- Textarea: "Describe your product or question..."
- Example chips (clickable): "I want to sell smartwatches in India" · "How do I certify LED bulbs?" · "Is my imported laptop CRS compliant?" · "Verify ISI mark on a helmet" · **"I want to hallmark gold jewellery"** (new — exercises the Hallmark Agent, which currently has zero coverage)
- "Analyze →" button (saffron, full width), Cmd+Enter shortcut
- Voice input button (decorative mic icon)
- Session history list below (see Sidebar History)

### 5. Agentic Pipeline Loader (critical wow-factor moment)
On submit, run a ~2.5s animated log using the **exact 6 stages and agent names from the Mock Service Layer section above** — not a generic "Analyzing..." spinner. Each line appears staggered, with a colored dot per stage, ending in a green "✅ Roadmap ready!" This is the moment that visually proves the multi-agent architecture from your Technical Approach slide is real, not decorative.

### 6. Right Panel — Compliance Roadmap Output

**A. Triage Result Card** (spring-in animation)
- Product detected, Category, Persona, Scheme badge — all **five** schemes named on the Scheme Classification Agent slide bullet must be selectable outcomes, not just two:
  - 🟠 SCHEME-I — ISI Mark (CM/L)
  - 🔵 SCHEME-II — CRS Registration
  - 🟡 Hallmarking (BIS Care)
  - 🟢 Eco Mark
  - 🟣 FMCS (Foreign Manufacturers Certification Scheme) — for imported goods

**B. IS Code Card + Clause Citation (NEW — this is your headline differentiator, build it properly)**
- IS Code + full title + "View Standard →"
- Directly below it, a distinct **"Verified Source"** sub-card: shows the specific clause reference (e.g. "IS 13252 (Part 1):2010, Cl. 4.2 — Marking Requirements") with a small checkmark icon and the label "Clause-Level Grounding · Cross-checked against BIS gazette." This is what turns "IS Code Card" from a static fact into proof of your "100% Source-Backed" claim.

**C. Step-by-Step Roadmap** (staggered 150ms entrance, expandable cards)
Each: step number, title, description, time badge, cost badge, portal link button.
CRS example steps: Product Classification → Lab Testing (opens Lab Finder) → Application Filing (CRSBIS) → R-Number Issuance → Product Marking.

**D. Fee Structure Card** — MSME / Large Enterprise / Importer × Application Fee / Annual Fee, "Updated: Feb 2026" tag

**E. Knowledge Graph Mini-View (NEW — matches deck's "360° Lab & Fee Mapping" innovation claim)**
- A small, simple node-link visualization: Product → Standard → Scheme → Nearest Lab. Doesn't need to be a full graph library — three-to-four connected circles with labels and animated connecting lines is enough to make the "Product-to-Standard-to-Lab mapping" claim tangible.

**F. Portal Quick Links Card** — CRSBIS, Manakonline, BIS Care App buttons

**G. Export as PDF** button (decorative, toast: "PDF exported!")

### 7. Lab Finder Modal
- Search by city/state, filter chips (NABL Accredited / BIS Recognized / Available Now)
- 3–4 mock labs (use the deck's actual named labs for Delhi: STQC Directorate ETDC, National Physical Laboratory, SGS India Pvt. Ltd., Gurgaon), each with distance, test-scope chips, turnaround time, fee range, Contact + Get Directions buttons, green "✓ BIS Recognized" badge
- Gray map placeholder with pin icons

### 8. Consumer Verification Flow
- Persona = Consumer, query = "verify product"
- Input: "Enter CM/L Number or scan QR"
- Result card: Product, Brand, IS Code, License number, Status ("✅ Valid — Expires Dec 2028"), "View on BIS Care App →"
- Add a second **Hallmark verification example** (e.g. HUID number lookup for jewellery) so all 4 schemes from the deck have live coverage, not just ISI/CRS.

### 9. Sidebar History
- Product name, scheme color dot, timestamp, "View →" to reload

### 10. Impact Dashboard tab (NEW, optional but recommended for judge Q&A)
A simple stats screen judges can click into mid-demo that mirrors the deck's Impact & Benefits slide verbatim: 70% faster compliance discovery (MSMEs), Faster Time-to-Market (Startups), 100% Consumer Trust, 60% Less Helpdesk Load (Government/BIS), Atmanirbhar Quality (Nation). Use the same three-category framing as the deck: Social / Economic / Quality & Regulatory.

---

## MOCK DATA (use exactly)

**"I want to sell smartwatches"** → IS 13252 (Part 1):2010 · CRS (Scheme-II) · crsbis.in · R-Number required · No factory inspection

**"I want to sell packaged drinking water"** → IS 14543:2016 · ISI Mark (Scheme-I) · manakonline.in · CM/L required · Factory inspection (Form V)

**"How do I certify LED bulbs?"** → IS 16102 (Part 1):2018 · CRS (Scheme-II) · crsbis.in

**"I want to hallmark gold jewellery"** (new) → IS 1417:2016 (Hallmarking of Gold) · Hallmarking Scheme · HUID-based · Assaying & Hallmarking Centre (AHC) required

**"I want an Eco Mark for my detergent"** (new — closes the 5th scheme gap; the deck's Scheme Classification Agent bullet explicitly lists ISI, CRS, Hallmarking, Eco Mark, and FMCS, but earlier mock data only covered two) → IS 4837 (Ecolabelling criteria) · Eco Mark Scheme · voluntary label, environmental compliance criteria + safety/quality baseline under relevant IS code · CPCB coordination noted

**Mock Labs (Delhi):** STQC Directorate, Electronics Test & Development Centre, Delhi · National Physical Laboratory (NPL), New Delhi · SGS India Pvt. Ltd., Gurgaon

---

## ANIMATIONS & MICRO-INTERACTIONS
- Roadmap steps stagger in, 150ms delay each
- Triage card spring/scale-in
- Scheme badge pulses once on appearance
- Clause Citation card has a subtle "verified" checkmark animation (draws attention to the grounding claim)
- Skeleton loaders while "loading"
- Lab Finder panel slides in smoothly
- Knowledge graph nodes/lines animate in sequentially after the roadmap loads

---

## RESPONSIVENESS
- Desktop-first, 1440px
- Works at 1024px (tablet)
- Mobile: panels stack vertically, agent pipeline log becomes a compact single-line ticker

---

## ADDITIONAL DETAILS
- Dark mode toggle (navy bg, lighter cards)
- Language switcher: hardcode EN/HI for 6–8 key UI strings as a live demo (nav labels, CTA button, "Analyze," scheme badges); MR/TA/TE can be present in the toggle but fall back to EN with a "Coming soon" toast — don't fake full translation
- Footer: "Powered by BIS NAVIC | Team Nomadic Devs | SIH 2026 | PS ID: SIH26107"
- Keep every number, agent name, and stage label byte-identical to what's on the pitch deck slides — this is the single highest-leverage change from v1, since judges cross-reference deck and demo in real time.

---

## WHY THESE CHANGES (for the team, not the code-gen tool)
Your deck already sells a multi-agent, clause-grounded, four-scheme, metrics-backed product. The original prototype prompt built a good generic compliance-wizard UI, but it wasn't *this specific product* — it used different agent names than your architecture diagram, only covered half your certification schemes, never surfaced the clause-level grounding you're pitching as your #1 differentiator, and never echoed the impact numbers you're asking judges to remember. This version closes every one of those gaps without changing your stack, page count, or scope — it's the same build, aimed correctly.
