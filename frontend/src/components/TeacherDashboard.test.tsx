import { render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TeacherDashboard } from "./TeacherDashboard";

vi.mock("@/lib/api", () => ({
  api: {
    teacherAnalytics: () =>
      Promise.resolve({
        total_sessions: 3,
        weak_knowledge_points: ["features", "train-test"],
        note: "测试建议"
      })
  }
}));

describe("TeacherDashboard", () => {
  it("renders teacher analytics", async () => {
    render(<TeacherDashboard />);
    expect(screen.getByText("教师工作台")).toBeInTheDocument();
    await waitFor(() => expect(screen.getByText("已连接")).toBeInTheDocument());
    expect(screen.getByText("features、train-test")).toBeInTheDocument();
    expect(screen.getByText("新增资源")).toBeInTheDocument();
  });
});
