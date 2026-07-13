import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import AnswerCard from './AnswerCard.vue'

describe('AnswerCard', () => {
  it('renders the fixed fake answer fields', () => {
    const wrapper = mount(AnswerCard, {
      props: {
        answer: {
          answer: '它会从许多带有名字的小猫图片中学习共同特点。',
          check_question: '图片旁边写着‘小猫’，这个名字在训练中叫什么？',
          used_card_ids: ['U1-C02', 'U1-C04'],
          next_actions: ['answer_check', 'open_storybook']
        }
      }
    })

    expect(wrapper.text()).toContain('它会从许多带有名字的小猫图片中学习共同特点。')
    expect(wrapper.text()).toContain('图片旁边写着‘小猫’，这个名字在训练中叫什么？')
    expect(wrapper.text()).toContain('answer_check')
    expect(wrapper.text()).toContain('open_storybook')
  })
})
