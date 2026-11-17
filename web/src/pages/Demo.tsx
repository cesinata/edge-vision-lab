import { useCallback, useEffect, useRef, useState } from 'react';
import { Label } from '../components/Label';
import { DETECTOR_URL, MODEL_PUBLISHED, MODEL_UNPUBLISHED_REASON, PROJECT_MODEL_URL } from '../config';
import { CLASSES, SIZE, rgbaToNormalisedChw, softmax } from '../lib/classifier';
import { INPUT, N_ANCHORS, type Detection, decode, letterboxScale, rgbaToBgrChw } from '../lib/yolox';
import { loadOrt, modelUrl, type Ort } from '../lib/ort';
import { median } from '../lib/stats';

type Session = Awaited<ReturnType<Ort['InferenceSession']['create']>>;
type Source = HTMLVideoElement | HTMLImageElement | HTMLCanvasElement;

function sourceSize(src: Source): [number, number] {
  if (src instanceof HTMLVideoElement) return [src.videoWidth, src.videoHeight];
  if (src instanceof HTMLCanvasElement) return [src.width, src.height];
  return [src.naturalWidth, src.naturalHeight];
}

function letterboxPixels(src: Source, scratch: HTMLCanvasElement): { data: Uint8ClampedArray; scale: number } {
  const [w, h] = sourceSize(src);
  const scale = letterboxScale(w, h);
  scratch.width = INPUT;
  scratch.height = INPUT;
  const ctx = scratch.getContext('2d', { willReadFrequently: true })!;
  ctx.fillStyle = 'rgb(114,114,114)';
  ctx.fillRect(0, 0, INPUT, INPUT);
  ctx.drawImage(src, 0, 0, Math.round(w * scale), Math.round(h * scale));
  return { data: ctx.getImageData(0, 0, INPUT, INPUT).data, scale };
}

function drawDetections(canvas: HTMLCanvasElement, src: Source, dets: Detection[]) {
  const [w, h] = sourceSize(src);
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d')!;
  ctx.drawImage(src, 0, 0, w, h);
  ctx.lineWidth = Math.max(2, w / 300);
  ctx.font = `${Math.max(14, Math.round(w / 40))}px ui-monospace, Menlo, Consolas, monospace`;
  for (const d of dets) {
    ctx.strokeStyle = '#a58be0';
    ctx.strokeRect(d.x, d.y, d.w, d.h);
    const text = `${d.label} ${(d.score * 100).toFixed(0)}%`;
    const tw = ctx.measureText(text).width + 8;
    ctx.fillStyle = '#2e2a33';
    ctx.fillRect(d.x, Math.max(0, d.y - 22), tw, 22);
    ctx.fillStyle = '#ffffff';
    ctx.fillText(text, d.x + 4, Math.max(16, d.y - 6));
  }
}

