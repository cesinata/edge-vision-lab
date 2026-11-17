import { useCallback, useEffect, useRef, useState } from 'react';
import { COPY } from '../content/copy';
import { benchMetric } from '../content/results';
import { DETECTOR_BYTES, DETECTOR_URL, MODEL_PUBLISHED, PROJECT_MODEL_URL } from '../config';
import { SIZE, CLASSES, rgbaToNormalisedChw, softmax } from '../lib/classifier';
import { loadOrt, modelUrl, type Ort } from '../lib/ort';
import { median } from '../lib/stats';
import { INPUT, N_ANCHORS, decode, letterboxScale, rgbaToBgrChw, type Detection } from '../lib/yolox';
import { Viewfinder } from '../illustrations/Viewfinder';
import { Label } from './Label';

type Session = Awaited<ReturnType<Ort['InferenceSession']['create']>>;
type Source = HTMLVideoElement | HTMLImageElement | HTMLCanvasElement;
type ModelKey = 'project' | 'general';

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

function drawFrame(canvas: HTMLCanvasElement, src: Source, dets: Detection[]) {
  const [w, h] = sourceSize(src);
  canvas.width = w;
  canvas.height = h;
  const ctx = canvas.getContext('2d')!;
  ctx.drawImage(src, 0, 0, w, h);
  ctx.lineWidth = Math.max(2, w / 300);
  ctx.font = `500 ${Math.max(14, Math.round(w / 40))}px "IBM Plex Mono", ui-monospace, Menlo, Consolas, monospace`;
  for (const d of dets) {
    ctx.strokeStyle = '#ffd200';
    ctx.strokeRect(d.x, d.y, d.w, d.h);
    const text = `${d.label} ${(d.score * 100).toFixed(0)}%`;
    const tw = ctx.measureText(text).width + 8;
    ctx.fillStyle = '#03234b';
    ctx.fillRect(d.x, Math.max(0, d.y - 22), tw, 22);
    ctx.fillStyle = '#ffffff';
    ctx.fillText(text, d.x + 4, Math.max(16, d.y - 6));
  }
}

