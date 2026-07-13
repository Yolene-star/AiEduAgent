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
    const fetchMock = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(
        JSON.stringify({
          answer: '它会从许多带有名字的小猫图片中学习共同特点。',
          check_question: '图片旁边写着‘小猫’，这个名字在训练中叫什么？',
          used_card_ids: ['U1-C02', 'U1-C04'],
          next_actions: ['answer_check', 'open_storybook']
        }),
        { status: 200, headers: { 'content-type': 'application/json' } }
      )
    )

    const wrapper = mount(App)
    await wrapper.find('select').setValue('middle_school')
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
