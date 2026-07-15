import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import QuizPanel from './QuizPanel.vue'

async function flushPromises() {
  await new Promise((resolve) => setTimeout(resolve, 0))
}

describe('QuizPanel', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('loads a fixed quiz and renders backend feedback after submit', async () => {
    const fetchMock = vi
      .spyOn(globalThis, 'fetch')
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify([
            {
              id: 'U1-C02-lower_primary-mc',
              stage: 'lower_primary',
              card_id: 'U1-C02',
              quiz_type: 'multiple_choice',
              prompt: '图片旁边写着“小猫”，这个名字在训练中叫什么？',
              options: [
                { id: 'A', text: '标签' },
                { id: 'B', text: '像素' }
              ],
              items: [],
              review_card_id: 'U1-C02'
            }
          ]),
          { status: 200, headers: { 'content-type': 'application/json' } }
        )
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            question_id: 'U1-C02-lower_primary-mc',
            correct: true,
            explanation: '标签就是给样本配上的正确名字。',
            error_type: 'none',
            review_card_id: 'U1-C02',
            next_actions: ['next_quiz'],
            already_recorded: false
          }),
          { status: 200, headers: { 'content-type': 'application/json' } }
        )
      )

    const wrapper = mount(QuizPanel, { props: { stage: 'lower_primary' } })
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('图片旁边写着“小猫”')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    await wrapper.vm.$nextTick()

    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8000/api/v1/quiz/U1-C02-lower_primary-mc/submit',
      expect.objectContaining({
        method: 'POST',
        body: expect.stringContaining('"answer":"A"')
      })
    )
    expect(wrapper.text()).toContain('回答正确')
    expect(wrapper.text()).toContain('标签就是给样本配上的正确名字。')
  })
})
