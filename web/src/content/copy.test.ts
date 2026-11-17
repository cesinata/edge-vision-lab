import { describe, expect, it } from 'vitest';
import { COPY } from './copy';

describe('site copy (generated from docs/site-copy.md)', () => {
  it('has the expected sections and counts', () => {
    expect(COPY.nav).toEqual(['Learn', 'Try it', 'Results', 'GitHub']);
    expect(COPY.pipeline.steps).toHaveLength(6);
    expect(COPY.anatomy.parts).toHaveLength(7);
    expect(COPY.lessons.items).toHaveLength(6);
    expect(COPY.demo.models).toHaveLength(2);
    expect(COPY.about.items).toHaveLength(4);
    expect(COPY.results.items).toHaveLength(3);
  });

  it('quotes no recall figure: it is a placeholder filled from the results file', () => {
    expect(COPY.results.items[0].text).toContain('{{drone_recall}}');
    expect(COPY.results.items[0].text).not.toMatch(/0\.\d{3}/);
  });

  it('keeps the vendor trademark and not-affiliated line', () => {
    expect(COPY.footer).toContain('STM32 is a trademark of STMicroelectronics');
    expect(COPY.footer).toContain('not affiliated with any vendor');
  });

  it('never claims the detector is larger, and says classification not detection for this model', () => {
    const all = JSON.stringify(COPY);
    expect(all).not.toMatch(/larger model/i);
    expect(COPY.about.items[3].a).toContain("doesn't find objects in a full frame yet");
  });
});
