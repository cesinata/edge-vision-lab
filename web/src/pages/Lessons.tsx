import { Label, fmt } from '../components/Label';
import { benchMetric, evalTorch, splitSummary } from '../content/results';

export function Lessons() {
  const s = splitSummary;
  const drone = s?.videos_per_class.DRONE;
  const droneClusters = s?.clusters_touched_per_class.DRONE;
  const birdClusters = s?.clusters_touched_per_class.BIRD;
  const birdVideos = s?.videos_per_class.BIRD;
  const a32 = benchMetric('fp32_onnx', 'test_accuracy');
  const a8 = benchMetric('int8_onnx', 'test_accuracy');
  const s32 = benchMetric('fp32_onnx', 'size_kb');
  const s8 = benchMetric('int8_onnx', 'size_kb');
  return (
    <>
      <h1>Lessons from building this</h1>
      <p>Each lesson comes from something that actually happened in this repository. Where there is a number, it has a label.</p>

      <section className="card" aria-labelledby="l1">
        <h2 id="l1" style={{ marginTop: 0 }}>1. Split by scene, not by frame</h2>
        <p>
          Video frames next to each other look almost identical. If you split frames at random, near-copies of the same
          scene land in both train and test, and the test score flatters the model. Here, clips were often filmed from the
          same spot, so even splitting by clip was not enough.
        </p>
        {s ? (
          <p>
            Grouping clips by how similar their frames look gave {s.n_clusters} scene clusters from {s.n_videos} videos{' '}
            <Label kind="measured (host CPU)" />. The {drone} drone videos fall into only {droneClusters} clusters, while
            the {birdVideos} bird videos fall into {birdClusters}. So drones were filmed in a few places and birds in many.
            A model can pick up the place instead of the object.
          </p>
        ) : null}
        <p><strong>What to do:</strong> split by whole scenes, write down how you grouped them, and say what the grouping misses.</p>
      </section>

      <section className="card" aria-labelledby="l2">
        <h2 id="l2" style={{ marginTop: 0 }}>2. A small test set needs honest error bars</h2>
        <p>
          Frames from one video are not independent samples, so the number of independent samples is closer to the number
          of videos. Intervals here are resampled by video. They are still optimistic, because videos from one scene are
          not independent either.
        </p>
        {evalTorch ? <p>On the test split macro F1 is {fmt(evalTorch.macro_f1)}, with a 95% interval of {fmt(evalTorch.macro_f1_ci95[0])} to {fmt(evalTorch.macro_f1_ci95[1])} <Label kind="measured (host CPU)" />. That width is the point.</p> : null}
        <p><strong>What to do:</strong> report an interval, say how it was made, and say how small the test set is.</p>
      </section>

      <section className="card" aria-labelledby="l3">
        <h2 id="l3" style={{ marginTop: 0 }}>3. Check labels before trusting a decoder</h2>
        <p>
          The labels came in a MATLAB format that Python cannot read directly. A small third-party decoder read most files
          but treated a frame with two birds as "no target", because it guessed from byte sizes. The check that caught it was
          simple: does the number of decoded labels equal the number of video frames? It did not, for several bird videos.
        </p>
        <p><strong>What to do:</strong> compare counts against something independent, and make a parser fail loudly on input it does not recognise.</p>
      </section>

      <section className="card" aria-labelledby="l4">
        <h2 id="l4" style={{ marginTop: 0 }}>4. Quantisation trades size for accuracy: measure both</h2>
        {a32 && a8 && s32 && s8 ? (
          <p>
            Converting the model to int8 changed its size from {fmt(s32.value, 1)} KB to {fmt(s8.value, 1)} KB{' '}
            <Label kind="measured (host CPU)" /> and its test accuracy from {fmt(a32.value)} to {fmt(a8.value)}{' '}
            <Label kind="measured (host CPU)" />. Whether that trade is acceptable depends on the job.
          </p>
        ) : (
          <p>The quantisation comparison has not been run yet.</p>
        )}
        <p><strong>What to do:</strong> keep a held-out set that the quantiser never saw, and compare before and after on it.</p>
      </section>

      <section className="card" aria-labelledby="l5">
        <h2 id="l5" style={{ marginTop: 0 }}>5. Write the device logic so a laptop can test it</h2>
        <p>
          The state machine takes timestamps and sensor readings as input and has no clock or random numbers inside. That
          lets a test replay a stall, a low battery or a fault and check the result exactly. Making the test fail on purpose
          (changing one comparison, switching off the watchdog) showed the tests would notice.
        </p>
        <p><strong>What to do:</strong> keep hardware access at the edge, test the logic in the middle, and say what the tests do not cover.</p>
      </section>

      <section className="card" aria-labelledby="l6">
        <h2 id="l6" style={{ marginTop: 0 }}>6. The licence of where the data came from matters</h2>
        <p>
          One candidate dataset was rejected because its images came from a stock footage site whose terms prohibit
          machine-learning use. Another is used with a licence question still open, so no model or sample images are published.
          A dataset's own licence does not override the terms of the material it was built from.
        </p>
        <p><strong>What to do:</strong> trace where the data came from before you train on it, and write the answer down.</p>
      </section>

      <section className="card" aria-labelledby="l7">
        <h2 id="l7" style={{ marginTop: 0 }}>7. Check colour contrast with a script</h2>
        <p>
          The first dark-mode version of one figure put light text on bright pastel dots at roughly 1.4 to 2 to 1. A contrast
          check on every text and background pair caught it before it shipped. The fix was a separate dark text colour for
          those dots.
        </p>
      </section>
    </>
  );
}