function GeneralDetector() {
  const [status, setStatus] = useState('Not loaded. The model (about 3.7 MB) and the runtime load when you press a button.');
  const [times, setTimes] = useState<number[]>([]);
  const [found, setFound] = useState<Detection[]>([]);
  const [running, setRunning] = useState(false);
  const [hasImage, setHasImage] = useState(false);
  const session = useRef<Session | null>(null);
  const ort = useRef<Ort | null>(null);
  const video = useRef<HTMLVideoElement>(null);
  const view = useRef<HTMLCanvasElement>(null);
  const scratch = useRef<HTMLCanvasElement>(null);
  const stream = useRef<MediaStream | null>(null);
  const loop = useRef(false);

  const ensureSession = useCallback(async () => {
    if (session.current) return;
    setStatus('Loading the runtime and the detector...');
    ort.current = await loadOrt();
    session.current = await ort.current.InferenceSession.create(modelUrl(DETECTOR_URL), { executionProviders: ['wasm'] });
    setStatus('Detector ready.');
  }, []);

  const infer = useCallback(async (src: Source) => {
    const o = ort.current!;
    const s = session.current!;
    const { data, scale } = letterboxPixels(src, scratch.current!);
    const input = new o.Tensor('float32', rgbaToBgrChw(data), [1, 3, INPUT, INPUT]);
    const t0 = performance.now();
    const out = await s.run({ [s.inputNames[0]]: input });
    const dt = performance.now() - t0;
    const raw = out[s.outputNames[0]].data as Float32Array;
    if (raw.length !== N_ANCHORS * 85) throw new Error(`unexpected output size ${raw.length}`);
    const dets = decode(raw, scale);
    drawDetections(view.current!, src, dets);
    setHasImage(true);
    setFound(dets);
    setTimes((t) => [...t.slice(-29), dt]);
  }, []);

  const stop = useCallback(() => {
    loop.current = false;
    stream.current?.getTracks().forEach((t) => t.stop());
    stream.current = null;
    setRunning(false);
  }, []);

  useEffect(() => stop, [stop]);

  const start = async () => {
    try {
      await ensureSession();
      stream.current = await navigator.mediaDevices.getUserMedia({ video: { width: 640 }, audio: false });
      const v = video.current!;
      v.srcObject = stream.current;
      await v.play();
      setRunning(true);
      loop.current = true;
      setStatus('Running on your webcam. Frames stay in this browser tab; nothing is uploaded.');
      while (loop.current) {
        await infer(v);
        await new Promise((r) => requestAnimationFrame(() => r(null)));
      }
    } catch (err) {
      setStatus(`Could not start: ${err instanceof Error ? err.message : String(err)}`);
      stop();
    }
  };

  const onFile = async (file: File | undefined) => {
    if (!file) return;
    stop();
    try {
      await ensureSession();
      const img = new Image();
      img.src = URL.createObjectURL(file);
      await img.decode();
      await infer(img);
      URL.revokeObjectURL(img.src);
      setStatus('Done. The image stayed in this browser tab; nothing was uploaded.');
    } catch (err) {
      setStatus(`Could not run: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  // ?selftest=1 runs the real load-and-infer path once on a synthetic image and reports
  // the result in the status line. Used to check the build in a headless browser.
  useEffect(() => {
    if (!new URLSearchParams(window.location.search).has('selftest')) return;
    (async () => {
      try {
        await ensureSession();
        const c = document.createElement('canvas');
        c.width = 640;
        c.height = 512;
        const g = c.getContext('2d')!;
        const grad = g.createLinearGradient(0, 0, 0, 512);
        grad.addColorStop(0, '#6aa0d8');
        grad.addColorStop(1, '#c9d9ea');
        g.fillStyle = grad;
        g.fillRect(0, 0, 640, 512);
        g.fillStyle = '#222';
        g.fillRect(300, 240, 40, 20);
        await infer(c);
        setStatus('SELFTEST OK: runtime loaded, detector ran on a synthetic image.');
      } catch (err) {
        setStatus(`SELFTEST FAILED: ${err instanceof Error ? err.message : String(err)}`);
      }
    })();
  }, [ensureSession, infer]);

  const med = median(times);
  return (
    <section aria-labelledby="gen">
      <h2 id="gen">General detector <Label kind="measured (browser)" detail="timings" /></h2>
      <p>
        <strong>Third-party pre-trained model, not trained by this project.</strong> YOLOX-Nano from Megvii
        (Apache-2.0), trained on the COCO dataset, which has a "bird" and an "airplane" class but no "drone" class.
        Use it to see in-browser inference working. It says nothing about this project's classifier.
      </p>
      <div className="row">
        <button className="primary" onClick={start} disabled={running}>Start webcam</button>
        <button onClick={stop} disabled={!running}>Stop</button>
        <label className="row" style={{ margin: 0 }}>
          <span>or upload an image:</span>
          <input type="file" accept="image/*" onChange={(e) => onFile(e.target.files?.[0])} />
        </label>
      </div>
      <p role="status" aria-live="polite">{status}</p>
      <video ref={video} className="hidden" muted playsInline aria-hidden="true" />
      <canvas ref={scratch} className="hidden" width={INPUT} height={INPUT} aria-hidden="true" style={{ display: 'none' }} />
      <canvas ref={view} className="view" hidden={!hasImage} role="img" aria-label="Camera or uploaded image with detected objects outlined and labelled" />
      <div aria-live="polite">
        <p>
          Inference time (the model run only), median of the last {times.length} runs:{' '}
          <strong>{times.length ? `${med.toFixed(1)} ms` : 'not run yet'}</strong> <Label kind="measured (browser)" />
          {' '}on this browser and device, single-threaded WebAssembly. It will differ on yours.
        </p>
        <ul>
          {found.length === 0 ? <li>No detections yet.</li> : found.map((d, i) => (
            <li key={i}>{d.label}: {(d.score * 100).toFixed(0)}% at x {Math.round(d.x)}, y {Math.round(d.y)}, {Math.round(d.w)} by {Math.round(d.h)} px</li>
          ))}
        </ul>
      </div>
    </section>
  );
}

function ProjectModel() {
  const [result, setResult] = useState<{ probs: number[]; ms: number } | null>(null);
  const [msg, setMsg] = useState('');
  const scratch = useRef<HTMLCanvasElement>(null);

  const run = async (file: File | undefined) => {
    if (!file) return;
    try {
      const o = await loadOrt();
      const s = await o.InferenceSession.create(modelUrl(PROJECT_MODEL_URL), { executionProviders: ['wasm'] });
      const img = new Image();
      img.src = URL.createObjectURL(file);
      await img.decode();
      const c = scratch.current!;
      c.width = SIZE;
      c.height = SIZE;
      const ctx = c.getContext('2d', { willReadFrequently: true })!;
      ctx.drawImage(img, 0, 0, SIZE, SIZE);
      const input = new o.Tensor('float32', rgbaToNormalisedChw(ctx.getImageData(0, 0, SIZE, SIZE).data), [1, 3, SIZE, SIZE]);
      const t0 = performance.now();
      const out = await s.run({ [s.inputNames[0]]: input });
      const ms = performance.now() - t0;
      setResult({ probs: softmax(out[s.outputNames[0]].data as Float32Array), ms });
      setMsg('');
    } catch (err) {
      setMsg(`Could not run: ${err instanceof Error ? err.message : String(err)}`);
    }
  };

  return (
    <section aria-labelledby="proj">
      <h2 id="proj">This project's classifier</h2>
      {MODEL_PUBLISHED ? (
        <>
          <p>Upload a small crop of a bird, a drone or neither. The image is squeezed to 224 by 224 and stays in your browser.</p>
          <input type="file" accept="image/*" onChange={(e) => run(e.target.files?.[0])} aria-label="Upload a crop" />
          <canvas ref={scratch} style={{ display: 'none' }} />
          {msg ? <p role="alert">{msg}</p> : null}
          {result ? (
            <p aria-live="polite">
              {CLASSES.map((c, i) => `${c} ${(result.probs[i] * 100).toFixed(1)}%`).join(', ')}. Inference time{' '}
              {result.ms.toFixed(1)} ms <Label kind="measured (browser)" />
            </p>
          ) : null}
        </>
      ) : (
        <div className="notice warn" role="note">
          <strong>Model not published yet.</strong> {MODEL_UNPUBLISHED_REASON} No placeholder model is shipped, so
          there is nothing to run here. Once the authors confirm the licence the repository owner can publish it with{' '}
          <code>scripts/publish_model.sh</code>.
        </div>
      )}
    </section>
  );
}

export function Demo() {
  return (
    <>
      <h1>Try it</h1>
      <p>Everything runs in your browser with ONNX Runtime Web. No image or video frame leaves the page.</p>
      <GeneralDetector />
      <ProjectModel />
    </>
  );
}
