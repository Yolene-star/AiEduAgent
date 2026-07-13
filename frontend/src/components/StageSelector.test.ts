import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'

import StageSelector from './StageSelector.vue'

describe('StageSelector', () => {
  it('renders four stage options', () => {
    const wrapper = mount(StageSelector, {
      props: {
        modelValue: 'lower_primary'
      }
    })

    expect(wrapper.text()).toContain('小学低年级')
    expect(wrapper.text()).toContain('小学高年级')
    expect(wrapper.text()).toContain('初中')
    expect(wrapper.text()).toContain('高中')
  })
})