/** Live demo: the general detector works today; this project's model is locked until it is published. */
export function DemoPanel() {
  const [model, setModel] = useState<ModelKey>('general');
  const [status, setStatus] = useState('Not loaded. The model (about 3.7 MB) and the runtime load when you press a button.');
  const [times, setTimes] = useState<number[]>([]);
  const [found, setFound] = useState<Detection[]>([]);
  const [verdict, setVerdict] = useState('');
  const [running, setRunning] = useState(false);
  const [hasImage, setHasImage] = useState(false);
  const sessions = useRef<Partial<Record<ModelKey, Session>>>({});
  const ort = useRef<Ort | null>(null);
  const video = useRef<HTMLVideoElement>(null);
  const view = useRef<HTMLCanvasElement>(null);
  const scratch = useRef<HTMLCanvasElement>(null);
  const stream = useRef<MediaStream | null>(null);
  const loop = useRef(false);
  const modelRef = useRef<ModelKey>(model);
  modelRef.current = model;

  const projectLocked = model === 'project' && !MODEL_PUBLISHED;
  const int8Kb = benchMetric('int8_onnx', 'size_kb');

  const ensureSession = useCallback(async (m: ModelKey) => {
    if (sessions.current[m]) return;
    setStatus('Loading the runtime and the model...');
    ort.current = await loadOrt();
    sessions.current[m] = await ort.current.InferenceSession.create(modelUrl(m === 'general' ? DETECTOR_URL : PROJECT_MODEL_URL), { executionProviders: ['wasm'] });
    setStatus('Model ready.');
  }, []);

  const infer = useCallback(async (src: Source) => {
    const o = ort.current!;
    const m = modelRef.current;
    const s = sessions.current[m]!;
    let dt: number;
    if (m === 'general') {
      const { data, scale } = letterboxPixels(src, scratch.current!);
      const input = new o.Tensor('float32', rgbaToBgrChw(data), [1, 3, INPUT, INPUT]);
      const t0 = performance.now();
      const out = await s.run({ [s.inputNames[0]]: input });
      dt = performance.now() - t0;
      const raw = out[s.outputNames[0]].data as Float32Array;
      if (raw.length !== N_ANCHORS * 85) throw new Error(`unexpected output size ${raw.length}`);
      const dets = decode(raw, scale);
      drawFrame(view.current!, src, dets);
      setFound(dets);
    } else {
      // This project's classifier names the whole image: centre square, resized to 224 x 224.
      const [w, h] = sourceSize(src);
      const side = Math.min(w, h);
      const c = scratch.current!;
      c.width = SIZE;
      c.height = SIZE;
      const ctx = c.getContext('2d', { willReadFrequently: true })!;
      ctx.drawImage(src, (w - side) / 2, (h - side) / 2, side, side, 0, 0, SIZE, SIZE);
      const input = new o.Tensor('float32', rgbaToNormalisedChw(ctx.getImageData(0, 0, SIZE, SIZE).data), [1, 3, SIZE, SIZE]);
      const t0 = performance.now();
      const out = await s.run({ [s.inputNames[0]]: input });
      dt = performance.now() - t0;
      const p = softmax(out[s.outputNames[0]].data as Float32Array);
      drawFrame(view.current!, src, []);
      setVerdict(CLASSES.map((c2, i) => `${c2} ${(p[i] * 100).toFixed(1)}%`).join(', '));
    }
    setHasImage(true);
    setTimes((t) => [...t.slice(-29), dt]);
  }, []);

  const stop = useCallback(() => {
    loop.current = false;
    stream.current?.getTracks().forEach((t) => t.stop());
    stream.current = null;
    setRunning(false);
  }, []);

  useEffect(() => stop, [stop]);

  const choose = (m: ModelKey) => {
    stop();
    setModel(m);
    setTimes([]);
    setFound([]);
    setVerdict('');
    setHasImage(false);
  };

  const start = async () => {
    try {
      await ensureSession(model);
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
      await ensureSession(model);
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

  // ?selftest=1 runs the real load-and-infer path once on a synthetic image and reports the result
  // in the status line. Used to check the build in a headless browser.
  useEffect(() => {
    if (!new URLSearchParams(window.location.search).has('selftest')) return;
    (async () => {
      try {
        await ensureSession('general');
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
  const sizeKb = model === 'general' ? DETECTOR_BYTES / 1024 : int8Kb?.value ?? null;
  const models = COPY.demo.models;
  const active = models[model === 'project' ? 0 : 1];

  return (
    <div className="card demo">
      <div className="stage">
        <video ref={video} hidden muted playsInline aria-hidden="true" />
        <canvas ref={scratch} hidden aria-hidden="true" />
        <div className="gridbg" style={{ borderRadius: 4, border: '1px solid var(--rule)' }} hidden={hasImage}>
          <Viewfinder />
        </div>
        <canvas ref={view} className="view" hidden={!hasImage} role="img" aria-label="Camera or uploaded image with what the model found" />
        <p className="cap" role="status" aria-live="polite">{status}</p>
      </div>
      <div className="side">
        <div className="lbl">Model</div>
        <div className="toggle" role="group" aria-label="Choose a model">
          <button aria-pressed={model === 'project'} onClick={() => choose('project')}>{models[0].name}</button>
          <button aria-pressed={model === 'general'} onClick={() => choose('general')}>{models[1].name}</button>
        </div>
        <p className="sm ink2" style={{ margin: 0 }}><strong>{active.name}</strong> {active.text}</p>
        <div className="readouts">
          <div><span className="k">latency (ms)</span>{times.length ? med.toFixed(1) : '—'}</div>
          <div><span className="k">model size (KB)</span>{sizeKb ? Math.round(sizeKb).toLocaleString('en-AU') : '—'}</div>
          <div style={{ gridColumn: '1 / -1', borderRight: 0 }}><span className="k">input size</span>{model === 'general' ? `${INPUT} × ${INPUT}` : `${SIZE} × ${SIZE}`}</div>
        </div>
        <p className="cap" style={{ margin: 0 }}>latency measured in your browser <Label kind="measured (browser)" /></p>
        <p className="cap" style={{ margin: 0 }}>model size <Label kind="measured (host CPU)" /></p>
        <div className="row" style={{ margin: 0 }}>
          <button className="btn primary" onClick={start} disabled={running || projectLocked}>Start webcam</button>
          <button className="btn secondary" onClick={stop} disabled={!running}>Stop</button>
        </div>
        <label style={{ margin: 0 }}>or upload an image:
          <input type="file" accept="image/*" onChange={(e) => onFile(e.target.files?.[0])} disabled={projectLocked} />
        </label>
        {model === 'general' && found.length > 0 ? (
          <ul className="sm" style={{ margin: 0, paddingLeft: 18 }}>
            {found.slice(0, 5).map((d, i) => <li key={i}>{d.label}: {(d.score * 100).toFixed(0)}%</li>)}
          </ul>
        ) : null}
        {model === 'project' && verdict ? <p className="sm" aria-live="polite" style={{ margin: 0 }}>{verdict}</p> : null}
      </div>
    </div>
  );
}
