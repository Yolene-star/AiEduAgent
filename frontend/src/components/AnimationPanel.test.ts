import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import AnimationPanel from './AnimationPanel.vue'

async function flushPromises() {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('AnimationPanel', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('loads the whitelisted animation spec and steps forward manually', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(
        JSON.stringify({
          id: 'anim-u1-image-classification',
          title: '图像分类五步动画',
          concept_id: 'U1-C04',
          template: 'image_classification_process',
          version: 1,
          subtitle: '从图片到标签',
          steps: [
            { id: 'image_input', title: '图片进入', caption: '先把图片交给模型。', visual: 'image-card' },
            { id: 'pixel_grid', title: '像素网格', caption: '图片变成小格子。', visual: 'pixel-grid' },
            { id: 'feature_hint', title: '寻找线索', caption: '寻找边缘和颜色。', visual: 'feature-lines' },
            { id: 'class_scores', title: '类别分数', caption: '计算类别可能性。', visual: 'score-bars' },
            { id: 'final_label', title: '输出标签', caption: '输出预测标签。', visual: 'label-badge' }
          ],
          allowed_controls: ['play', 'pause', 'restart', 'previous', 'next'],
          license: 'self-authored-demo-assets'
        }),
        { status: 200, headers: { 'content-type': 'application/json' } }
      )
    )

    const wrapper = mount(AnimationPanel)
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('图片进入')
    await wrapper.findAll('button').find((button) => button.text() === '下一步')?.trigger('click')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('像素网格')
    expect(wrapper.find('.animation-stage').attributes('data-visual')).toBe('pixel-grid')
  })
})
