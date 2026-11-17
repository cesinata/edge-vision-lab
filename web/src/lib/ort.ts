// onnxruntime-web is loaded on demand, only when a demo starts, so the other pages
// stay small. Vite emits the wasm binary as one hashed asset; its URL is passed to the
// runtime explicitly.
import wasmUrl from 'onnxruntime-web/ort-wasm-simd-threaded.wasm?url';

export type Ort = typeof import('onnxruntime-web/wasm');

let ortPromise: Promise<Ort> | null = null;

export function loadOrt(): Promise<Ort> {
  if (!ortPromise) {
    ortPromise = import('onnxruntime-web/wasm').then((ort) => {
      ort.env.wasm.wasmPaths = { wasm: new URL(wasmUrl, document.baseURI).href };
      ort.env.wasm.numThreads = 1; // GitHub Pages cannot send the headers threads need
      return ort;
    });
  }
  return ortPromise;
}

export function modelUrl(path: string): string {
  return new URL(import.meta.env.BASE_URL + path, document.baseURI).href;
}
