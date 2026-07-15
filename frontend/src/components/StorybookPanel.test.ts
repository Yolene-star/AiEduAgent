import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import StorybookPanel from './StorybookPanel.vue'

async function flushPromises() {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

function storybookPayload() {
  return {
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
      alt: `第${index + 1}页替代文本`,
      narration: `第${index + 1}页旁白`,
      dialogue: `第${index + 1}页台词`,
      question: `第${index + 1}页问题？`
    })),
    license: 'self-authored-demo-assets'
  }
}

describe('StorybookPanel', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('opens by default for lower primary and moves through six pages', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(storybookPayload()), {
        status: 200,
        headers: { 'content-type': 'application/json' }
      })
    )

    const wrapper = mount(StorybookPanel, { props: { stage: 'lower_primary' } })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('第1页旁白')
    await wrapper.findAll('button').find((button) => button.text() === '下一页')?.trigger('click')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('第2页旁白')
  })

  it('shows a text fallback when an image fails', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(storybookPayload()), {
        status: 200,
        headers: { 'content-type': 'application/json' }
      })
    )

    const wrapper = mount(StorybookPanel, { props: { stage: 'lower_primary' } })
    await flushPromises()
    await wrapper.vm.$nextTick()
    await wrapper.find('img').trigger('error')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('图片暂时无法显示')
    expect(wrapper.text()).toContain('第1页替代文本')
  })
})
