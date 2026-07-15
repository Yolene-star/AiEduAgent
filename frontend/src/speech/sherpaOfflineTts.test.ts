import { afterEach, describe, expect, it, vi } from 'vitest'

import { probeSherpaOfflineTts } from './sherpaOfflineTts'

describe('probeSherpaOfflineTts', () => {
  afterEach(() => {
    vi.restoreAllMocks()
    vi.unstubAllGlobals()
  })

  it('reports missing runtime files when sherpa assets are absent', async () => {
    vi.stubGlobal('Worker', class MockWorker {})
    vi.stubGlobal('AudioContext', class MockAudioContext {})
    vi.stubGlobal('fetch', vi.fn(async () => new Response('', { status: 404 })))

    const result = await probeSherpaOfflineTts()

    expect(result.available).toBe(false)
    expect(result.missing).toContain('sherpa-onnx-tts.worker.js')
    expect(result.missing).toContain('sherpa-onnx-wasm-main-tts.wasm')
  })

  it('reports available when the required runtime files exist', async () => {
    vi.stubGlobal('Worker', class MockWorker {})
    vi.stubGlobal('AudioContext', class MockAudioContext {})
    vi.stubGlobal('fetch', vi.fn(async () => new Response('', { status: 200 })))

    const result = await probeSherpaOfflineTts()

    expect(result.available).toBe(true)
    expect(result.missing).toEqual([])
  })
})
