/** Reset window scroll — list→detail (Club) and route changes share one call site. */
export function scrollToTop(): void {
  if (typeof window === "undefined") return;
  window.scrollTo(0, 0);
}
