import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import SpeechControls from './SpeechControls.vue'

describe('SpeechControls', () => {
  it('keeps subtitles visible when browser speech is unavailable', async () => {
    const wrapper = mount(SpeechControls, { props: { text: '这是一句字幕。' } })

    expect(wrapper.text()).toContain('字幕：这是一句字幕。')
    await wrapper.find('button').trigger('click')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('文本仍可正常阅读')
  })
})
