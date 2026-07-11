import { expect, test } from "@playwright/test";

test("student can see MVP learning workflow controls", async ({ page }) => {
  await page.route("**/health", async (route) => {
    await route.fulfill({
      json: { status: "ok", service: "AiEduAgent", version: "0.1.0" }
    });
  });
  await page.route("**/api/students/session", async (route) => {
    await route.fulfill({
      json: {
        session_id: "e2e-session",
        stage: "upper_primary",
        stage_label: "小学高年级",
        welcome_message: "你好，小学高年级同学。"
      }
    });
  });
  await page.route("**/api/courses?stage=upper_primary", async (route) => {
    await route.fulfill({
      json: {
        id: "ai-classification",
        title: "人工智能如何学会分类",
        summary: "用分类任务理解数据。",
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
      }
    });
  });
  await page.route("**/api/tts/loopback-test", async (route) => {
    await route.fulfill({ json: { passed: true, similarity: 1, notes: [] } });
  });
  await page.route("**/api/animations/classification", async (route) => {
    await route.fulfill({
      json: {
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
      }
    });
  });
  await page.route("**/api/code/run", async (route) => {
    await route.fulfill({
      json: {
        status: "ok",
        output: "hello",
        feedback: "代码运行成功。",
        sandbox: "mock-judge0"
      }
    });
  });

  await page.goto("/");
  await expect(page.getByText("AiEduAgent")).toBeVisible();
  await page.getByRole("button", { name: "小学高年级" }).click();
  await expect(page.getByText("人工智能如何学会分类")).toBeVisible();
  await expect(page.getByText(/TTS 回环通过/)).toBeVisible();
  await expect(page.getByRole("button", { name: "播放语音" })).toBeVisible();
  await page.getByRole("button", { name: "动画讲解" }).click();
  await expect(page.getByText("观察对象")).toBeVisible();
  await page.getByRole("button", { name: "运行代码" }).click();
  await expect(page.getByText(/代码运行成功/)).toBeVisible();
});

test("teacher can see analytics dashboard", async ({ page }) => {
  await page.route("**/api/teacher/analytics", async (route) => {
    await route.fulfill({
      json: {
        total_sessions: 2,
        weak_knowledge_points: ["features"],
        note: "SQLite-backed analytics"
      }
    });
  });

  await page.goto("/teacher");
  await expect(page.getByText("教师工作台")).toBeVisible();
  await expect(page.getByText("features")).toBeVisible();
  await expect(page.getByRole("button", { name: "新增资源" })).toBeVisible();
});
