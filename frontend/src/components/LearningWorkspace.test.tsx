import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { LearningWorkspace } from "./LearningWorkspace";

vi.mock("@/lib/api", () => ({
  api: {
    health: () => Promise.resolve({ service: "AiEduAgent", version: "0.1.0", status: "ok" }),
    createSession: () =>
      Promise.resolve({
        session_id: "test-session",
        stage: "upper_primary",
        stage_label: "小学高年级",
        welcome_message: "你好，小学高年级同学。"
      }),
    course: () =>
      Promise.resolve({
        id: "ai-classification",
        title: "人工智能如何学会分类",
        summary: "测试课程",
        stage: "upper_primary",
        knowledge_points: [
          {
            id: "classification",
            title: "什么是分类",
            order: 1,
            prerequisites: [],
            goal: "理解分类",
            intro: "分类是按特征分组。"
          }
        ]
      }),
    ttsLoopback: () => Promise.resolve({ passed: true, similarity: 1, notes: [] }),
    animation: () =>
      Promise.resolve({
        id: "classification-features",
        title: "分类与特征动画",
        reference: "test",
        steps: [
          {
            id: "observe",
            title: "观察对象",
            narration: "先观察线索。",
            highlighted_features: ["颜色"],
            category: "待判断"
          }
        ]
      })
  }
}));

describe("LearningWorkspace", () => {
  it("renders product shell and stage choices", () => {
    render(<LearningWorkspace />);
    expect(screen.getByText("AiEduAgent")).toBeInTheDocument();
    expect(screen.getByText("小学低年级")).toBeInTheDocument();
    expect(screen.getByText("高中")).toBeInTheDocument();
    expect(screen.getByLabelText("输入问题")).toBeInTheDocument();
    expect(screen.getByText("动画讲解")).toBeInTheDocument();
    expect(screen.getByText("播放语音")).toBeInTheDocument();
  });
});
