export type StandardData = {
  isCode: string;
  title: string;
  type: "Mandatory" | "Voluntary" | "Related";
  description: string;
};

export const mockStandards: Record<string, StandardData[]> = {
  "smartwatch": [
    {
      isCode: "IS 13252 (Part 1):2010",
      title: "Information Technology Equipment - Safety Requirements",
      type: "Mandatory",
      description: "Primary standard covering electrical safety, battery handling, and radiation requirements for smart wearables.",
    },
    {
      isCode: "IS 16046 (Part 2):2018",
      title: "Secondary Cells and Batteries containing Alkaline",
      type: "Mandatory",
      description: "Mandatory requirement for the lithium-ion cells used inside the smartwatch.",
    },
    {
      isCode: "IS 9000 (Part 3):1977",
      title: "Basic Environmental Testing Procedures",
      type: "Voluntary",
      description: "Recommended testing for durability, sweat resistance, and IP rating validation.",
    }
  ],
  "helmet": [
    {
      isCode: "IS 4151:2015",
      title: "Protective Helmets for Two Wheeler Riders",
      type: "Mandatory",
      description: "Primary standard ensuring impact absorption, penetration resistance, and retention system strength.",
    },
    {
      isCode: "IS 2553 (Part 2):2019",
      title: "Safety Glass - Specification",
      type: "Related",
      description: "Applies if the helmet includes a specialized visor or safety glass component.",
    }
  ],
  "default": [
    {
      isCode: "IS 1234:2024",
      title: "General Product Safety Guidelines",
      type: "Mandatory",
      description: "Mandatory requirements for the selected category based on current BIS schedules.",
    },
    {
      isCode: "IS 5678:2021",
      title: "Packaging and Labeling Standards",
      type: "Related",
      description: "Guidelines for legal metrology and packaging specifications.",
    }
  ]
};

export function getStandardsForQuery(query: string): StandardData[] {
  const lower = query.toLowerCase();
  if (lower.includes("smartwatch") || lower.includes("watch") || lower.includes("laptop") || lower.includes("bulb")) {
    return mockStandards["smartwatch"]; // Reuse for tech
  }
  if (lower.includes("helmet")) {
    return mockStandards["helmet"];
  }
  return mockStandards["default"];
}
