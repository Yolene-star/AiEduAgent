import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { ClassificationAnimation } from "./ClassificationAnimation";

const animation = {
  id: "classification-features",
  title: "分类与特征动画",
  reference: "test",
  steps: [
    {
      id: "observe",
      title: "观察对象",
      narration: "先观察线索。",
      highlighted_features: ["颜色", "耳朵"],
      category: "待判断"
    },
    {
      id: "classify",
      title: "完成分类",
      narration: "根据线索分类。",
      highlighted_features: ["规则"],
      category: "分类完成"
    }
  ]
};

describe("ClassificationAnimation", () => {
  it("renders progress and advances steps", () => {
    const onStepChange = vi.fn();
    render(<ClassificationAnimation animation={animation} currentStep={0} onStepChange={onStepChange} />);
    expect(screen.getByText("第 1 / 2 步")).toBeInTheDocument();
    expect(screen.getByText("颜色")).toBeInTheDocument();
    fireEvent.click(screen.getByText("下一步"));
    expect(onStepChange).toHaveBeenCalledWith(1);
  });
});
