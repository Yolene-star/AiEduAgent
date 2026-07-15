export interface SherpaTtsProbeResult {
  available: boolean
  missing: string[]
}

export interface SherpaTtsAudio {
  samples: Float32Array
  sampleRate: number
}

type ReadyMessage = {
  type: 'sherpa-onnx-tts-ready'
  modelType: number
  numSpeakers: number
}

type ResultMessage = {
  type: 'sherpa-onnx-tts-result'
  samples: Float32Array
  sampleRate: number
}

type ErrorMessage = {
  type: 'error'
  message: string
}

type ProgressMessage = {
  type: 'sherpa-onnx-tts-progress' | 'sherpa-onnx-tts-generation-progress'
  status?: string
  progress?: number
}

type SherpaWorkerMessage = ReadyMessage | ResultMessage | ErrorMessage | ProgressMessage

const SHERPA_BASE = '/vendor/sherpa-onnx-tts/'
const REQUIRED_RUNTIME_FILES = [
  'sherpa-onnx-tts.worker.js',
  'sherpa-onnx-tts.js',
  'sherpa-onnx-wasm-main-tts.js',
  'sherpa-onnx-wasm-main-tts.wasm'
]

async function hasAsset(path: string): Promise<boolean> {
  try {
    const response = await fetch(`${SHERPA_BASE}${path}`, {
      method: 'HEAD',
      cache: 'no-store'
    })
    return response.ok
  } catch {
    return false
  }
}

export async function probeSherpaOfflineTts(): Promise<SherpaTtsProbeResult> {
  if (typeof Worker === 'undefined' || typeof fetch === 'undefined' || typeof AudioContext === 'undefined') {
    return { available: false, missing: ['browser-worker-or-audio-context'] }
  }

  const checks = await Promise.all(
    REQUIRED_RUNTIME_FILES.map(async (path) => ({
      path,
      ok: await hasAsset(path)
    }))
  )
  const missing = checks.filter((check) => !check.ok).map((check) => check.path)
  return { available: missing.length === 0, missing }
}

export class SherpaOfflineTtsClient {
  private worker: Worker | null = null
  private readyPromise: Promise<ReadyMessage> | null = null
  private pending:
    | {
        resolve: (audio: SherpaTtsAudio) => void
        reject: (error: Error) => void
      }
    | null = null

  constructor(private onStatus: (status: string) => void = () => {}) {}

  init(): Promise<ReadyMessage> {
    if (this.readyPromise) {
      return this.readyPromise
    }

    this.readyPromise = new Promise((resolve, reject) => {
      this.worker = new Worker(`${SHERPA_BASE}sherpa-onnx-tts.worker.js`, { type: 'module' })
      this.worker.onmessage = (event: MessageEvent<SherpaWorkerMessage>) => {
        const message = event.data
        if (message.type === 'sherpa-onnx-tts-ready') {
          this.onStatus(`离线语音已就绪，speaker 数量：${message.numSpeakers}`)
          resolve(message)
          return
        }
        if (message.type === 'sherpa-onnx-tts-result') {
          this.pending?.resolve({
            samples: message.samples,
            sampleRate: message.sampleRate
          })
          this.pending = null
          return
        }
        if (message.type === 'error') {
          const error = new Error(message.message)
          if (this.pending) {
            this.pending.reject(error)
            this.pending = null
          } else {
            reject(error)
          }
          return
        }
        if (message.type === 'sherpa-onnx-tts-generation-progress') {
          const percent = Math.round((message.progress ?? 0) * 100)
          this.onStatus(`离线语音生成中：${percent}%`)
          return
        }
        this.onStatus(message.status ?? '离线语音模型加载中...')
      }
      this.worker.onerror = (event) => {
        reject(new Error(event.message || 'Sherpa ONNX worker failed'))
      }
    })

    return this.readyPromise
  }

  async synthesize(text: string, speed: number): Promise<SherpaTtsAudio> {
    const worker = this.worker
    if (!worker) {
      throw new Error('Sherpa ONNX worker is not initialized')
    }
    if (this.pending) {
      throw new Error('Sherpa ONNX TTS is already generating audio')
    }

    await this.init()
    return new Promise((resolve, reject) => {
      this.pending = { resolve, reject }
      worker.postMessage({
        type: 'generate',
        text,
        sid: 0,
        speed
      })
    })
  }

  terminate() {
    this.pending?.reject(new Error('Sherpa ONNX TTS terminated'))
    this.pending = null
    this.worker?.terminate()
    this.worker = null
    this.readyPromise = null
  }
}

export async function playSherpaAudio(audio: SherpaTtsAudio): Promise<AudioContext> {
  const audioContext = new AudioContext({ sampleRate: audio.sampleRate })
  const buffer = audioContext.createBuffer(1, audio.samples.length, audio.sampleRate)
  buffer.getChannelData(0).set(audio.samples)
  const source = audioContext.createBufferSource()
  source.buffer = buffer
  source.connect(audioContext.destination)
  source.start()
  return audioContext
}
