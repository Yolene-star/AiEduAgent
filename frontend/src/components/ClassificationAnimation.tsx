"use client";

import { AnimationResponse } from "@/lib/api";

type Props = {
  animation: AnimationResponse | null;
  currentStep: number;
  onStepChange: (step: number) => void;
};

export function ClassificationAnimation({ animation, currentStep, onStepChange }: Props) {
  if (!animation) {
    return null;
  }

  const step = animation.steps[currentStep] ?? animation.steps[0];

  return (
    <section className="animation-panel" aria-label="分类与特征动画">
      <div className="animation-stage">
        <div className="object-card">
          <span className="object-dot" />
          <strong>{step.category}</strong>
          <p>{step.highlighted_features.join(" / ")}</p>
        </div>
      </div>
      <div>
        <h2>{step.title}</h2>
        <p>{step.narration}</p>
        <div className="animation-controls">
          <button onClick={() => onStepChange(Math.max(0, currentStep - 1))}>上一步</button>
          <button onClick={() => onStepChange((currentStep + 1) % animation.steps.length)}>下一步</button>
          <button onClick={() => onStepChange(0)}>重播</button>
        </div>
      </div>
    </section>
  );
}
