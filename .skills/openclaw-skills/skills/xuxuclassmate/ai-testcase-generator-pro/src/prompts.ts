/**
 * Prompt templates for test case generation stages.
 * These are internal templates used by the skill.
 */

import { TestStage, Language } from "./types";

export interface StagePrompt {
  name: { zh: string; en: string };
  description: { zh: string; en: string };
  focus: { zh: string[]; en: string[] };
}

export const STAGE_PROMPTS: Record<TestStage, StagePrompt> = {
  requirement: {
    name: {
      zh: "需求评审阶段",
      en: "Requirement Review Stage",
    },
    description: {
      zh: "聚焦需求完整性、流程清晰度和边界条件覆盖",
      en: "Focus on requirement completeness, process clarity, and boundary coverage",
    },
    focus: {
      zh: [
        "需求是否完整明确",
        "流程是否清晰（主流程/分支/异常）",
        "边界条件是否覆盖",
        "权限是否明确",
        "是否有非功能需求",
      ],
      en: [
        "Requirements are complete and unambiguous",
        "Flows are clear (happy path / branches / error paths)",
        "Boundary conditions are covered",
        "Permissions and roles are defined",
        "Non-functional requirements are addressed",
      ],
    },
  },

  development: {
    name: {
      zh: "开发提测阶段",
      en: "Development Handoff Stage",
    },
    description: {
      zh: "覆盖功能、UI、安全、兼容性和易用性",
      en: "Cover functionality, UI, security, compatibility, and usability",
    },
    focus: {
      zh: [
        "功能是否符合需求",
        "UI 是否符合设计",
        "安全性测试（注入、XSS、CSRF）",
        "兼容性测试（浏览器、设备）",
        "易用性测试",
      ],
      en: [
        "Functionality matches requirements",
        "UI matches design specs",
        "Security tests (injection, XSS, CSRF)",
        "Compatibility tests (browsers, devices)",
        "Usability tests",
      ],
    },
  },

  prerelease: {
    name: {
      zh: "发布前验证阶段",
      en: "Pre-release Verification Stage",
    },
    description: {
      zh: "回归测试、性能验证和生产就绪检查",
      en: "Regression testing, performance validation, and production readiness",
    },
    focus: {
      zh: [
        "回归测试覆盖",
        "性能边界测试",
        "安全漏洞扫描",
        "监控和日志就绪",
        "回滚方案验证",
      ],
      en: [
        "Regression test coverage",
        "Performance boundary tests",
        "Security vulnerability scans",
        "Monitoring and logging readiness",
        "Rollback plan validation",
      ],
    },
  },
};

export const REVIEWER_INSTRUCTIONS = {
  testManager: "Review test cases for coverage and executability. Score 0-100.",
  devManager: "Review test cases for technical feasibility and security. Score 0-100.",
  productManager: "Review test cases for business logic and user experience. Score 0-100.",
};
