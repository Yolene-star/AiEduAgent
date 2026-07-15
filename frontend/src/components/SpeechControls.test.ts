import { mount } from '@vue/test-utils'
import { afterEach, describe, expect, it, vi } from 'vitest'

import SpeechControls from './SpeechControls.vue'

describe('SpeechControls', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('keeps subtitles visible when browser speech is unavailable', async () => {
    const wrapper = mount(SpeechControls, { props: { text: '这是一句字幕。' } })

    expect(wrapper.text()).toContain('字幕：这是一句字幕。')
    await wrapper.find('button').trigger('click')
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('文本仍可正常阅读')
  })

  it('uses browser speech synthesis with a Chinese voice when available', async () => {
    const speak = vi.fn()
    const cancel = vi.fn()
    const getVoices = vi.fn(() => [
      {
        name: 'Chinese Demo Voice',
        lang: 'zh-CN',
        default: true,
        localService: true,
        voiceURI: 'zh-demo'
      }
    ])
    const speechSynthesis = {
      speak,
      cancel,
      pause: vi.fn(),
      resume: vi.fn(),
      getVoices,
      onvoiceschanged: null
    }
    const utterances: SpeechSynthesisUtterance[] = []
    class MockUtterance {
      text: string
      lang = ''
      rate = 1
      voice: SpeechSynthesisVoice | null = null
      onend: (() => void) | null = null
      onerror: (() => void) | null = null

      constructor(text: string) {
        this.text = text
        utterances.push(this as unknown as SpeechSynthesisUtterance)
      }
    }

    vi.stubGlobal('speechSynthesis', speechSynthesis)
    vi.stubGlobal('SpeechSynthesisUtterance', MockUtterance)

    const wrapper = mount(SpeechControls, { props: { text: '播放这句中文。' } })
    await wrapper.vm.$nextTick()
    await wrapper.find('button').trigger('click')

    expect(getVoices).toHaveBeenCalled()
    expect(speak).toHaveBeenCalledTimes(1)
    expect(utterances[0].lang).toBe('zh-CN')
    expect(utterances[0].voice?.name).toBe('Chinese Demo Voice')
  })
})
