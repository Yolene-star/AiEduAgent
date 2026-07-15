# sherpa-onnx offline TTS assets

This directory is reserved for local sherpa-onnx WebAssembly TTS runtime files.

Copy the generated files from `k2-fsa/sherpa-onnx/wasm/tts` into this directory:

- `sherpa-onnx-tts.worker.js`
- `sherpa-onnx-tts.js`
- `sherpa-onnx-wasm-main-tts.js`
- `sherpa-onnx-wasm-main-tts.wasm`
- any model/data assets produced by the sherpa-onnx TTS build

The app probes these files at runtime. If they are present, `SpeechControls.vue` can use local CPU-only TTS through a Web Worker and Web Audio. If they are absent, it falls back to browser `speechSynthesis`.

Large model and wasm files are intentionally ignored by Git. Keep them local for demos or distribute them as release artifacts with their original sherpa-onnx/model licenses.
