export interface ClauseData {
  id: string;
  source: string;
  title: string;
  excerpt: string;
}

export const clauseFixtures: Record<string, ClauseData> = {
  "is-13252-4.2": {
    id: "is-13252-4.2",
    source: "IS 13252 (Part 1):2010, Cl. 4.2",
    title: "Marking Requirements",
    excerpt: "Equipment shall be plainly and durably marked with the manufacturer's name or trademark, and the product model designation. For CRS registered products, the **BIS Standard Mark** and corresponding **R-Number** must be affixed as per Scheme-II guidelines.",
  },
  "is-14543-6.1": {
    id: "is-14543-6.1",
    source: "IS 14543:2016, Cl. 6.1",
    title: "Microbiological Requirements",
    excerpt: "Packaged drinking water shall be free from pathogenic microorganisms and indicator organisms. Regular sampling and testing must be performed in a **BIS-recognized internal laboratory** before dispatch.",
  },
  "is-16102-7.1": {
    id: "is-16102-7.1",
    source: "IS 16102 (Part 1):2018, Cl. 7.1",
    title: "Photobiological Safety",
    excerpt: "Self-ballasted LED lamps shall be evaluated for photobiological hazard. Products intended for general lighting must conform to **Risk Group 0 or 1** as tested by a recognized **BIS/NABL accredited laboratory**.",
  },
  "is-1417-6": {
    id: "is-1417-6",
    source: "IS 1417:2016, Section 6",
    title: "Marking (Hallmarking)",
    excerpt: "Jewellery and artefacts shall be marked with the BIS logo, fineness grade, and the **six-digit alphanumeric HUID code** issued by the Assaying and Hallmarking Centre (AHC).",
  }
};
