export type StandardData = {
  isCode: string;
  title: string;
  type: "Mandatory" | "Voluntary" | "Related";
  description: string;
};

// Department-agnostic: No hardcoded department features.
// All standards are dynamically retrieved from the BIS database search engine.
export const mockStandards: Record<string, StandardData[]> = {};

/**
 * Returns standards for a query based on active standard data identified by the search engine.
 * If no information is found for the product, returns an empty array.
 */
export function getStandardsForQuery(
  query: string,
  activeStandard?: { isCode?: string; isCodeTitle?: string }
): StandardData[] {
  if (
    activeStandard?.isCode &&
    activeStandard.isCode !== "Unknown" &&
    !activeStandard.isCode.toLowerCase().includes("no direct match")
  ) {
    return [
      {
        isCode: activeStandard.isCode,
        title: activeStandard.isCodeTitle || "Official Indian Standard Specification",
        type: "Mandatory",
        description: `Standard identified for ${query || "queried product"}.`,
      },
    ];
  }

  // No hardcoded department fixtures — if no information is in database, return empty
  return [];
}
