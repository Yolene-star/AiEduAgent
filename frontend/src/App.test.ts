import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import App from './App.vue'

async function flushPromises() {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('App', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('submits the selected stage and message, then renders the fake answer', async () => {
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockImplementation(async (input) => {
      const url = String(input)
      if (url.includes('/api/v1/quizzes')) {
        return new Response(JSON.stringify([]), { status: 200, headers: { 'content-type': 'application/json' } })
      }
      if (url.includes('/api/v1/multimodal/animation')) {
        return new Response(
          JSON.stringify({
            id: 'anim-u1-image-classification',
            title: '图像分类五步动画',
            concept_id: 'U1-C04',
            template: 'image_classification_process',
            version: 1,
            subtitle: '动画字幕',
            steps: [
              { id: 'image_input', title: '图片进入', caption: '图片进入模型。', visual: 'image-card' },
              { id: 'pixel_grid', title: '像素网格', caption: '图片变成像素。', visual: 'pixel-grid' },
              { id: 'feature_hint', title: '寻找线索', caption: '模型寻找线索。', visual: 'feature-lines' },
              { id: 'class_scores', title: '类别分数', caption: '模型计算分数。', visual: 'score-bars' },
              { id: 'final_label', title: '输出标签', caption: '输出预测标签。', visual: 'label-badge' }
            ],
            allowed_controls: ['play', 'pause', 'restart', 'previous', 'next'],
            license: 'self-authored-demo-assets'
          }),
          { status: 200, headers: { 'content-type': 'application/json' } }
        )
      }
      if (url.includes('/api/v1/multimodal/storybook')) {
        return new Response(
          JSON.stringify({
            id: 'storybook-u1-lower-primary',
            title: '小智学会看图片',
            stage: 'lower_primary',
            concept_id: 'U1-C04',
            version: 1,
            recommended_by_default: true,
            pages: Array.from({ length: 6 }, (_, index) => ({
              page: index + 1,
              title: `第${index + 1}页`,
              image: `/assets/storybook/u1-page-0${index + 1}.svg`,
              alt: '绘本图片',
              narration: '旁白',
              dialogue: '台词',
              question: '问题？'
            })),
            license: 'self-authored-demo-assets'
          }),
          { status: 200, headers: { 'content-type': 'application/json' } }
        )
      }
      return Promise.resolve(
        new Response(
          JSON.stringify({
            answer: '它会从许多带有名字的小猫图片中学习共同特点。',
            check_question: '图片旁边写着‘小猫’，这个名字在训练中叫什么？',
            used_card_ids: ['U1-C02', 'U1-C04'],
            next_actions: ['answer_check', 'open_storybook'],
            sources: [
              {
                card_id: 'U1-C02',
                title: 'Google Supervised Learning',
                url: 'https://developers.google.com/machine-learning/intro-to-ml/supervised'
              }
            ],
            lesson_state: 'WELCOME',
            next_lesson_state: 'DIAGNOSE',
            teaching_form: 'storybook',
            stage_policy_label: '小学低年级',
            format_warnings: []
          }),
          { status: 200, headers: { 'content-type': 'application/json' } }
        )
      )
    })

    const wrapper = mount(App)
    await flushPromises()
    await wrapper.find('select').setValue('middle_school')
    await flushPromises()
    await wrapper.find('textarea').setValue('AI怎么认识小猫？')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/chat',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ stage: 'middle_school', message: 'AI怎么认识小猫？' })
      })
    )
    expect(wrapper.text()).toContain('它会从许多带有名字的小猫图片中学习共同特点。')
    expect(wrapper.text()).toContain('U1-C02')
    expect(wrapper.text()).toContain('Google Supervised Learning')
  })

  it('shows a readable error when the backend request fails', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('后端未启动'))

    const wrapper = mount(App)
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('后端未启动')
  })
})
