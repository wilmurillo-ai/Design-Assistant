import type { RecipeFrontmatter } from "./recipe-frontmatter";

export type RecipeLintIssue = { level: "warn" | "error"; code: string; message: string };

/**
 * Lightweight recipe lint for common scaffolding pitfalls.
 * Intentionally conservative: warnings should be actionable and low-noise.
 */
export function lintRecipe(recipe: RecipeFrontmatter): RecipeLintIssue[] {
  const issues: RecipeLintIssue[] = [];

  if ((recipe.kind ?? "") === "team") {
    const agents = recipe.agents ?? [];
    const files = recipe.files ?? [];
    const templates = recipe.templates ?? {};

    if (agents.length && files.length === 0) {
      const hasRoleTemplates = Object.keys(templates).some((k) => k.includes(".") && /(\.soul|\.agents|\.tools|\.status|\.notes)$/.test(k));
      issues.push({
        level: "warn",
        code: "team.missing_files",
        message:
          `Team recipe has agents[] but no files[]. Per-role workspaces will be empty. ` +
          `Add a files: section (e.g. SOUL.md/AGENTS.md/TOOLS.md/STATUS.md/NOTES.md) ` +
          `or rely on scaffold defaults. ${hasRoleTemplates ? "(Detected role templates; likely meant to scaffold role files.)" : ""}`,
      });
    }

    // Templates exist but won't be used if files[] doesn't reference them.
    if (agents.length && Object.keys(templates).length && files.length) {
      const baseTemplates = new Set(files.map((f) => String(f.template ?? "").trim()).filter(Boolean));
      const missing = ["soul", "agents", "tools"].filter((t) => !baseTemplates.has(t) && ![...baseTemplates].some((x) => x.endsWith(`.${t}`)));
      if (missing.length) {
        issues.push({
          level: "warn",
          code: "team.files.missing_core_templates",
          message: `Team recipe files[] is missing some common templates (${missing.join(", ")}). This may be intentional, but usually each role should have SOUL.md/AGENTS.md/TOOLS.md at minimum.`,
        });
      }
    }
  }

  return issues;
}
