/*!
 * ae-motion.js 1.0 - After Effects-style motion for HyperFrames and any GSAP timeline.
 *
 * One file, no dependencies but GSAP 3. Load it after GSAP with a <script src>, or paste it
 * inline (it is a plain IIFE and only defines window.AE).
 *
 * What it gives you (SKILL.md and reference/API.md beside this file):
 *   curves     every curve by name (kit.*, AE influence, easings.net, Material 3, Carbon), springs
 *              by damping or by overshoot percent, inertial bounce, AE graph-editor influence/speed
 *   keys       AE-style keyframe tracks per property, any ease per segment, holds, springs,
 *              continuous (auto-bezier) interpolation, velocity, pixel motion blur (smear)
 *   camera     2.5D camera over depth layers: pan, dolly, lens zoom, roll, handheld noise,
 *              rack focus, true parallax
 *   camera3d   true 3D orbit camera over z-layers: perspective, pan/tilt/orbit, dolly, roll,
 *              rack focus and depth of field, handheld, impact shake
 *   text       range selector, wiggly selector, masked words/lines/chars, cut, type-on (stepped or
 *              with a caret), scramble, slot roll (word or per character), counter, odometer, slam,
 *              3D flip-up, word swap, highlight wipe, text exits
 *   mattes     feathered linear wipe, iris, box/split reveals, track matte (SVG mask), text matte
 *   paths      trim paths (start/end/offset), follow a path with auto-orient
 *   tx         transitions built in halves that meet at a seam: whip, push, slide-stack, iris,
 *              matte wipe, zoom-through, dip, bar sweep, 3D flip, flash
 *   timing     duration from distance, uneven reactions, frame snapping, beat grid, hits.py beat
 *              sheets, word cues
 *   finish     grain and RGB split on hits (opt-in only), impact shake on a wrapper
 *
 * Seek-safe by construction: every procedural value is a pure function of timeline time and is
 * written by a property SETTER that GSAP calls on every render, silent seeks included (onUpdate
 * does not fire on a silent seek, which is why the HyperFrames skills switched to setters).
 *
 * Curves, springs, timing, text treatments and the AE tools build on motion-kit.js by Hugh Phan
 * (MIT, github.com/hughminhphan/motion-kit). The 3D camera, auto-bezier tracks, springs by
 * overshoot, slam / flip / wiggly / odometer / swap / per-character slot, the text matte, bar /
 * flip / flash transitions, grain and RGB split come from motion-pro (built in another of the owner's
 * Claude sessions, merged here). Everything else is new here.
 */
(function (root) {
  'use strict';
  if (root.AE && root.AE.__aeMotion) return; // loaded twice (inlined and linked): keep the first

  const G = () => {
    if (!root.gsap) throw new Error('ae-motion: load GSAP before ae-motion.js');
    return root.gsap;
  };
  const doc = root.document;
  const NS = 'http://www.w3.org/2000/svg';
  const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
  const clamp01 = (v) => clamp(v, 0, 1);
  const lerp = (a, b, u) => a + (b - a) * u;

  // ------------------------------------------------------------------ frames and time

  let FPS = null;
  function readFps() {
    const r = doc && doc.querySelector('[data-composition-id][data-fps]');
    const v = r ? Number(r.getAttribute('data-fps')) : 0;
    return v > 0 ? v : 30;
  }
  const fps = () => FPS || (FPS = readFps());
  const setFps = (n) => { FPS = n; return n; };
  const F = (n) => n / fps();                               // composition frames -> seconds
  const snap = (t) => Math.round(t * fps()) / fps();        // land on a frame
  const F60 = (n) => n / 60;                                 // timing tables are authored in 60ths

  function toEls(target, scope) {
    if (target == null) return [];
    if (typeof target === 'string') return Array.from((scope || doc).querySelectorAll(target));
    if (target.nodeType === 1) return [target];
    if (typeof target.length === 'number') return Array.from(target).flatMap((t) => toEls(t, scope));
    return [target];
  }
  const el1 = (target, scope) => toEls(target, scope)[0];

  function rootDuration(fromEl) {
    const host = fromEl && fromEl.closest ? fromEl.closest('[data-duration]') : null;
    const r = host || (doc && doc.querySelector('[data-composition-id][data-duration]'));
    return r ? Number(r.getAttribute('data-duration')) || 0 : 0;
  }

  // Drive: run fn(t) for every rendered time in [start, end], pure function of t. A property
  // setter is used so silent seeks (scrub, render) still call it. Before start it holds fn(start);
  // after end it holds fn(end). One driver per property per element. GSAP rounds tweened numbers to
  // 6 decimals, so times within a microsecond of either end snap to it (holds land exactly on keys).
  function drive(tl, start, end, fn) {
    const p = {};
    const d = Math.max(1e-4, end - start), stop = end - start >= 1e-4 ? end : start + d;
    let cur = start;
    Object.defineProperty(p, 't', {
      get() { return cur; },
      set(v) { cur = v <= start + 1e-6 ? start : v >= stop - 1e-6 ? stop : v; fn(cur); },
      enumerable: true,
      configurable: true,
    });
    tl.fromTo(p, { t: start }, { t: stop, duration: d, ease: 'none', immediateRender: true, lazy: false }, start);
    fn(start);
    return p;
  }

  // ------------------------------------------------------------------ curves

  // Cubic bezier ease: the same numbers as CSS cubic-bezier(), an AE speed graph, Blender handles.
  function bez(x1, y1, x2, y2) {
    const cx = 3 * x1, bx = 3 * (x2 - x1) - cx, ax = 1 - cx - bx;
    const cy = 3 * y1, by = 3 * (y2 - y1) - cy, ay = 1 - cy - by;
    const sx = (t) => ((ax * t + bx) * t + cx) * t;
    const sy = (t) => ((ay * t + by) * t + cy) * t;
    const dx = (t) => (3 * ax * t + 2 * bx) * t + cx;
    const solve = (x) => {
      let t = x;
      for (let i = 0; i < 8; i++) {
        const e = sx(t) - x, d = dx(t);
        if (Math.abs(e) < 1e-6) return t;
        if (Math.abs(d) < 1e-6) break;
        t -= e / d;
      }
      let lo = 0, hi = 1;
      t = x;
      for (let i = 0; i < 40; i++) {
        const v = sx(t);
        if (Math.abs(v - x) < 1e-7) break;
        if (v < x) lo = t; else hi = t;
        t = (lo + hi) / 2;
      }
      return t;
    };
    const fn = (p) => (p <= 0 ? 0 : p >= 1 ? 1 : sy(solve(p)));
    fn.points = [x1, y1, x2, y2];
    return fn;
  }

  // AE graph editor -> bezier. Influence is the handle length in % (AE's Keyframe Velocity dialog),
  // speed is the handle's slope relative to the segment's average speed (0 = eased to a stop,
  // 1 = average speed, >1 = arrives/leaves faster). influence(33.33, 33.33) is AE's Easy Ease (F9).
  function influence(outInf = 33.33, inInf = 33.33, outSpeed = 0, inSpeed = 0) {
    const a = clamp(outInf, 0.1, 100) / 100, b = clamp(inInf, 0.1, 100) / 100;
    return bez(a, outSpeed * a, 1 - b, 1 - inSpeed * b);
  }

  // Motion-design curves (from motion-kit, AE practice: Easy Ease with influence dragged to 70-90%).
  const C = {
    land: bez(0.1, 0.75, 0.15, 1),    // arrives at speed, long confident settle
    heavy: bez(0.75, 0, 0.18, 1),     // slow push-off, decisive arrival (big objects, camera)
    whip: bez(0.85, 0, 0.15, 1),      // hang, snap, hang (state changes, transitions)
    reveal: bez(0.22, 1, 0.36, 1),    // almost all travel in the first third (masked type)
    leave: bez(0.55, 0, 0.9, 0.35),   // accelerates out, never settles (exits)
    wind: bez(0.45, 0, 0.55, 1),      // anticipation counter-move
    drift: bez(0.4, 0, 0.6, 1),       // camera breath
    // added here
    glide: bez(0.6, 0.05, 0.1, 1),    // camera travel that lands just before the payoff
    snap: bez(0.2, 0.9, 0.1, 1),      // UI state change, crisp with a short tail
    accel: bez(0.5, 0, 0.75, 0.25),   // into a seam: ends at 3x average speed
    decel: bez(0.25, 0.75, 0.5, 1),   // out of a seam: starts at 3x average speed
  };

  const LIN = (p) => clamp01(p);
  const HOLD = (p) => (p >= 1 ? 1 : 0);
  const B = (x1, y1, x2, y2) => bez(x1, y1, x2, y2);
  const LIB = {
    // AE keyframe assistant equivalents
    'ae.easy': influence(33.33, 33.33), 'ae.easyIn': influence(16.67, 33.33, 1, 0), 'ae.easyOut': influence(33.33, 16.67, 0, 1),
    'ae.arrive': influence(10, 85, 1, 0), 'ae.depart': influence(85, 10, 0, 1), 'ae.strong': influence(85, 85),
    // AE speed-graph presets named by what the move does (from motion-pro; its ae.arrive differs, ours stays)
    'ae.easyEase': influence(33.33, 33.33), 'ae.ease60': influence(60, 60), 'ae.ease75': influence(75, 75), 'ae.ease90': influence(90, 90),
    'ae.punch': influence(8, 88, 9, 0),     // bursts off the key, long settle: hits, slams, landings
    'ae.glide': influence(70, 85),          // camera: steady push-off, long confident settle
    'ae.launch': influence(85, 12, 0, 5),   // hangs, then leaves at speed: exits, zoom-throughs
    'ae.snap': influence(92, 92),           // hang-snap-hang: state changes, whips
    // easings.net (Penner families as CSS cubic-beziers)
    'easings.inSine': B(0.12, 0, 0.39, 0), 'easings.outSine': B(0.61, 1, 0.88, 1), 'easings.inOutSine': B(0.37, 0, 0.63, 1),
    'easings.inQuad': B(0.11, 0, 0.5, 0), 'easings.outQuad': B(0.5, 1, 0.89, 1), 'easings.inOutQuad': B(0.45, 0, 0.55, 1),
    'easings.inCubic': B(0.32, 0, 0.67, 0), 'easings.outCubic': B(0.33, 1, 0.68, 1), 'easings.inOutCubic': B(0.65, 0, 0.35, 1),
    'easings.inQuart': B(0.5, 0, 0.75, 0), 'easings.outQuart': B(0.25, 1, 0.5, 1), 'easings.inOutQuart': B(0.76, 0, 0.24, 1),
    'easings.inQuint': B(0.64, 0, 0.78, 0), 'easings.outQuint': B(0.22, 1, 0.36, 1), 'easings.inOutQuint': B(0.83, 0, 0.17, 1),
    'easings.inExpo': B(0.7, 0, 0.84, 0), 'easings.outExpo': B(0.16, 1, 0.3, 1), 'easings.inOutExpo': B(0.87, 0, 0.13, 1),
    'easings.inCirc': B(0.55, 0, 1, 0.45), 'easings.outCirc': B(0, 0.55, 0.45, 1), 'easings.inOutCirc': B(0.85, 0, 0.15, 1),
    'easings.inBack': B(0.36, 0, 0.66, -0.56), 'easings.outBack': B(0.34, 1.56, 0.64, 1), 'easings.inOutBack': B(0.68, -0.6, 0.32, 1.6),
    // Material 3
    'm3.standard': B(0.2, 0, 0, 1), 'm3.standardDecelerate': B(0, 0, 0, 1), 'm3.standardAccelerate': B(0.3, 0, 1, 1),
    'm3.emphasizedDecelerate': B(0.05, 0.7, 0.1, 1), 'm3.emphasizedAccelerate': B(0.3, 0, 0.8, 0.15),
    'm3.legacy': B(0.4, 0, 0.2, 1), 'm3.legacyDecelerate': B(0, 0, 0.2, 1), 'm3.legacyAccelerate': B(0.4, 0, 1, 1),
    // IBM Carbon
    'carbon.productive.standard': B(0.2, 0, 0.38, 0.9), 'carbon.productive.entrance': B(0, 0, 0.38, 0.9), 'carbon.productive.exit': B(0.2, 0, 1, 0.9),
    'carbon.expressive.standard': B(0.4, 0.14, 0.3, 1), 'carbon.expressive.entrance': B(0, 0, 0.3, 1), 'carbon.expressive.exit': B(0.4, 0.14, 1, 1),
    // speed ramps for ramp(): output time -> section time, flat = slow motion
    'ramp.slowMid': B(0.1, 0.6, 0.9, 0.4), 'ramp.speedUp': B(0.6, 0, 0.9, 0.55), 'ramp.slowDown': B(0.1, 0.45, 0.4, 1),
  };
  Object.keys(C).forEach((k) => { LIB['kit.' + k] = C[k]; });

  // Physical spring (damped oscillator) normalised to land exactly on 1. Returns { ease, duration }:
  // the settle time IS the physics, so use both. damping 1 = no overshoot, 0.75-0.85 = felt not seen,
  // 0.55-0.7 = visible settle. Transforms only: it passes 1, never put it on opacity or colour.
  // Or set it like a motion designer (from motion-pro): spring({ overshoot: 10, duration: 0.6 })
  // swings 10% past the target and settles in 0.6 s. overshoot is in percent (a value below 1 is read
  // as a share, so 0.1 is also 10%); duration sets the response. damping wins over overshoot,
  // response over duration.
  function spring(opts) {
    const o = opts || {};
    const damping = o.damping != null ? o.damping : o.overshoot != null ? dampingFor(o.overshoot) : 0.8;
    const w = 2 * Math.PI; // response 1: the shape depends on damping only, response scales time
    const pos = (t) => {
      if (damping >= 1) return 1 - Math.exp(-w * t) * (1 + w * t);
      const wd = w * Math.sqrt(1 - damping * damping);
      return 1 - Math.exp(-damping * w * t) * (Math.cos(wd * t) + ((damping * w) / wd) * Math.sin(wd * t));
    };
    let T1 = 4;
    for (let i = 400; i >= 0; i--) {
      const t = (i / 400) * 4;
      if (Math.abs(1 - pos(t)) > 0.002) { T1 = ((i + 1) / 400) * 4; break; }
    }
    const response = o.response != null ? o.response : o.duration != null ? o.duration / T1 : 0.45;
    const end = pos(T1);
    const ease = (p) => (p <= 0 ? 0 : p >= 1 ? 1 : pos(p * T1) + p * (1 - end));
    return { ease, duration: response * T1, response, damping };
  }
  // Damping ratio for an overshoot in percent: overshoot = e^(-z*pi/sqrt(1-z^2)), solved for z.
  function dampingFor(pct) {
    const os = pct >= 1 ? pct / 100 : pct;
    if (!(os > 0)) return 1;
    const l = Math.log(Math.min(os, 0.95));
    return -l / Math.sqrt(Math.PI * Math.PI + l * l);
  }

  // Resolve anything to an ease function: a function, [x1,y1,x2,y2], 'kit.land', 'ae.easy',
  // 'spring(0.45,0.8)', 'cubic-bezier(...)', 'hold', 'linear', {influence:[o,i], speed:[o,i]},
  // AE handles {out, in, outVel, inVel} (motion-pro's ae()), a spring {response, damping | overshoot},
  // or (last resort) a GSAP ease string you chose on purpose.
  function ease(e, fallback) {
    if (e == null) return fallback !== undefined ? fallback : LIB['ae.easy'];
    if (typeof e === 'function') return e;
    if (Array.isArray(e)) return bez(e[0], e[1], e[2], e[3]);
    if (typeof e === 'object') {
      if (e.influence) return influence(e.influence[0], e.influence[1], (e.speed || [])[0] || 0, (e.speed || [])[1] || 0);
      if (e.response != null || e.damping != null || e.overshoot != null) return spring(e).ease;
      if (e.out != null || e.in != null) return influence(e.out != null ? e.out : 33.33, e.in != null ? e.in : 33.33, e.outVel || 0, e.inVel || 0);
      return fallback || LIB['ae.easy'];
    }
    const s = String(e).trim();
    if (LIB[s]) return LIB[s];
    if (s === 'linear' || s === 'none') return LIN;
    if (s === 'hold') return HOLD;
    if (s === 'spring') return spring({}).ease;
    let m = s.match(/^spring\(\s*([\d.]+)\s*(?:,\s*([\d.]+))?\s*\)$/);
    if (m) return spring({ response: +m[1], damping: m[2] != null ? +m[2] : 0.8 }).ease;
    m = s.match(/^cubic-bezier\(([^)]+)\)$/);
    if (m) { const v = m[1].split(',').map(Number); return bez(v[0], v[1], v[2], v[3]); }
    const parsed = root.gsap && root.gsap.parseEase(s);
    if (parsed) return parsed;
    throw new Error('ae-motion: unknown ease "' + s + '"');
  }
  const curve = (name) => {
    if (!LIB[name]) throw new Error('ae-motion: no curve "' + name + '"');
    return LIB[name];
  };

  // Slopes of an ease at its ends (speed relative to average). Used to match speed across a seam.
  const startSlope = (fn) => fn(1e-3) / 1e-3;
  const endSlope = (fn) => (1 - fn(1 - 1e-3)) / 1e-3;

  // Inertial bounce (the AE expression): keeps arrival speed and rings past the target, decaying.
  // Wrap an ease that ends moving (linear, an ease-in, kit.leave, kit.accel). Transforms only.
  function settle(e, seconds, opts) {
    const o = opts || {};
    const base = ease(e, LIN), share = o.share != null ? o.share : 0.45, freq = o.freq != null ? o.freq : 2.4, decay = o.decay != null ? o.decay : 6;
    const T = 1 - share, w = 2 * Math.PI * freq, h = 1e-3;
    const v = (base(1) - base(1 - h)) / h / (T * seconds);
    return (p) => {
      if (p <= 0) return 0;
      if (p >= 1) return 1;
      if (p < T) return base(p / T);
      const tau = (p - T) * seconds, s = (p - T) / share;
      return 1 + (v * Math.sin(w * tau) / w) * Math.exp(-decay * tau) * (1 - s * s * s);
    };
  }

  // ------------------------------------------------------------------ timing

  // Duration from distance and weight (motion-kit): (9 + 1.15 * sqrt(px)) * weight, in 60ths,
  // snapped to composition frames. weight 0.7 light (chips, labels), 1 normal, 1.35 heavy (panels).
  function dur(distancePx, weight) {
    const frames = (9 + 1.15 * Math.sqrt(Math.max(0, distancePx))) * (weight == null ? 1 : weight);
    return Math.max(F(1), snap(F60(frames)));
  }
  // Uneven reaction offsets: followers answer the lead quickly, then less so. Never an even stagger.
  const REACT = [0, 4, 9, 15, 22, 30];
  const react = (i, scale) => snap(F60((REACT[i] != null ? REACT[i] : REACT[REACT.length - 1] + 8 * (i - REACT.length + 1)) * (scale == null ? 1 : scale)));
  // Beat grid: beat n computed from its index (never accumulated), snapped to frames, so 32 beats
  // at 128 BPM do not drift. Pass the JSON from scripts/hits.py (or `npx hyperframes beats --json`)
  // instead of a bpm for the track's real beat sheet (beatSheet below).
  const beats = (bpm, offset) => (bpm && typeof bpm === 'object' ? beatSheet(bpm) : (n) => snap((offset || 0) + (n * 60) / bpm));
  const grid = beats; // motion-kit name
  // Beat sheet from hits.py: b(n) is beat n (past the list it continues at the tempo), b.near(t),
  // b.after(t), b.downbeat(i), b.onsetNear(t), b.onsetAfter(t); b.hits, b.lifts, b.dips as given.
  // Every time comes back snapped to a frame.
  function beatSheet(j) {
    const B = (j.beats || j.beatTimes || []).map(Number), D = (j.downbeats || []).map(Number), O = (j.onsets || []).map(Number);
    const per = j.bpm ? 60 / j.bpm : 0.5;
    const near = (list, t) => list.reduce((best, x) => (Math.abs(x - t) < Math.abs(best - t) ? x : best), list.length ? list[0] : t);
    const after = (list, t) => { for (let i = 0; i < list.length; i++) if (list[i] >= t - 1e-6) return list[i]; return t; };
    const f = (n) => snap(n < B.length ? B[n] : (B.length ? B[B.length - 1] : j.offset || 0) + (n - Math.max(0, B.length - 1)) * per);
    f.near = (t) => snap(near(B, t));
    f.after = (t) => snap(after(B, t));
    f.downbeat = (i) => snap(D[i] != null ? D[i] : f(i * 4));
    f.onsetNear = (t) => snap(near(O, t));
    f.onsetAfter = (t) => snap(after(O, t));
    f.bpm = j.bpm; f.list = B; f.hits = j.hits || []; f.lifts = j.lifts || []; f.dips = j.dips || [];
    return f;
  }
  // Land a visual hit on (or one frame before) an audio transient. Never after it.
  const hit = (t, leadFrames) => snap(t) - F(leadFrames == null ? 1 : leadFrames);

  // Word cues from a transcript: [{text|word|w, start|s, end|e}]. cue.at('claude') -> start of the
  // first "claude"; cue.at('claude', 2) the second; cue.at(14) the 15th word; cue.after('so', 3.2).
  function words(list) {
    const norm = (s) => String(s).toLowerCase().replace(/[^\p{L}\p{N}']+/gu, '');
    const W = (list || []).map((w, i) => ({
      i,
      text: w.text != null ? w.text : w.word != null ? w.word : w.w,
      start: Number(w.start != null ? w.start : w.s),
      end: Number(w.end != null ? w.end : w.e != null ? w.e : w.start != null ? w.start : w.s),
    }));
    const find = (q, nth, after) => {
      if (typeof q === 'number') return W[q];
      let k = nth || 1;
      const qs = String(q).trim().split(/\s+/).map(norm);
      for (let i = 0; i < W.length; i++) {
        if (W[i].start < (after || -Infinity)) continue;
        let ok = true;
        for (let j = 0; j < qs.length; j++) if (!W[i + j] || norm(W[i + j].text) !== qs[j]) { ok = false; break; }
        if (ok && --k === 0) return Object.assign({}, W[i], { end: W[i + qs.length - 1].end });
      }
      throw new Error('ae-motion: word "' + q + '" not found');
    };
    return {
      list: W,
      word: find,
      at: (q, nth) => find(q, nth).start,
      end: (q, nth) => find(q, nth).end,
      after: (q, t) => find(q, 1, t).start,
      between: (t0, t1) => W.filter((w) => w.start >= t0 && w.start < t1),
    };
  }

  // ------------------------------------------------------------------ keyframe tracks

  // track([[t, v, ease], ...]) -> f(t). ease is the curve INTO that key (AE's incoming segment).
  // t may be '+0.4' (relative to the previous key). v is a number or an array of numbers.
  // f.velocity(t) is units per second; f.start / f.end bound the keys.
  // interp: 'auto' is AE's continuous (auto) bezier, from motion-pro: the value passes exactly
  // through every key and its speed is continuous across it, so a move glides through the middle
  // keys instead of stopping at each. The first and last keys ease to rest; a key marked 'stop'
  // (third element, or stop: true) comes to rest; a key with its own ease makes the segment into it
  // a plain eased segment (both its keys rest). A local peak gets zero speed so nothing swings past
  // a key (monotone: false allows it). tension 0..1 tightens toward ease in/out at every key.
  // log: true interpolates in log space (zoom, scale, distance feel even; values must be > 0).
  function track(keys, opts) {
    const o = opts || {};
    const def = ease(o.ease, LIB['ae.easy']);
    const auto = o.interp === 'auto';
    let prev = 0;
    const K = keys.map((k) => {
      const raw = Array.isArray(k) ? { t: k[0], v: k[1], e: k[2] } : { t: k.t, v: k.v, e: k.ease, stop: k.stop };
      const t = typeof raw.t === 'string' && raw.t[0] === '+' ? prev + parseFloat(raw.t.slice(1)) : Number(raw.t);
      prev = t;
      const marker = raw.e === 'stop' || raw.e === 'auto';
      return { t, v: raw.v, e: marker ? null : raw.e, stop: !!raw.stop || raw.e === 'stop' };
    });
    if (!K.length) throw new Error('ae-motion: track needs at least one key');
    K.forEach((k, i) => { k.fn = !i ? null : auto ? (k.e != null ? ease(k.e) : null) : ease(k.e, def); });
    const isArr = Array.isArray(K[0].v);
    const n = K.length, comps = isArr ? K[0].v.length : 1;
    const fwd = o.log ? Math.log : (x) => x, back = o.log ? Math.exp : (x) => x;
    const VL = K.map((k) => (isArr ? k.v : [k.v]).map(fwd));            // key values in interpolation space
    const mix = (i, u) => {
      const a = VL[i - 1], b = VL[i];
      return isArr ? a.map((x, j) => back(x + (b[j] - x) * u)) : back(a[0] + (b[0] - a[0]) * u);
    };
    // auto slopes: non-uniform Catmull-Rom, zero at peaks, Fritsch-Carlson limit so it never overshoots
    const monotone = o.monotone !== false, tension = clamp01(o.tension || 0);
    const M = !auto ? null : VL.map((v, i) => v.map((x, c) => {
      if (i === 0 || i === n - 1 || K[i].stop || K[i].fn || K[i + 1].fn) return 0;
      const h0 = K[i].t - K[i - 1].t, h1 = K[i + 1].t - K[i].t;
      if (h0 <= 0 || h1 <= 0) return 0;
      const d0 = (x - VL[i - 1][c]) / h0, d1 = (VL[i + 1][c] - x) / h1;
      if (monotone && d0 * d1 <= 0) return 0;
      const m = (d0 * h1 + d1 * h0) / (h0 + h1);
      const lim = monotone ? 3 * Math.min(Math.abs(d0), Math.abs(d1)) : Infinity;
      return Math.sign(m) * Math.min(Math.abs(m), lim) * (1 - tension);
    }));
    const hermite = (i, u, span) => {
      const s2 = u * u, s3 = s2 * u;
      const h00 = 2 * s3 - 3 * s2 + 1, h10 = s3 - 2 * s2 + u, h01 = -2 * s3 + 3 * s2, h11 = s3 - s2;
      const out = [];
      for (let c = 0; c < comps; c++) out.push(back(h00 * VL[i - 1][c] + h10 * span * M[i - 1][c] + h01 * VL[i][c] + h11 * span * M[i][c]));
      return isArr ? out : out[0];
    };
    const f = (t) => {
      if (t <= K[0].t) return K[0].v;
      const last = K[n - 1];
      if (t >= last.t) return last.v;
      let i = 1;
      while (i < n - 1 && K[i].t < t) i++;
      const a = K[i - 1], b = K[i], span = b.t - a.t;
      if (span <= 0) return b.v;
      const u = (t - a.t) / span;
      return b.fn ? mix(i, b.fn(u)) : hermite(i, u, span);
    };
    // units per second; zero outside the keyed window (a held value isn't moving), one-sided at the ends
    f.velocity = (t, h) => {
      const d = h || 1 / 480, t0 = K[0].t, t1 = K[K.length - 1].t;
      if (t <= t0 || t >= t1) return isArr ? K[0].v.map(() => 0) : 0;
      const ta = Math.max(t0, t - d), tb = Math.min(t1, t + d), a = f(ta), b = f(tb), span = tb - ta || d;
      return isArr ? a.map((x, j) => (b[j] - x) / span) : (b - a) / span;
    };
    f.start = K[0].t;
    f.end = K[K.length - 1].t;
    f.keys = K;
    return f;
  }
  const constant = (v) => { const f = () => v; f.velocity = () => 0; f.start = Infinity; f.end = -Infinity; return f; };
  const asTrack = (v, opts) => (typeof v === 'function' ? v : Array.isArray(v) && Array.isArray(v[0]) ? track(v, opts) : constant(v));

  // keys(tl, el, { x: [[0,-400],[0.6,0,'kit.land']], opacity: [[0,0],[0.1,1,'linear']] }, opts)
  // An AE layer: every property is its own keyframe track, evaluated at timeline time.
  // opts.ease is the default curve, opts.units { letterSpacing: 'em' }, opts.from / opts.until
  // widen the driven window, opts.smear turns on pixel motion blur from x/y velocity
  // ({ shutter: 180, max: 40 }). Don't also tween these properties with GSAP.
  function keys(tl, target, props, opts) {
    const o = opts || {};
    const els = toEls(target);
    const tracks = {};
    let start = Infinity, end = -Infinity;
    Object.keys(props).forEach((k) => {
      const tr = asTrack(props[k], o);
      tracks[k] = tr;
      if (isFinite(tr.start)) start = Math.min(start, tr.start);
      if (isFinite(tr.end)) end = Math.max(end, tr.end);
    });
    if (!isFinite(start)) start = 0;
    if (!isFinite(end)) end = start;
    if (o.from != null) start = o.from;
    if (o.until != null) end = o.until;
    const units = o.units || {};
    const sm = o.smear ? smearer(els, o.smear === true ? {} : o.smear) : null;
    const apply = (t) => {
      const v = {};
      Object.keys(tracks).forEach((k) => {
        const val = tracks[k](t);
        v[k] = units[k] ? val + units[k] : val;
      });
      G().set(els, v);
      if (sm) sm(t, tracks);
    };
    drive(tl, start, end, apply);
    return { tracks, start, end, value: (k, t) => tracks[k](t), velocity: (k, t) => tracks[k].velocity(t) };
  }

  // ------------------------------------------------------------------ smear (pixel motion blur)

  // A directional SVG blur whose length follows real velocity: displacement per frame times the
  // shutter fraction. Deterministic, per element, no global sampling. Use it on a few hero movers or
  // inside transitions; for whole-composition blur use HyperFrames' data-motion-blur on the root
  // (and data-motion-blur="off" on anything already smeared here). It owns the element's CSS filter.
  let defs = null, fid = 0;
  function defsFor(el) {
    if (defs && defs.isConnected) return defs;
    defs = doc.createElementNS(NS, 'svg');
    defs.setAttribute('width', '0');
    defs.setAttribute('height', '0');
    defs.setAttribute('aria-hidden', 'true');
    defs.setAttribute('data-ae-defs', '');
    defs.style.cssText = 'position:absolute;left:0;top:0;width:0;height:0;overflow:hidden;pointer-events:none';
    const host = (el && el.closest && el.closest('[data-composition-id]')) || doc.body;
    host.appendChild(defs);
    return defs;
  }
  function smearFilter(el) {
    if (el._aeSmear) return el._aeSmear;
    const f = doc.createElementNS(NS, 'filter');
    const id = 'ae-smear-' + (++fid);
    f.setAttribute('id', id);
    f.setAttribute('x', '-50%'); f.setAttribute('y', '-50%');
    f.setAttribute('width', '200%'); f.setAttribute('height', '200%');
    f.setAttribute('color-interpolation-filters', 'sRGB');
    const b = doc.createElementNS(NS, 'feGaussianBlur');
    b.setAttribute('stdDeviation', '0 0');
    b.setAttribute('edgeMode', 'none');
    f.appendChild(b);
    defsFor(el).appendChild(f);
    el._aeSmear = { id, b, on: false };
    return el._aeSmear;
  }
  function setSmear(el, sx, sy) {
    const s = smearFilter(el);
    const x = Math.round(sx * 10) / 10, y = Math.round(sy * 10) / 10;
    if (x < 0.25 && y < 0.25) {
      if (s.on) { el.style.filter = ''; s.on = false; }
      return;
    }
    s.b.setAttribute('stdDeviation', x + ' ' + y);
    if (!s.on) { el.style.filter = 'url(#' + s.id + ')'; s.on = true; }
  }
  function smearer(els, o) {
    const shutter = (o.shutter != null ? o.shutter : 180) / 360, max = o.max != null ? o.max : 40, k = o.strength != null ? o.strength : 0.5;
    return (t, tracks) => {
      const vx = tracks.x ? tracks.x.velocity(t) : 0;
      const vy = tracks.y ? tracks.y.velocity(t) : 0;
      const sx = Math.min(max, (Math.abs(vx) / fps()) * shutter * k);
      const sy = Math.min(max, (Math.abs(vy) / fps()) * shutter * k);
      // x/y move in the parent's pixels but the filter blurs in the element's own (scaled) units: divide by its scale,
      // or a card at 13x smears 13 times too far (`max` is in screen pixels)
      els.forEach((e) => {
        const gx = Math.abs(Number(G().getProperty(e, 'scaleX'))) || 1, gy = Math.abs(Number(G().getProperty(e, 'scaleY'))) || 1;
        setSmear(e, sx / gx, sy / gy);
      });
    };
  }
  // Manual smear driven by your own function of time: smear(tl, el, at, until, (t) => [sx, sy]).
  function smear(tl, target, at, until, fn) {
    const els = toEls(target);
    drive(tl, at, until, (t) => { const s = fn(t) || [0, 0]; els.forEach((e) => setSmear(e, s[0], s[1])); });
  }

  // ------------------------------------------------------------------ noise and wiggle

  function noise1(x, seed) {
    const h = (n) => { const s = Math.sin((n + seed * 101.3) * 127.1) * 43758.5453; return (s - Math.floor(s)) * 2 - 1; };
    const i = Math.floor(x), f = x - i, u = f * f * (3 - 2 * f);
    return h(i) * (1 - u) + h(i + 1) * u;
  }
  // AE wiggle(freq, amp) as two octaves of seeded smooth noise: same frame every render.
  const wig = (t, freq, seed) => noise1(t * freq, seed) * 0.7 + noise1(t * freq * 2.1, seed + 7) * 0.3;
  // Seeded hash in [0, 1) and a seeded random sequence (mulberry32). Never Math.random().
  const hash01 = (n, seed) => { const s = Math.sin((n + seed * 101.3) * 127.1) * 43758.5453; return s - Math.floor(s); };
  function rng(seed) {
    let a = ((seed == null ? 1 : seed) * 2654435761) >>> 0;
    return () => {
      a = (a + 0x6d2b79f5) >>> 0;
      let t = a;
      t = Math.imul(t ^ (t >>> 15), t | 1);
      t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }

  // Impact shake offset u seconds after a hit (from motion-pro): seeded noise under a decaying
  // envelope, exactly 0 from `duration` on. Pure; used by shake() and camera3d's shake.
  function shakeAt(u, o) {
    const d = o.duration, k = u < 0 || u > d ? 0 : Math.exp(-o.decay * u) * (1 - u / d);
    return { x: k * o.amp * noise1(u * o.freq, o.seed), y: k * o.amp * noise1(u * o.freq, o.seed + 5), rotation: k * o.rot * noise1(u * o.freq, o.seed + 9) };
  }
  const shakeOpts = (at, s, def) => {
    const q = s || {};
    const pick = (k) => (q[k] != null ? q[k] : def[k]);
    return { amp: pick('amp'), rot: pick('rot'), freq: pick('freq'), decay: pick('decay'), duration: pick('duration'), seed: q.seed != null ? q.seed : Math.round(at * 100) };
  };

  // shake(tl, wrapper, at, { amp: 10, rot: 0.6, freq: 24, decay: 8, duration: 0.5, seed })
  // Impact shake on a layer (a slam, a bass hit), still before the hit and after `duration`. On a
  // wrapper only: it owns the wrapper's x, y and rotation. For the 3D camera use camera3d's shake.
  // A hit, not a look: one to three in a film. The owner's YouTube intros ban shakes.
  function shake(tl, target, at, opts) {
    const els = toEls(target);
    const q = shakeOpts(at, opts, { amp: 10, rot: 0.6, freq: 24, decay: 8, duration: 0.5 });
    drive(tl, Math.max(0, at - F(1)), at + q.duration, (t) => G().set(els, t < at ? { x: 0, y: 0, rotation: 0 } : shakeAt(t - at, q)));
  }

  // wiggle(tl, wrapper, { x: 6, y: 4, rotation: 0.5 }, { freq, at, until, seed, fadeIn })
  // On a wrapper only: GSAP is not additive, so never on an element other tweens move.
  function wiggle(tl, target, amps, opts) {
    const o = opts || {};
    const els = toEls(target);
    const at = o.at || 0, until = o.until != null ? o.until : rootDuration(els[0]) || tl.duration();
    const freq = o.freq != null ? o.freq : 1, seed = o.seed != null ? o.seed : 1, fadeIn = o.fadeIn != null ? o.fadeIn : 0.4;
    drive(tl, at, until, (t) => {
      const k = clamp01((t - at) / Math.max(1e-6, fadeIn)), vals = {};
      Object.keys(amps).forEach((prop, j) => {
        const rest = /^scale/.test(prop) ? 1 : 0;
        vals[prop] = rest + k * amps[prop] * wig(t, freq, seed + j * 13);
      });
      G().set(els, vals);
    });
  }

  // ------------------------------------------------------------------ camera (2.5D)

  // camera(tl, '#stage', {
  //   layers: [{ el: '#bg', z: 1400 }, { el: '#mid', z: 0 }, { el: '#fg', z: -300 }]   // or data-z on children
  //   x: [[0, -120], [2.2, 0, 'kit.glide']],   y: 0,   z: [[0, -500], [2.2, 0, 'kit.heavy']],   // dolly
  //   zoom: 1, roll: [[0, -1.2], [2.4, 0, 'kit.heavy']],
  //   handheld: { x: 4, y: 3, roll: 0.15, freq: 0.5, seed: 3 },
  //   focus: [[0, 0]], dof: { amount: 6, max: 8 },     // blur px per 1000 depth units, off by default
  //   focal: 1200, until: 5 })
  // Layers are full-frame boxes scaled about the frame centre. z > 0 is behind the focal plane;
  // with compensate (default) every layer looks as authored when the camera rests, and moves with
  // true parallax when it pans or dollies. The camera owns each layer's transform: animate children.
  function camera(tl, stage, opts) {
    const o = opts || {};
    const st = el1(stage);
    const focal = o.focal != null ? o.focal : 1200;
    const compensate = o.compensate !== false;
    const list = o.layers || Array.from(st.children).filter((c) => c.hasAttribute('data-z')).map((c) => ({ el: c }));
    const layers = list.map((l) => {
      const e = el1(l.el, st);
      const z = l.z != null ? l.z : Number(e.getAttribute('data-z')) || 0;
      if (root.getComputedStyle && getComputedStyle(e).position === 'static') { e.style.position = 'absolute'; e.style.inset = '0'; }
      e.style.transformOrigin = '50% 50%';
      return { el: e, z, fixed: !!l.fixed || e.hasAttribute('data-camera-fixed'), k: compensate ? (focal + z) / focal : 1, shown: true };
    });
    const tr = {
      x: asTrack(o.x != null ? o.x : 0, o), y: asTrack(o.y != null ? o.y : 0, o), z: asTrack(o.z != null ? o.z : 0, o),
      zoom: asTrack(o.zoom != null ? o.zoom : 1, o), roll: asTrack(o.roll != null ? o.roll : 0, o),
      focus: asTrack(o.focus != null ? o.focus : 0, o),
    };
    const hh = o.handheld || null, dof = o.dof || null;
    let start = Infinity, end = -Infinity;
    Object.keys(tr).forEach((k) => { if (isFinite(tr[k].start)) start = Math.min(start, tr[k].start); if (isFinite(tr[k].end)) end = Math.max(end, tr[k].end); });
    if (!isFinite(start)) start = 0;
    if (o.from != null) start = o.from;
    if (o.until != null) end = o.until;
    else if (hh || !isFinite(end)) end = Math.max(isFinite(end) ? end : 0, rootDuration(st) || tl.duration());
    const at = (t) => {
      let x = tr.x(t), y = tr.y(t), roll = tr.roll(t);
      if (hh) {
        const fade = clamp01((t - start) / (hh.fadeIn != null ? hh.fadeIn : 0.6));
        const f = hh.freq != null ? hh.freq : 0.5, s = hh.seed != null ? hh.seed : 3;
        x += fade * (hh.x || 0) * wig(t, f, s);
        y += fade * (hh.y || 0) * wig(t, f, s + 31);
        roll += fade * (hh.roll || 0) * wig(t, f * 0.8, s + 57);
      }
      return { x, y, z: tr.z(t), zoom: tr.zoom(t), roll, focus: tr.focus(t) };
    };
    const apply = (t) => {
      const c = at(t);
      layers.forEach((l) => {
        if (l.fixed) return;
        const d = focal + l.z - c.z;
        if (d <= 1) { if (l.shown) { l.el.style.display = 'none'; l.shown = false; } return; }
        if (!l.shown) { l.el.style.display = ''; l.shown = true; }
        const s = (focal / d) * c.zoom;
        const tx = -c.x * s, ty = -c.y * s;
        l.el.style.transform = 'rotate(' + c.roll.toFixed(4) + 'deg) translate(' + tx.toFixed(2) + 'px,' + ty.toFixed(2) + 'px) scale(' + (s * l.k).toFixed(5) + ')';
        if (dof) {
          const b = Math.min(dof.max != null ? dof.max : 10, ((dof.amount != null ? dof.amount : 6) * Math.abs(l.z - c.focus)) / 1000);
          l.el.style.filter = b > 0.2 ? 'blur(' + b.toFixed(2) + 'px)' : '';
        }
      });
    };
    drive(tl, start, end, apply);
    return { tracks: tr, layers, at, start, end };
  }

  // ------------------------------------------------------------------ camera3d (true 3D)

  // camera3d(tl, { viewport: '#vp', world: '#world', perspective: 2000,
  //   keys: [{ t: 0,   target: [960, 540, 0], fw: 3000, rx: 24, ry: -12 },     // fw = px of width framed at the target
  //          { t: 0.5, target: [960, 520, 0], fw: 2080, rx: 7, stop: true },  // arrives as the title lands
  //          { t: 4,   target: [1400, 580, 600], fw: 1600, ry: 30, focus: 600 }],   // orbit, rack focus to z 600
  //   handheld: { amp: 2.5 }, shake: [{ at: 0.5, amp: 22 }], dof: { strength: 9 } })
  // A real CSS 3D camera (from motion-pro). Markup: <div id="vp"><div id="world"> layers with data-z
  // </div></div>; the world is a frame-sized box at 0,0. AE conventions: x right, y down, +z farther.
  // It is an orbit camera: it looks at `target` [x, y, z] from `dist` px (or frames `fw` px of width at
  // the target, or `zoom` = scale at the target), turned by rx (tilt), ry (orbit around the target)
  // and rz (roll). Keys interpolate those values, so arcs stay arcs, and glide through every key
  // without stopping (interp 'auto'; `stop: true` rests at a key; mode: 'segments' eases and settles at
  // every key, each key's `ease` the curve into it). dist moves in log space. focus follows the
  // target's depth unless you key it. Runs from `from` (0) to `until` (the composition's duration;
  // pass it on a page without data-duration).
  // Ownership: the camera writes the WORLD's CSS transform (never tween the world). Each layer's z is
  // a GSAP transform set once from data-z: animate layers' x, y, scale or rotation with GSAP or keys,
  // never z or a CSS transform string. dof owns the filter of its layers (data-dof; a filter flattens
  // a layer's 3D subtree, so keep it on flat cards). Nothing may come within ~150 px of the eye
  // plane (it tears), and far layers must still cover the frame at the widest framing.
  // Blur: HyperFrames' engine motion blur skips anything inside a preserve-3d world (the camera move
  // and every mover in it render sharp), so give fast movers in the world keys(..., { smear }) or
  // smear(), never on a data-dof layer (both own its filter: smear a child of it instead).
  // Chain or pass in opts: .keys(list, { mode, tension, ease }), .handheld({ amp, rot, freq, seed,
  // at, until }), .shake(at, { amp, rot, freq, decay, duration, seed }), .dof({ strength, max,
  // layers }), .offset(t => ({ tx, ty, tz, dist, rx, ry, rz })). cam.state(t) gives the values.
  function camera3d(tl, opts) {
    const o = opts || {};
    const vp = el1(o.viewport || '#vp'), world = el1(o.world || '#world', vp);
    if (!vp || !world) throw new Error('ae-motion: camera3d needs a viewport and a world element');
    const comp = vp.closest ? vp.closest('[data-width][data-height]') : null;
    const W = o.width || vp.offsetWidth || (comp ? Number(comp.getAttribute('data-width')) : 0) || 1080;
    const H = o.height || vp.offsetHeight || (comp ? Number(comp.getAttribute('data-height')) : 0) || 1920;
    const P = o.perspective || 2000;
    vp.style.perspective = P + 'px';
    vp.style.perspectiveOrigin = W / 2 + 'px ' + H / 2 + 'px';
    if (!vp.style.overflow) vp.style.overflow = 'hidden';
    world.style.transformStyle = 'preserve-3d';
    world.style.transformOrigin = W / 2 + 'px ' + H / 2 + 'px 0px';
    if (root.getComputedStyle && getComputedStyle(world).position === 'static') world.style.position = 'absolute';
    const zOf = (e) => Number(e.getAttribute('data-z')) || 0;
    const layers = toEls(o.layers || '[data-z]', world).map((e) => ({ el: e, z: zOf(e) }));
    layers.forEach((l) => G().set(l.el, { z: -l.z }));
    const PROPS = ['tx', 'ty', 'tz', 'dist', 'rx', 'ry', 'rz', 'focus'];
    const base = { tx: W / 2, ty: H / 2, tz: 0, dist: P, rx: 0, ry: 0, rz: 0, focus: 0 };
    const keyVals = (k) => {
      const out = {};
      const tg = Array.isArray(k.target) ? k.target : k.target ? [k.target.x, k.target.y, k.target.z] : null;
      if (tg) { out.tx = tg[0]; out.ty = tg[1]; out.tz = tg[2] || 0; }
      if (k.dist != null) out.dist = k.dist;
      if (k.fw != null) out.dist = (P * k.fw) / W;
      if (k.zoom != null) out.dist = P / k.zoom;
      ['rx', 'ry', 'rz', 'focus'].forEach((p) => { if (k[p] != null) out[p] = k[p]; });
      return out;
    };
    let tracks = null, focusKeyed = false, dof = null, drv = null;
    const add = [];
    const state = (t) => {
      const s = Object.assign({}, base);
      if (tracks) PROPS.forEach((p) => { if (p !== 'focus' || focusKeyed) s[p] = tracks[p](t); });
      if (!focusKeyed) s.focus = s.tz;
      add.forEach((fn) => { const d = fn(t); if (d) Object.keys(d).forEach((p) => { s[p] = (s[p] || 0) + d[p]; }); });
      return s;
    };
    const apply = (t) => {
      const s = state(t);
      world.style.transform = 'translateZ(' + (P - s.dist).toFixed(3) + 'px) rotateZ(' + s.rz.toFixed(4) + 'deg) rotateX(' + s.rx.toFixed(4) +
        'deg) rotateY(' + s.ry.toFixed(4) + 'deg) translate3d(' + (W / 2 - s.tx).toFixed(3) + 'px,' + (H / 2 - s.ty).toFixed(3) + 'px,' + s.tz.toFixed(3) + 'px)';
      if (dof) dof.layers.forEach((l) => {
        const b = Math.min(dof.max, (Math.abs(l.z - s.focus) / s.dist) * dof.strength);
        const v = b < 0.15 ? '' : 'blur(' + b.toFixed(2) + 'px)';
        if (l.el._aeDof !== v) { l.el.style.filter = v; l.el._aeDof = v; }
      });
    };
    const refresh = () => { if (drv) apply(drv.t); };
    const cam = {
      perspective: P, width: W, height: H, layers, state, at: state,
      keys(list, ko) {
        const q = ko || {};
        const segs = (q.mode || o.mode) === 'segments';
        let last = Object.assign({}, base), prev = 0;
        const filled = list.map((k) => {
          const t = typeof k.t === 'string' && k.t[0] === '+' ? prev + parseFloat(k.t.slice(1)) : Number(k.t);
          prev = t;
          last = Object.assign({}, last, keyVals(k));
          return Object.assign({ t, stop: k.stop, ease: k.ease }, last);
        }).sort((a, b) => a.t - b.t);
        tracks = {};
        PROPS.forEach((p) => {
          tracks[p] = track(filled.map((k) => ({ t: k.t, v: k[p], stop: k.stop, ease: k.ease })),
            { interp: segs ? null : 'auto', log: p === 'dist', tension: q.tension != null ? q.tension : o.tension, ease: q.ease || o.ease });
        });
        focusKeyed = list.some((k) => k.focus != null);
        refresh();
        return cam;
      },
      // AE wiggle on the camera: a slow handheld breath (seeded, additive), ramps in and out over 0.5 s.
      handheld(h) {
        const q = h || {};
        const amp = q.amp != null ? q.amp : 3, rot = q.rot != null ? q.rot : 0.12, freq = q.freq != null ? q.freq : 0.55, seed = q.seed != null ? q.seed : 3;
        const a = q.at || 0, b = q.until != null ? q.until : Infinity;
        add.push((t) => {
          if (t < a || t > b) return null;
          const k = Math.min(1, (t - a) / 0.5) * Math.min(1, (b - t) / 0.5);
          return { tx: k * amp * wig(t, freq, seed), ty: k * amp * wig(t, freq, seed + 11), rz: k * rot * wig(t, freq * 0.8, seed + 23) };
        });
        refresh();
        return cam;
      },
      // Impact shake: decaying seeded noise from `at` (a slam, a bass hit). Additive.
      shake(at, s) {
        const q = shakeOpts(at, s, { amp: 16, rot: 0.5, freq: 22, decay: 7, duration: 0.7 });
        add.push((t) => {
          if (t < at || t > at + q.duration) return null;
          const v = shakeAt(t - at, q);
          return { tx: v.x, ty: v.y, rz: v.rotation };
        });
        refresh();
        return cam;
      },
      // Any extra additive offset t -> { tx, ty, tz, dist, rx, ry, rz }.
      offset(fn) { add.push(fn); refresh(); return cam; },
      // Depth of field: layers marked data-dof blur by their distance from the focus plane.
      dof(d) {
        const q = d || {};
        dof = { strength: q.strength != null ? q.strength : 10, max: q.max != null ? q.max : 16, layers: toEls(q.layers || '[data-dof]', world).map((e) => ({ el: e, z: zOf(e) })) };
        refresh();
        return cam;
      },
    };
    if (o.keys) cam.keys(o.keys);
    if (o.handheld) cam.handheld(o.handheld === true ? {} : o.handheld);
    if (o.shake) [].concat(o.shake).forEach((s) => (typeof s === 'number' ? cam.shake(s) : cam.shake(s.at, s)));
    if (o.dof) cam.dof(o.dof === true ? {} : o.dof);
    const from = o.from || 0;
    const until = o.until != null ? o.until : rootDuration(vp) || Math.max(tracks ? tracks.tx.end : 0, tl.duration());
    drv = drive(tl, from, until, apply);
    cam.start = from;
    cam.end = until;
    return cam;
  }

  // ------------------------------------------------------------------ motion-kit moves (tween-based)

  function arc(tl, el, from, to, at, opts) {
    const o = opts || {};
    const d = Math.hypot((to.x || 0) - (from.x || 0), (to.y || 0) - (from.y || 0));
    const base = o.duration != null ? o.duration : dur(d, o.weight != null ? o.weight : 1);
    const xe = ease(o.xEase, C.land), ye = ease(o.yEase, C.heavy);
    if (from.x !== undefined) tl.fromTo(el, { x: from.x }, { x: to.x, duration: base, ease: xe }, at);
    if (from.y !== undefined) tl.fromTo(el, { y: from.y }, { y: to.y, duration: base * 1.12, ease: ye }, at);
    return base;
  }
  function anticipate(tl, el, prop, from, to, at, opts) {
    const o = opts || {};
    const travel = to - from, back = from - travel * (o.amount != null ? o.amount : 0.05);
    const windT = F60(o.windFrames != null ? o.windFrames : 9);
    const d = o.duration != null ? o.duration : dur(Math.abs(travel), o.weight != null ? o.weight : 1);
    tl.fromTo(el, { [prop]: from }, { [prop]: back, duration: windT, ease: C.wind }, at);
    tl.to(el, { [prop]: to, duration: d, ease: ease(o.ease, C.whip) }, at + windT);
    return windT + d;
  }
  function drag(tl, child, prop, lagPx, at, parentDur, opts) {
    const o = opts || {};
    tl.fromTo(child, { [prop]: lagPx }, { [prop]: 0, duration: parentDur + F60(o.extraFrames != null ? o.extraFrames : 8), ease: ease(o.ease, C.land) }, at + F60(o.delayFrames != null ? o.delayFrames : 3));
  }
  function exitTo(tl, el, to, at, opts) {
    const o = opts || {};
    const d = Math.hypot(to.x || 0, to.y || 0);
    tl.to(el, Object.assign({}, to, { duration: dur(d, (o.weight != null ? o.weight : 1) * 0.65), ease: ease(o.ease, C.leave) }), at);
  }
  function loop(tl, el, fromVars, toVars, opts) {
    const o = opts || {};
    const at = o.at || 0, until = o.until != null ? o.until : rootDuration(el1(el)) || tl.duration(), period = o.period || 1;
    const reps = Math.max(1, Math.floor((until - at) / period));
    const pingpong = o.mode === 'pingpong';
    tl.fromTo(el, fromVars, Object.assign({}, toVars, { duration: period, ease: ease(o.ease, pingpong ? C.drift : LIN), repeat: reps - 1, yoyo: pingpong }), at);
  }
  function ramp(tl, section, at, seconds, rampCurve) {
    section.pause(0);
    tl.fromTo(section, { progress: 0 }, { progress: 1, duration: seconds, ease: ease(rampCurve, LIB['ramp.slowMid']) }, at);
  }
  // Null + pick-whip: one controller value drives many properties. Pure function of time.
  function controller(opts) {
    const o = opts || {};
    const from = o.from || 0, to = o.to != null ? o.to : 1, at = o.at || 0, duration = o.duration || 1, e = ease(o.ease, C.heavy);
    return { at, duration, value: (t) => from + (to - from) * e(clamp01((t - at) / duration)) };
  }
  function link(tl, ctl, target, map, opts) {
    const o = opts || {};
    const els = toEls(target);
    const start = o.at != null ? o.at : ctl.at, end = o.until != null ? o.until : ctl.at + ctl.duration;
    drive(tl, start, end, (t) => {
      const out = Object.assign({}, map(ctl.value(t), t));
      if ('textContent' in out) { els.forEach((e) => { e.textContent = out.textContent; }); delete out.textContent; }
      if (Object.keys(out).length) G().set(els, out);
    });
  }

  // ------------------------------------------------------------------ text

  const MASK_CSS = 'display:inline-block;overflow:hidden;vertical-align:top;padding:0.06em 0.04em 0.12em;margin:-0.06em -0.04em -0.12em';
  // Split text into masked units once, at build time (after fonts load). by: 'chars' | 'words' |
  // 'lines'. Returns the inner spans to animate; each sits in an overflow-hidden mask.
  function splitText(el, by, opts) {
    const o = opts || {};
    const mode = by || 'words';
    const masked = o.mask !== false;
    if (el._aeSplit && el._aeSplit.by === mode && el._aeSplit.masked === masked) return el._aeSplit.inners;
    if (mode === 'lines') return splitLines(el, masked);
    const text = el._aeText != null ? el._aeText : el.textContent;
    el._aeText = text;
    el.textContent = '';
    const inners = [];
    const words = text.split(/(\s+)/);
    words.forEach((word) => {
      if (/^\s+$/.test(word) || !word) { if (word) el.appendChild(doc.createTextNode(' ')); return; }
      if (mode === 'chars') {
        const w = doc.createElement('span');
        w.style.cssText = 'display:inline-block;white-space:nowrap';
        Array.from(word).forEach((ch) => w.appendChild(unit(ch, masked, inners)));
        el.appendChild(w);
      } else {
        el.appendChild(unit(word, masked, inners));
      }
    });
    el._aeSplit = { by: mode, masked, inners };
    return inners;
  }
  function unit(text, masked, inners) {
    const mask = doc.createElement('span');
    mask.style.cssText = masked ? MASK_CSS : 'display:inline-block';
    const inner = doc.createElement('span');
    inner.style.cssText = 'display:inline-block;will-change:transform';
    inner.textContent = text;
    mask.appendChild(inner);
    inners.push(inner);
    return mask;
  }
  function splitLines(el, masked) {
    const text = el._aeText != null ? el._aeText : el.textContent;
    el._aeText = text;
    el._aeSplit = null;
    const probe = splitText(el, 'words', { mask: false });
    const rows = [];
    let lastTop = null;
    probe.forEach((w) => {
      const top = Math.round(w.parentNode.offsetTop);
      if (lastTop === null || Math.abs(top - lastTop) > 2) { rows.push([]); lastTop = top; }
      rows[rows.length - 1].push(w.textContent);
    });
    el.textContent = '';
    const inners = rows.map((row) => {
      const mask = doc.createElement('span');
      mask.style.cssText = (masked ? 'overflow:hidden;' : '') + 'display:block;padding:0.06em 0 0.12em;margin:-0.06em 0 -0.12em';
      const inner = doc.createElement('span');
      inner.style.cssText = 'display:block;will-change:transform';
      inner.textContent = row.join(' ');
      mask.appendChild(inner);
      el.appendChild(mask);
      return inner;
    });
    el._aeSplit = { by: 'lines', masked, inners };
    return inners;
  }

  // Hard cut: the element is simply there from this frame (or gone with on = false).
  function cut(tl, target, at, on) {
    tl.set(target, { autoAlpha: on === false ? 0 : 1 }, at);
  }

  // AE text animator with a range selector. One move swept across a line's units: `from` is each
  // unit's offset before the selection reaches it ({ yPercent: 110, rotation: 6, x, y, scale,
  // opacity }); it settles to rest as the selection passes. width = softness of the leading edge
  // (share of the line), shape = falloff ('smooth' | 'ramp' | 'square' | any curve name),
  // direction = 'left' | 'right' | 'center' (outward) | 'edges' (inward), order: 'random' with a
  // seed shuffles which unit goes when. by: 'chars' | 'words' | 'lines'. Set out: true to sweep the
  // units OUT to `from` (exit). Returns the units.
  function textRange(tl, target, at, seconds, opts) {
    const o = opts || {};
    const e = el1(target);
    const units = o.units || splitText(e, o.by || 'chars', { mask: o.mask !== false });
    const from = o.from || { yPercent: 110 };
    const n = units.length, width = Math.max(0.01, o.width != null ? o.width : 0.35);
    let order = units.map((_, i) => i);
    if (o.order === 'random') {
      let s = o.seed != null ? o.seed : 7;
      const rnd = () => { s = (s * 16807) % 2147483647; return (s - 1) / 2147483646; };
      for (let i = order.length - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); const tmp = order[i]; order[i] = order[j]; order[j] = tmp; }
    }
    const dir = o.direction || 'left';
    const pos = (i) => {
      const t = order[i] / Math.max(1, n - 1);
      return dir === 'right' ? 1 - t : dir === 'center' ? Math.abs(t - 0.5) * 2 : dir === 'edges' ? 1 - Math.abs(t - 0.5) * 2 : t;
    };
    const SH = { smooth: (u) => u * u * (3 - 2 * u), ramp: (u) => u, square: (u) => (u > 0 ? 1 : 0) };
    const shape = typeof o.shape === 'function' ? o.shape : SH[o.shape || 'smooth'] || curve(o.shape);
    const rest = (k) => (/^(scale|scaleX|scaleY|opacity)$/.test(k) ? 1 : 0);
    const sweepEase = ease(o.ease, LIN);
    if (o.origin) units.forEach((u) => { u.style.transformOrigin = o.origin; });
    const out = !!o.out;
    const apply = (t) => {
      const p = sweepEase(clamp01((t - at) / seconds));
      const sweep = p * (1 + width);
      units.forEach((u, i) => {
        let s = shape(clamp01((sweep - pos(i)) / width));
        if (out) s = 1 - s;
        const vals = {};
        Object.keys(from).forEach((k) => { vals[k] = from[k] + (rest(k) - from[k]) * s; });
        G().set(u, vals);
      });
    };
    if (!out) tl.set(e, { autoAlpha: 1 }, at);
    drive(tl, at, at + seconds, apply);
    return units;
  }

  // Words (or chars) rise through their masks at uneven reaction offsets.
  function revealWords(tl, target, at, opts) {
    const o = opts || {};
    const e = el1(target);
    const inners = splitText(e, o.by || 'words');
    tl.set(e, { autoAlpha: 1 }, at);
    inners.forEach((w, i) => tl.fromTo(w, { yPercent: 112 }, { yPercent: 0, duration: o.duration != null ? o.duration : F60(30), ease: ease(o.ease, C.reveal) }, at + react(i, o.spread != null ? o.spread : 1)));
    return inners;
  }
  // Lines rise out of their own baselines (broadcast title). Accepts an element (auto-split into
  // lines) or a list of line elements that each contain an .inner.
  function revealLines(tl, target, at, opts) {
    const o = opts || {};
    const one = el1(target);
    const lines = one && !one.querySelector('.inner') && toEls(target).length === 1 ? splitText(one, 'lines') : toEls(target).map((l) => l.querySelector('.inner') || l);
    if (one && one.style) tl.set(one, { autoAlpha: 1 }, at);
    lines.forEach((inner, i) => tl.fromTo(inner, { yPercent: 108 }, { yPercent: 0, duration: o.duration != null ? o.duration : F60(34), ease: ease(o.ease, C.reveal) }, at + react(i, o.spread != null ? o.spread : 1.2)));
    return lines;
  }
  // Text exit: the units leave up through their masks, faster than they came, accelerating.
  function textOut(tl, target, at, opts) {
    const o = opts || {};
    const e = el1(target);
    const units = (e._aeSplit && e._aeSplit.inners) || splitText(e, o.by || 'words');
    const d = o.duration != null ? o.duration : F60(20);
    units.forEach((u, i) => tl.to(u, { yPercent: o.to != null ? o.to : -110, duration: d, ease: ease(o.ease, C.leave) }, at + react(i, o.spread != null ? o.spread : 0.5)));
    return at + d + react(units.length - 1, o.spread != null ? o.spread : 0.5);
  }
  // Type-on for written text (prompts, terminals): stepped character uncover. Mono reads best.
  // With cps (or caret: true) it types like a person instead (from motion-pro): characters appear at
  // `cps` per second with a seeded uneven rhythm (jitter), and class ae-caret rides the last typed
  // character, then blinks every `blink` s until caretUntil (style .ae-caret::after; ae-caret-pre
  // marks the first character for the 0.4 s before typing starts). Returns the end time in that mode.
  function typeOn(tl, target, at, opts) {
    const o = opts || {};
    const e = el1(target);
    if (o.cps != null || o.caret) return typeHuman(tl, e, at, o);
    const n = o.chars || e.textContent.trim().length;
    tl.set(e, { autoAlpha: 1 }, at);
    tl.fromTo(e, { clipPath: 'inset(-10% 100% -10% 0%)' }, { clipPath: 'inset(-10% 0% -10% 0%)', duration: o.duration != null ? o.duration : F60(o.frames != null ? o.frames : n * 1.6), ease: 'steps(' + n + ')' }, at);
  }
  function typeHuman(tl, e, at, o) {
    const outers = splitText(e, 'chars', { mask: false }).map((u) => u.parentNode);
    const cps = o.cps != null ? o.cps : 22, jitter = o.jitter != null ? o.jitter : 0.45, r = rng(o.seed != null ? o.seed : 9);
    let t = at;
    const times = outers.map(() => { const tt = t; t += (1 / cps) * (1 + (r() - 0.5) * 2 * jitter); return tt; });
    const end = t, blink = o.blink != null ? o.blink : 0.53, caretUntil = o.caretUntil != null ? o.caretUntil : Infinity;
    const caret = o.caret !== false, pre = caret ? 0.4 : 0;
    const until = o.until != null ? o.until : Math.max(end, rootDuration(e) || tl.duration());
    tl.set(e, { autoAlpha: 1 }, Math.max(0, at - pre));
    drive(tl, Math.max(0, at - pre - F(1)), until, (tt) => {
      let last = -1;
      outers.forEach((u, i) => { const on = tt >= times[i]; u.style.opacity = on ? '1' : '0'; if (on) last = i; });
      const show = caret && tt >= at - pre && tt < caretUntil && (tt < end || Math.floor((tt - end) / blink) % 2 === 0);
      outers.forEach((u, i) => {
        u.classList.toggle('ae-caret', show && last >= 0 && i === last);
        u.classList.toggle('ae-caret-pre', show && last < 0 && i === 0);
      });
    });
    return end;
  }
  // Tracking settle (premium titles only; the owner's reels never animate letter-spacing on captions).
  // glyphs: true moves each glyph's x instead of letter-spacing (from motion-pro: letter-spacing can
  // step in whole pixels and stutter on a slow settle). Then `from` is extra tracking per gap in em
  // (0.35) and anchor 0..1 picks the glyph that stays put (0 = first, 0.5 = centre).
  function trackIn(tl, target, at, opts) {
    const o = opts || {};
    const e = el1(target);
    if (o.glyphs) {
      const units = splitText(e, 'chars', { mask: false });
      const fs = parseFloat(getComputedStyle(e).fontSize) || 100;
      const gap = (o.from != null ? parseFloat(o.from) : 0.35) * fs, c = (units.length - 1) * (o.anchor != null ? o.anchor : 0.5);
      const d = o.duration != null ? o.duration : F60(48), ez = ease(o.ease, C.heavy);
      tl.set(e, { autoAlpha: 1 }, at);
      drive(tl, at, at + d, (t) => { const k = 1 - ez(clamp01((t - at) / d)); units.forEach((u, i) => G().set(u, { x: (i - c) * gap * k })); });
      return units;
    }
    const to = o.to != null ? o.to : getComputedStyle(e).letterSpacing;
    tl.set(e, { autoAlpha: 1 }, at);
    tl.fromTo(e, { letterSpacing: o.from || '0.4em' }, { letterSpacing: to === 'normal' ? '0em' : to, duration: o.duration != null ? o.duration : F60(48), ease: ease(o.ease, C.heavy) }, at);
  }
  // Scramble / decode: characters resolve left to right; unresolved ones cycle through glyphs.
  function scramble(tl, target, at, seconds, opts) {
    const o = opts || {};
    const e = el1(target);
    const text = o.text != null ? o.text : e.textContent;
    const glyphs = o.glyphs || 'ABCDEFGHJKLMNPQRSTUVWXYZ0123456789#%&*+=/<>';
    const s = seconds || 0.8, se = ease(o.ease, LIN);
    tl.set(e, { autoAlpha: 1 }, at);
    drive(tl, at, at + s, (t) => {
      const p = se(clamp01((t - at) / s));
      const frame = Math.round(t * fps() / 2);
      const done = Math.floor(p * text.length);
      e.textContent = Array.from(text).map((ch, i) => (i < done || ch === ' ' ? ch : glyphs[(i * 7 + frame * 13) % glyphs.length])).join('');
    });
  }
  // Slot roll: one word rolls through options inside its mask and lands on the last one.
  function roll(tl, target, options, at, opts) {
    const o = opts || {};
    const e = el1(target);
    const each = o.each != null ? o.each : 0.1;
    e.textContent = '';
    const mask = doc.createElement('span');
    mask.style.cssText = 'display:inline-block;overflow:hidden;vertical-align:bottom;height:1.15em;line-height:1.15em;text-align:' + (o.align || 'left');
    const col = doc.createElement('span');
    col.style.cssText = 'display:block;will-change:transform';
    options.forEach((w) => { const d = doc.createElement('span'); d.style.cssText = 'display:block;white-space:nowrap'; d.textContent = w; col.appendChild(d); });
    mask.appendChild(col);
    e.appendChild(mask);
    const n = options.length;
    const k = [[at, 0]];
    for (let i = 1; i < n; i++) {
      const last = i === n - 1;
      k.push([at + i * each, -(100 / n) * i, last ? ease(o.landEase, C.land) : ease(o.ease, C.whip)]);
    }
    if (n > 1) k[k.length - 1][0] = at + (n - 2) * each + (o.land != null ? o.land : each * 2.2);
    keys(tl, col, { yPercent: k });
    return col;
  }
  // Counter: numbers as a function of time, tabular figures so the width never jumps.
  function count(tl, target, from, to, at, seconds, opts) {
    const o = opts || {};
    const els = toEls(target);
    const e = ease(o.ease, C.heavy), dec = o.decimals || 0;
    const fmt = o.format || ((v) => (o.prefix || '') + v.toLocaleString(o.locale || 'en-US', { minimumFractionDigits: dec, maximumFractionDigits: dec }) + (o.suffix || ''));
    els.forEach((x) => { x.style.fontVariantNumeric = 'tabular-nums'; });
    drive(tl, at, at + seconds, (t) => {
      const v = from + (to - from) * e(clamp01((t - at) / seconds));
      const r = Math.round(v * Math.pow(10, dec)) / Math.pow(10, dec);
      els.forEach((x) => { x.textContent = fmt(r); });
    });
  }
  // Highlight or underline wipe: a bar grows from one side under or behind a word on screen.
  function highlight(tl, bar, at, opts) {
    const o = opts || {};
    tl.fromTo(bar, { scaleX: 0, transformOrigin: o.from === 'right' ? '100% 50%' : '0% 50%' }, { scaleX: 1, duration: o.duration != null ? o.duration : F60(18), ease: ease(o.ease, C.whip) }, at);
  }

  // ---- text treatments from motion-pro (slam, flip, wiggly, odometer, swap, slot)

  const restOf = (k) => (/^(scale|scaleX|scaleY|opacity)$/.test(k) ? 1 : 0);
  // Order positions 0..1 per unit, the range selector's: direction left | right | center | edges,
  // order 'random' + seed shuffles who goes when.
  function orderPositions(n, dir, order, seed) {
    let idx = Array.from({ length: n }, (_, i) => i);
    if (order === 'random') {
      const r = rng(seed != null ? seed : 7);
      for (let i = n - 1; i > 0; i--) { const j = Math.floor(r() * (i + 1)); const tmp = idx[i]; idx[i] = idx[j]; idx[j] = tmp; }
    }
    return idx.map((k) => {
      const t = k / Math.max(1, n - 1);
      return dir === 'right' ? 1 - t : dir === 'center' ? Math.abs(t - 0.5) * 2 : dir === 'edges' ? 1 - Math.abs(t - 0.5) * 2 : t;
    });
  }
  // First share of a spring ease at full value (the frame a slammed glyph first reaches size).
  function firstLand(fn) { for (let i = 1; i <= 400; i++) if (fn(i / 400) >= 1) return i / 400; return 1; }

  // Slam: characters punch down from a large scale a frame or two apart and settle on a spring.
  // Opacity snaps on over 2 frames (it never takes the overshoot). Unmasked units. Returns each
  // unit's land time (first frame at full size) for an SFX or a camera shake. reels-edit bans
  // all-caps slams on captions. opts: { by: 'chars', gap: F(1.5), scale: 2.6, yPercent: -6,
  // from: { rotation, x, y }, spring: { response: 0.36, overshoot: 7 }, origin, units }
  function slam(tl, target, at, opts) {
    const o = opts || {};
    const e = el1(target);
    const units = o.units || splitText(e, o.by || 'chars', { mask: false });
    const gap = o.gap != null ? o.gap : F(1.5);
    const sp = spring(o.spring || { response: 0.36, overshoot: 7 });
    const from = Object.assign({ scale: o.scale != null ? o.scale : 2.6, yPercent: o.yPercent != null ? o.yPercent : -6 }, o.from || {});
    delete from.opacity;
    if (o.origin) units.forEach((u) => { u.style.transformOrigin = o.origin; });
    tl.set(e, { autoAlpha: 1 }, at);
    drive(tl, at, at + (units.length - 1) * gap + sp.duration, (t) => {
      units.forEach((u, i) => {
        const t0 = at + i * gap, p = sp.ease(clamp01((t - t0) / sp.duration));
        const vals = { opacity: clamp01((t - t0) / F(2)) };
        Object.keys(from).forEach((k) => { vals[k] = from[k] + (restOf(k) - from[k]) * p; });
        G().set(u, vals);
      });
    });
    const land = firstLand(sp.ease) * sp.duration;
    return units.map((_, i) => at + i * gap + land);
  }

  // 3D flip-up: characters hinge up from their baselines in perspective, swept across the line like a
  // range selector, each settling on a spring; opacity fades on over 5 frames. GSAP's
  // transformPerspective on each unit, so no parent is touched. opts: { by: 'chars', angle: -100,
  // axis: 'x' | 'y', duration, spread: 0.25, direction, order: 'random', seed,
  // spring: { response: 0.5, overshoot: 4 }, perspective: 900, units }
  function flip(tl, target, at, opts) {
    const o = opts || {};
    const e = el1(target);
    const units = o.units || splitText(e, o.by || 'chars', { mask: false });
    const n = units.length;
    const seconds = o.duration != null ? o.duration : Math.max(0.5, n * F(1.2));
    const sp = spring(o.spring || { response: 0.5, overshoot: 4 });
    const spread = clamp(o.spread != null ? o.spread : 0.25, 0.01, 1);
    const pos = orderPositions(n, o.direction, o.order, o.seed);
    const ang = o.angle != null ? o.angle : -100, prop = o.axis === 'y' ? 'rotationY' : 'rotationX';
    const du = Math.max((seconds * spread) / (1 + spread), sp.duration);
    const fs = root.getComputedStyle ? parseFloat(getComputedStyle(e).fontSize) || 100 : 100;
    G().set(units, { transformOrigin: '50% 100% ' + (-0.3 * fs).toFixed(1) + 'px', transformPerspective: o.perspective || 900, backfaceVisibility: 'hidden' });
    tl.set(e, { autoAlpha: 1 }, at);
    drive(tl, at, at + seconds / (1 + spread) + du, (t) => {
      units.forEach((u, i) => {
        const ts = at + (seconds * pos[i]) / (1 + spread);
        G().set(u, { [prop]: ang * (1 - sp.ease(clamp01((t - ts) / du))), opacity: clamp01((t - ts) / F(5)) });
      });
    });
    return units;
  }

  // AE wiggly selector: seeded per-unit jitter on each unit's OUTER span (its mask or wrapper), so it
  // adds to an animator moving the inner spans. Uses the element's existing split (call it after
  // textRange, slam or flip), else splits by `by`. Ramps in and out over `ramp` s. On calm titles,
  // keep it for playful beats: a landed title is otherwise dead still.
  // opts: { amps: { y: 6, rotation: 3, x, scale }, freq: 2, seed: 7, at: 0, until, ramp: 0.3, by, mask }
  function wiggly(tl, target, opts) {
    const o = opts || {};
    const e = el1(target);
    const inners = (e._aeSplit && e._aeSplit.inners) || splitText(e, o.by || 'chars', { mask: !!o.mask });
    const outers = inners.map((u) => u.parentNode);
    const amps = o.amps || { y: 6, rotation: 3 };
    const freq = o.freq != null ? o.freq : 2, seed = o.seed != null ? o.seed : 7, ramp = o.ramp != null ? o.ramp : 0.3;
    const at = o.at || 0, until = o.until != null ? o.until : rootDuration(e) || tl.duration();
    drive(tl, at, until, (t) => {
      const k = clamp01((t - at) / ramp) * clamp01((until - t) / ramp);
      outers.forEach((u, i) => {
        const vals = {};
        Object.keys(amps).forEach((p, j) => { vals[p] = restOf(p) + k * amps[p] * wig(t, freq, seed + j * 17 + i * 3); });
        G().set(u, vals);
      });
    });
    return outers;
  }

  // Odometer digit k's roll position (0..10, 10 = the 0 after 9) for value v. Pure. The ones spin;
  // a higher digit ticks over while the digits below it pass from ...9 to ...0.
  function digitRoll(v, k) {
    const p = Math.pow(10, k);
    return k === 0 ? v % 10 : (Math.floor(v / p) % 10) + clamp01((v % p) - (p - 1));
  }
  // Odometer: a number rolls digit by digit like a mechanical counter; the value comes from a curve,
  // so any frame renders on its own. Leading zeros stay hidden (they keep their width: right-align
  // the element) unless pad. Tabular figures. Whole numbers >= 0 (use count() for decimals).
  // odometer(tl, '#n', { from: 0, to: 4820, at: 2, duration: 1.4, ease: 'kit.glide', separator: ',', prefix, suffix, pad })
  function odometer(tl, target, opts) {
    const o = opts || {};
    const e = el1(target);
    const from = o.from || 0, to = o.to != null ? o.to : Number(String(e.textContent).replace(/[^0-9.]/g, '')) || 0;
    const at = o.at || 0, d = o.duration != null ? o.duration : 1.4, ez = ease(o.ease, C.glide);
    const digits = Math.max(String(Math.floor(Math.abs(to))).length, String(Math.floor(Math.abs(from))).length);
    const add = (text) => { const s = doc.createElement('span'); s.textContent = text; e.appendChild(s); return s; };
    e.textContent = '';
    e.style.fontVariantNumeric = 'tabular-nums';
    if (o.prefix) add(o.prefix);
    const cols = [], seps = [];
    for (let k = digits - 1; k >= 0; k--) {
      const cell = doc.createElement('span');
      cell.style.cssText = 'display:inline-block;overflow:hidden;height:1.1em;line-height:1.1em;vertical-align:top';
      const strip = doc.createElement('span');
      strip.style.cssText = 'display:block;will-change:transform';
      for (let i = 0; i < 11; i++) { const g = doc.createElement('span'); g.style.display = 'block'; g.textContent = String(i % 10); strip.appendChild(g); }
      cell.appendChild(strip);
      e.appendChild(cell);
      cols.push({ k, strip, cell });
      if (o.separator && k > 0 && k % 3 === 0) seps.push({ k, el: add(o.separator) });
    }
    if (o.suffix) add(o.suffix);
    const shown = (k, v) => !!o.pad || k === 0 || v >= Math.pow(10, k) - 1e-6;
    drive(tl, at, at + d, (t) => {
      const v = Math.max(0, lerp(from, to, ez(clamp01((t - at) / d))));
      cols.forEach((c) => {
        G().set(c.strip, { yPercent: (-100 * digitRoll(v, c.k)) / 11 });
        c.cell.style.opacity = shown(c.k, v) ? '1' : '0';
      });
      seps.forEach((s) => { s.el.style.opacity = shown(s.k, v) ? '1' : '0'; });
    });
    return cols.map((c) => c.strip);
  }

  // Word swap: at each time you give, the old word leaves up through a mask and the new one rises in.
  // el holds the first word; list = [{ t, text }]. The mask is as wide as the widest word. Swaps
  // closer than `in` apart are pushed back to land first.
  // opts: { in: 0.5, out: 0.24, overlap: 0.06, ease: 'kit.reveal', outEase: 'kit.leave' }
  function swap(tl, target, list, opts) {
    const o = opts || {};
    const e = el1(target);
    const first = e.textContent;
    e.textContent = '';
    const mask = doc.createElement('span');
    mask.style.cssText = MASK_CSS.replace('display:inline-block', 'display:inline-grid');
    e.appendChild(mask);
    const dIn = o.in != null ? o.in : 0.5, dOut = o.out != null ? o.out : 0.24, ov = o.overlap != null ? o.overlap : 0.06;
    const eIn = ease(o.ease, C.reveal), eOut = ease(o.outEase, C.leave);
    const items = [{ t: -Infinity, text: first }].concat(list).map((it) => {
      const s = doc.createElement('span');
      s.style.cssText = 'grid-area:1/1;display:inline-block;white-space:nowrap;will-change:transform';
      s.textContent = it.text;
      mask.appendChild(s);
      return { t: it.t, s };
    });
    for (let i = 2; i < items.length; i++) items[i].t = Math.max(items[i].t, items[i - 1].t + ov + dIn);
    items.forEach((it, i) => {
      const next = items[i + 1], k = [];
      if (i > 0) k.push([it.t + ov, 110], [it.t + ov + dIn, 0, eIn]);
      if (next) { if (!k.length) k.push([next.t, 0]); else k.push([next.t, 0, LIN]); k.push([next.t + dOut, -110, eOut]); }
      if (k.length) keys(tl, it.s, { yPercent: k });
    });
    return items.map((it) => it.s);
  }

  // Slot roll per character: each character is a strip of seeded random glyphs ending on the real one,
  // and the strips roll into place one after another; mode 'mech' steps like a split-flap. Cells are
  // sized by the final glyph and clip vertically only. (roll() instead rolls one word through options
  // you choose.) opts: { rolls: 7, duration: 0.55, gap: F(1.4), ease: 'kit.land', mode: 'smooth' |
  // 'mech', seed: 5, glyphs, jitter: 0, hidden: true }
  function slot(tl, target, at, opts) {
    const o = opts || {};
    const e = el1(target);
    const text = e._aeText != null ? e._aeText : e.textContent;
    e._aeText = text;
    const rolls = o.rolls || 7, r = rng(o.seed != null ? o.seed : 5);
    const glyphs = o.glyphs || 'ABCDEFGHJKLMNPRSTUVWXYZ0123456789';        // no descenders, no Q tail
    const d = o.duration != null ? o.duration : 0.55, gap = o.gap != null ? o.gap : F(1.4);
    const ez = o.mode === 'mech' ? 'steps(' + rolls + ')' : ease(o.ease, C.land);
    const endP = (-100 * rolls) / (rolls + 1);
    const line = (ch) => { const s = doc.createElement('span'); s.style.cssText = 'display:flex;justify-content:center;white-space:nowrap'; s.textContent = ch; return s; };
    e.textContent = '';
    let i = 0;
    const strips = [];
    Array.from(text).forEach((ch) => {
      const cell = doc.createElement('span');
      if (/\s/.test(ch)) { cell.textContent = ' '; cell.style.display = 'inline-block'; e.appendChild(cell); return; }
      cell.style.cssText = 'display:inline-block;position:relative;vertical-align:top;clip-path:inset(0 -60% -0.14em -60%)';
      const sizer = doc.createElement('span');
      sizer.textContent = ch;
      sizer.style.visibility = 'hidden';
      const strip = doc.createElement('span');
      strip.style.cssText = 'position:absolute;left:0;right:0;top:0;will-change:transform';
      for (let k = 0; k < rolls; k++) strip.appendChild(line(glyphs[Math.floor(r() * glyphs.length)]));
      strip.appendChild(line(ch));
      cell.appendChild(sizer);
      cell.appendChild(strip);
      e.appendChild(cell);
      const t = at + i * gap, dd = d + (o.jitter ? r() * o.jitter : 0);
      i++;
      keys(tl, strip, { yPercent: [[t, 0], [t + dd, endP, ez]] });
      if (o.hidden !== false) { G().set(cell, { opacity: 0 }); tl.set(cell, { opacity: 1 }, t); }
      strips.push(strip);
    });
    return strips;
  }

  // ------------------------------------------------------------------ mattes

  function setMask(e, img) { e.style.webkitMaskImage = img; e.style.maskImage = img; }
  function windowed(at, seconds, o, def) {
    const e = ease(o.ease, def);
    return (t) => e(clamp01((t - at) / seconds));
  }
  // Linear wipe with a feathered edge at any angle (AE Linear Wipe). angle in CSS degrees: 90
  // reveals left -> right, 180 top -> bottom. out: true conceals instead.
  function matteLinear(tl, target, at, seconds, opts) {
    const o = opts || {};
    const els = toEls(target);
    const angle = o.angle != null ? o.angle : 90, f = o.feather != null ? o.feather : 14, out = !!o.out;
    const prog = windowed(at, seconds, o, C.whip);
    drive(tl, at, at + seconds, (t) => {
      const p = prog(t), pos = p * (100 + f);
      let img;
      if (!out) img = p >= 1 ? 'none' : 'linear-gradient(' + angle + 'deg, #000 ' + (pos - f).toFixed(2) + '%, transparent ' + pos.toFixed(2) + '%)';
      else img = p <= 0 ? 'none' : 'linear-gradient(' + angle + 'deg, transparent ' + (pos - f).toFixed(2) + '%, #000 ' + pos.toFixed(2) + '%)';
      els.forEach((e) => setMask(e, img));
    });
  }
  // Iris: a circle grows from a point (x, y in px of the element box, or '50%'), optional feather.
  function matteIris(tl, target, at, seconds, opts) {
    const o = opts || {};
    const els = toEls(target);
    const prog = windowed(at, seconds, o, C.heavy);
    const geo = els.map((e) => {
      const w = e.offsetWidth || 1080, h = e.offsetHeight || 1920;
      const px = (v, size) => (typeof v === 'string' && v.slice(-1) === '%' ? (parseFloat(v) / 100) * size : v != null ? Number(v) : size / 2);
      const x = px(o.x, w), y = px(o.y, h);
      const rMax = Math.hypot(Math.max(x, w - x), Math.max(y, h - y)) + (o.feather || 0) + 2;
      return { x, y, rMax };
    });
    const r0 = o.r0 || 0, out = !!o.out, f = o.feather || 0;
    drive(tl, at, at + seconds, (t) => {
      const p = prog(t);
      els.forEach((e, i) => {
        const g = geo[i];
        const r = out ? lerp(g.rMax, r0, p) : lerp(r0, g.rMax, p);
        const full = (!out && p >= 1) || (out && p <= 0);
        if (f > 0) { setMask(e, full ? 'none' : 'radial-gradient(circle at ' + g.x + 'px ' + g.y + 'px, #000 ' + Math.max(0, r - f).toFixed(1) + 'px, transparent ' + r.toFixed(1) + 'px)'); }
        else e.style.clipPath = full ? 'none' : 'circle(' + r.toFixed(1) + 'px at ' + g.x + 'px ' + g.y + 'px)';
      });
    });
  }
  // Box reveal (AE mask expansion): from 'left' | 'right' | 'top' | 'bottom' | 'center' | 'x' | 'y',
  // optional corner radius. out: true closes it.
  function matteBox(tl, target, at, seconds, opts) {
    const o = opts || {};
    const els = toEls(target);
    const from = o.from || 'left', r = o.radius || 0, out = !!o.out;
    const prog = windowed(at, seconds, o, C.whip);
    drive(tl, at, at + seconds, (t) => {
      const p = out ? 1 - prog(t) : prog(t), h = (1 - p) * 100, half = h / 2;
      const ins = { left: [0, h, 0, 0], right: [0, 0, 0, h], top: [0, 0, h, 0], bottom: [h, 0, 0, 0], center: [half, half, half, half], x: [0, half, 0, half], y: [half, 0, half, 0] }[from];
      const v = p >= 1 ? 'none' : 'inset(' + ins.map((n) => n.toFixed(2) + '%').join(' ') + (r ? ' round ' + r + 'px' : '') + ')';
      els.forEach((e) => { e.style.clipPath = v; });
    });
  }
  // Track matte: show `fill` only through the alpha of an SVG <mask> (text, shapes, a path you
  // animate). Chrome draws CSS mask: url(#id) on HTML; test it in your render once per project.
  function trackMatte(fill, maskId) {
    toEls(fill).forEach((e) => { e.style.webkitMask = 'url(#' + maskId + ')'; e.style.mask = 'url(#' + maskId + ')'; });
  }
  // Text as a track matte (from motion-pro): everything inside `fill` (footage, UI, a gradient) shows
  // only through the glyphs of `text`. It builds an SVG <clipPath> of live <text> in the page's fonts
  // and applies it as CSS clip-path, which Chrome draws on HTML (more dependable than matte.track's
  // mask). Hard-edged and alpha-exact. x / y are px in the fill's own box (centre by default); an
  // array of strings sets lines. To zoom the type, scale a wrapper of the fill. Returns the <text>
  // (or a list) so you can tween its attributes (attr: { 'font-size', 'letter-spacing', x, y }).
  // Owns the fill's clip-path (don't also use matte.box or matte.iris on it); load fonts first.
  // matte.text(fill, 'MOTION', { size: 300, x, y, font, weight: 800, tracking: 0, anchor: 'middle', lineHeight, width, height, id })
  let matteN = 0;
  function matteText(fill, text, opts) {
    const o = opts || {};
    const e = el1(fill);
    const W = o.width || e.offsetWidth || 1080, H = o.height || e.offsetHeight || 1920;
    const size = o.size || 300, lh = o.lineHeight || size * 0.92;
    const lines = Array.isArray(text) ? text : [text];
    const id = o.id || 'ae-matte-' + (++matteN);
    const cp = doc.createElementNS(NS, 'clipPath');
    cp.setAttribute('id', id);
    cp.setAttribute('clipPathUnits', 'userSpaceOnUse');
    const font = o.font || (root.getComputedStyle ? getComputedStyle(e).fontFamily : '') || 'sans-serif';
    const y0 = (o.y != null ? o.y : H / 2) - ((lines.length - 1) * lh) / 2;
    const texts = lines.map((ln, i) => {
      const t = doc.createElementNS(NS, 'text');
      const attrs = { x: o.x != null ? o.x : W / 2, y: y0 + i * lh, 'text-anchor': o.anchor || 'middle', 'dominant-baseline': 'central',
        'font-family': font, 'font-weight': o.weight || 800, 'font-size': size, 'letter-spacing': o.tracking || 0 };
      Object.keys(attrs).forEach((k) => t.setAttribute(k, String(attrs[k])));
      t.textContent = ln;
      cp.appendChild(t);
      return t;
    });
    defsFor(e).appendChild(cp);
    e.style.webkitClipPath = 'url(#' + id + ')';
    e.style.clipPath = 'url(#' + id + ')';
    return texts.length === 1 ? texts[0] : texts;
  }
  const matte = { linear: matteLinear, iris: matteIris, box: matteBox, track: trackMatte, text: matteText };

  // ------------------------------------------------------------------ paths

  // AE Trim Paths on an SVG stroke: start, end and offset (0..1) each animate. Draw on: end 0 -> 1.
  // A line that runs through: end 0 -> 1, then start 0 -> 1 a few frames later (startDelay).
  // opts: { start: [a, b], end: [a, b], offset: [a, b], ease, startEase, endEase, startDelay, endDelay }
  function trim(tl, target, at, seconds, opts) {
    const o = opts || {};
    const els = toEls(target);
    const S = o.start || [0, 0], E = o.end || [0, 1], O = o.offset || [0, 0];
    const se = ease(o.startEase || o.ease, C.land), ee = ease(o.endEase || o.ease, C.land), oe = ease(o.offsetEase || o.ease, C.drift);
    const sd = o.startDelay || 0, ed = o.endDelay || 0;
    const lens = els.map((e) => (e.getTotalLength ? e.getTotalLength() : 0));
    const span = seconds + Math.max(sd, ed);
    const local = (t, delay) => clamp01((t - at - delay) / seconds);
    drive(tl, at, at + span, (t) => {
      let s = lerp(S[0], S[1], se(local(t, sd))), en = lerp(E[0], E[1], ee(local(t, ed)));
      const off = lerp(O[0], O[1], oe(local(t, 0)));
      if (en < s) { const x = s; s = en; en = x; }
      els.forEach((e, i) => {
        const L = lens[i];
        if (s <= 1e-4 && en >= 1 - 1e-4 && Math.abs(off) < 1e-4) { e.style.strokeDasharray = 'none'; e.style.strokeDashoffset = '0'; return; }
        const seg = Math.max(0, (en - s) * L);
        e.style.strokeDasharray = seg < 0.01 ? '0 ' + (L + 1) : seg.toFixed(2) + ' ' + (L + 1).toFixed(2);
        e.style.strokeDashoffset = (-(s + off) * L).toFixed(2);
      });
    });
  }
  // Follow a path with optional auto-orient. The follower sits in the same box as the SVG and the
  // SVG's viewBox matches its pixel size. Centre the follower on its own box (xPercent/yPercent -50
  // are set for you). opts: { from: 0, to: 1, ease, orient: true, offsetAngle: 0, samples: 400 }
  function follow(tl, target, path, at, seconds, opts) {
    const o = opts || {};
    const els = toEls(target);
    const pth = el1(path);
    const L = pth.getTotalLength(), N = o.samples || 400;
    const pts = [];
    for (let i = 0; i <= N; i++) { const p = pth.getPointAtLength((i / N) * L); pts.push([p.x, p.y]); }
    const sample = (u) => {
      const f = clamp01(u) * N, i = Math.min(N - 1, Math.floor(f)), r = f - i;
      return [lerp(pts[i][0], pts[i + 1][0], r), lerp(pts[i][1], pts[i + 1][1], r)];
    };
    const e = ease(o.ease, C.heavy), a = o.from || 0, b = o.to != null ? o.to : 1;
    G().set(els, { xPercent: -50, yPercent: -50, left: 0, top: 0 });
    drive(tl, at, at + seconds, (t) => {
      const u = lerp(a, b, e(clamp01((t - at) / seconds)));
      const p = sample(u), q = sample(u + (b >= a ? 0.002 : -0.002));
      const v = { x: p[0], y: p[1] };
      if (o.orient) v.rotation = (Math.atan2(q[1] - p[1], q[0] - p[0]) * 180) / Math.PI + (o.offsetAngle || 0);
      G().set(els, v);
    });
    return { sample, length: L };
  }

  // ------------------------------------------------------------------ transitions

  // Each transition is two halves that meet at a seam time `at`. Pass the outgoing and incoming
  // scene WRAPPERS (children of the timed .clip hosts, never the .clip itself); either may be
  // omitted when that half lives in another composition (then call it there with the same `at`).
  // Speeds match across the seam (the cut lands on the fastest frame, both sides moving the same).
  function hideUntil(tl, e, at) {
    if (at > 0) { G().set(e, { autoAlpha: 0 }); tl.set(e, { autoAlpha: 0 }, 0); }
    tl.set(e, { autoAlpha: 1 }, at);
  }
  function frameSize(e) { return { w: (e && e.offsetWidth) || 1080, h: (e && e.offsetHeight) || 1920 }; }
  const DIRS = { left: ['x', -1], right: ['x', 1], up: ['y', -1], down: ['y', 1] };

  // Whip pan: the outgoing scene accelerates off, hard cut at peak speed under a smear, the
  // incoming lands with a long settle. dir is the way content travels.
  function whip(tl, o) {
    const out = el1(o.out), inn = el1(o.in), at = o.at;
    const dirInfo = DIRS[o.dir || 'left'], axis = dirInfo[0], sign = dirInfo[1];
    const size = frameSize(out || inn), full = axis === 'x' ? size.w : size.h;
    const total = o.duration != null ? o.duration : 0.5;
    const dOut = total * 0.42, dIn = total * 0.58;
    const eOut = ease(o.outEase, C.accel), eIn = ease(o.inEase, C.land);
    const distOut = (o.distance != null ? o.distance : 0.55) * full;
    const vSeam = (distOut * endSlope(eOut)) / dOut;                 // px/s at the cut
    const distIn = Math.min(full * 1.5, (vSeam * dIn) / startSlope(eIn));
    const sm = o.smear === false ? null : Object.assign({ shutter: 180, max: 60, strength: 0.55 }, o.smear || {});
    if (out) {
      // The outgoing keeps travelling under the incoming at the same speed until the incoming has
      // covered the frame, so no gap shows at the cut. When the halves live in different
      // compositions, extend the outgoing host by the incoming duration and keep it underneath.
      const cover = o.cover !== false;
      const k = [[at - dOut, 0], [at, sign * distOut, eOut]];
      if (cover) k.push([at + dIn, sign * (distOut + distIn), eIn]);
      keys(tl, out, { [axis]: k }, { smear: sm });
      tl.set(out, { autoAlpha: 0 }, cover ? at + dIn + F(1) : at);
    }
    if (inn) {
      hideUntil(tl, inn, at);
      keys(tl, inn, { [axis]: [[at, -sign * distIn], [at + dIn, 0, eIn]] }, { smear: sm });
    }
    return { start: at - dOut, end: at + dIn };
  }
  // Push: both scenes travel as one strip (no cut), hang-snap-hang. Smear optional.
  function push(tl, o) {
    const out = el1(o.out), inn = el1(o.in), at = o.at;
    const dirInfo = DIRS[o.dir || 'left'], axis = dirInfo[0], sign = dirInfo[1];
    const size = frameSize(out || inn), full = axis === 'x' ? size.w : size.h;
    const d = o.duration != null ? o.duration : 0.7, e = ease(o.ease, C.whip);
    const sm = o.smear ? Object.assign({ shutter: 180, max: 40 }, o.smear === true ? {} : o.smear) : null;
    if (out) keys(tl, out, { [axis]: [[at - d / 2, 0], [at + d / 2, sign * full, e]] }, { smear: sm });
    if (inn) keys(tl, inn, { [axis]: [[at - d / 2, -sign * full], [at + d / 2, 0, e]] }, { smear: sm });
    return { start: at - d / 2, end: at + d / 2 };
  }
  // Slide stack (parallax push): the incoming scene slides over; the outgoing recedes a third as
  // far, shrinks a touch and darkens, so the two read as layers at different depths.
  function stack(tl, o) {
    const out = el1(o.out), inn = el1(o.in), at = o.at;
    const dirInfo = DIRS[o.dir || 'up'], axis = dirInfo[0], sign = dirInfo[1];
    const size = frameSize(out || inn), full = axis === 'x' ? size.w : size.h;
    const d = o.duration != null ? o.duration : 0.8;
    const e = ease(o.ease, C.heavy);
    const t0 = at - d * 0.35, t1 = t0 + d;
    if (inn) keys(tl, inn, { [axis]: [[t0, -sign * full], [t1, 0, e]] }, { smear: o.smear ? Object.assign({ shutter: 180, max: 30 }, o.smear === true ? {} : o.smear) : null });
    if (out) {
      keys(tl, out, { [axis]: [[t0, 0], [t1, sign * full * (o.depth != null ? o.depth : 0.33), e]], scale: [[t0, 1], [t1, o.recede != null ? o.recede : 0.94, e]] });
      const dark = o.darken != null ? o.darken : 0.45;
      drive(tl, t0, t1, (t) => { const p = e(clamp01((t - t0) / d)); out.style.filter = p > 0.001 ? 'brightness(' + (1 - dark * p).toFixed(3) + ')' : ''; });
      if (o.hideOut !== false) tl.set(out, { autoAlpha: 0 }, t1 + F(1));
    }
    return { start: t0, end: t1 };
  }
  // Iris from an object: the incoming scene opens as a circle from a point (a clicked button, a
  // dot), optionally from the object's own radius, so the object becomes the next world.
  function iris(tl, o) {
    const inn = el1(o.in), out = el1(o.out), at = o.at, d = o.duration != null ? o.duration : 0.6;
    if (inn) {
      hideUntil(tl, inn, at);
      matteIris(tl, inn, at, d, { x: o.x, y: o.y, r0: o.r0 || 0, feather: o.feather || 0, ease: o.ease || C.heavy });
    }
    if (out && o.push !== false) keys(tl, out, { scale: [[at, 1], [at + d, o.pushScale || 1.06, ease(o.ease, C.heavy)]] });
    return { start: at, end: at + d };
  }
  // Matte wipe: a feathered edge sweeps the incoming scene on at any angle. The incoming drifts
  // into place from the side the edge comes from; the outgoing pushes away a touch (scale up, so
  // no edge of it is ever exposed). Covered outgoing is hidden when done (hideOut: false keeps it).
  function wipe(tl, o) {
    const inn = el1(o.in), out = el1(o.out), at = o.at, d = o.duration != null ? o.duration : 0.7;
    const e = ease(o.ease, C.whip);
    const angle = o.angle != null ? o.angle : 90, a = (angle * Math.PI) / 180, px = o.parallax != null ? o.parallax : 60;
    if (inn) {
      hideUntil(tl, inn, at);
      matteLinear(tl, inn, at, d, { angle, feather: o.feather != null ? o.feather : 8, ease: e });
      if (px) keys(tl, inn, { x: [[at, -Math.sin(a) * px], [at + d, 0, C.land]], y: [[at, Math.cos(a) * px], [at + d, 0, C.land]] });
    }
    if (out) {
      if (px) keys(tl, out, { scale: [[at, 1], [at + d, o.pushScale || 1.04, e]] });
      if (o.hideOut !== false) tl.set(out, { autoAlpha: 0 }, at + d + F(1));
    }
    return { start: at, end: at + d };
  }
  // Zoom through: the outgoing scene accelerates past the lens into a point, the incoming grows
  // from smaller and settles; blur follows the zoom speed. (The owner's YouTube intros reject zoom-
  // throughs: keep it for explainers and launches.)
  function zoom(tl, o) {
    const out = el1(o.out), inn = el1(o.in), at = o.at;
    const total = o.duration != null ? o.duration : 0.6, dOut = total * 0.45, dIn = total * 0.55;
    const origin = o.origin || '50% 50%', max = o.blur != null ? o.blur : 14;
    if (out) {
      out.style.transformOrigin = origin;
      const k = keys(tl, out, { scale: [[at - dOut, 1], [at, o.scale || 3.2, C.accel]] });
      drive(tl, at - dOut, at, (t) => { const v = Math.abs(k.velocity('scale', t)) / k.value('scale', t); out.style.filter = v > 0.3 ? 'blur(' + Math.min(max, v * 1.6).toFixed(2) + 'px)' : ''; });
      tl.set(out, { autoAlpha: 0 }, at);
    }
    if (inn) {
      inn.style.transformOrigin = origin;
      hideUntil(tl, inn, at);
      const k = keys(tl, inn, { scale: [[at, o.fromScale || 0.62], [at + dIn, 1, C.land]] });
      drive(tl, at, at + dIn, (t) => { const v = Math.abs(k.velocity('scale', t)) / k.value('scale', t); inn.style.filter = v > 0.3 ? 'blur(' + Math.min(max, v * 1.6).toFixed(2) + 'px)' : ''; });
    }
    return { start: at - dOut, end: at + dIn };
  }
  // Dip cut: the outgoing frame darkens for a few frames before the hard cut, so the cut reads as meant.
  function dip(tl, o) {
    const out = el1(o.out), at = o.at, fr = o.frames || 3, amt = o.amount != null ? o.amount : 0.4;
    drive(tl, at - F(fr), at, (t) => { const p = clamp01((t - (at - F(fr))) / F(fr)); out.style.filter = p > 0 ? 'brightness(' + (1 - amt * p).toFixed(3) + ')' : ''; });
    tl.set(out, { autoAlpha: 0 }, at);
    return { start: at - F(fr), end: at };
  }
  // Bar sweep (from motion-pro): solid bars (brand colours) sweep across in uneven order until they
  // cover the frame at the seam, the scenes swap underneath, then the bars carry on and uncover the
  // incoming. bars: elements in a full-frame, overflow-hidden container above both scenes, full-width
  // rows for dir 'left' | 'right', full-height columns for 'up' | 'down'. They travel the way content
  // travels, punch in on ae.punch and launch out on ae.launch. The bars own their transform.
  function bars(tl, o) {
    const out = el1(o.out), inn = el1(o.in), at = o.at, list = toEls(o.bars);
    const dirInfo = DIRS[o.dir || 'left'], prop = dirInfo[0] === 'x' ? 'xPercent' : 'yPercent', sign = dirInfo[1];
    const d = o.duration != null ? o.duration : 0.42, dOut = d * 0.85, hold = o.hold != null ? o.hold : 0.06, spread = o.spread != null ? o.spread : 0.9;
    const eIn = ease(o.easeIn, LIB['ae.punch']), eOut = ease(o.easeOut, LIB['ae.launch']);
    const lastR = react(Math.max(0, list.length - 1), spread);
    list.forEach((b, i) => {
      const r = react(i, spread), t0 = at - d - lastR + r, t1 = at + hold + r;
      keys(tl, b, { [prop]: [[t0, -sign * 101], [t0 + d, 0, eIn], [t1, 0, LIN], [t1 + dOut, sign * 101, eOut]] });
    });
    if (out) tl.set(out, { autoAlpha: 0 }, at);
    if (inn) hideUntil(tl, inn, at);
    return { start: at - d - lastR, end: at + hold + lastR + dOut };
  }
  // 3D flip (from motion-pro): the outgoing scene hinges away to edge-on, the cut lands there, and
  // the incoming hinges in from the other side starting at the same angular speed, then settles.
  // GSAP's transformPerspective on each scene, so their parents are untouched. axis 'y' turns like a
  // door, 'x' like a lid. The scenes' transforms belong to it while it runs.
  function flipTx(tl, o) {
    const out = el1(o.out), inn = el1(o.in), at = o.at;
    const prop = o.axis === 'x' ? 'rotationX' : 'rotationY';
    const d = o.duration != null ? o.duration : 0.7, dOut = d / 2, dIn = d * 0.85;
    const ang = o.angle != null ? o.angle : 90, sc = o.scale != null ? o.scale : 0.86, P = o.perspective || 2200;
    const eOut = ease(o.outEase, LIB['easings.inCubic']);
    const s = Math.min(8, (endSlope(eOut) * dIn) / dOut);                   // incoming start slope that matches the seam speed
    const eIn = ease(o.inEase, bez(0.12, Math.min(1, 0.12 * s), 0.3, 1));
    if (out) {
      G().set(out, { transformPerspective: P });
      keys(tl, out, { [prop]: [[at - dOut, 0], [at, ang, eOut]], scale: [[at - dOut, 1], [at, sc, eOut]] });
      tl.set(out, { autoAlpha: 0 }, at);
    }
    if (inn) {
      G().set(inn, { transformPerspective: P });
      hideUntil(tl, inn, at);
      keys(tl, inn, { [prop]: [[at, -ang], [at + dIn, 0, eIn]], scale: [[at, sc], [at + dIn, 1, C.land]] });
    }
    return { start: at - dOut, end: at + dIn };
  }
  // Flash frame on a cut (from motion-pro): a full-frame overlay (white or the brand colour) pops to
  // `peak` at the seam, holds `hold` frames and decays over `decay` frames. Pass out / in to hard-cut
  // the scenes under it. Owns the overlay's opacity.
  // The owner bans flash cuts in his YouTube intros: keep it for launches, trailers and music cuts.
  function flash(tl, o) {
    const fl = el1(o.el), at = o.at;
    const peak = o.peak != null ? o.peak : 1, hold = F(o.hold != null ? o.hold : 2), dec = F(o.decay != null ? o.decay : 5);
    keys(tl, fl, { opacity: [[Math.max(0, at - F(1)), 0], [at, peak, HOLD], [at + hold, peak, LIN], [at + hold + dec, 0, LIB['easings.outQuad']]] });
    if (o.out) tl.set(el1(o.out), { autoAlpha: 0 }, at);
    if (o.in) hideUntil(tl, el1(o.in), at);
    return { start: at, end: at + hold + dec };
  }
  const tx = { whip, push, stack, iris, wipe, zoom, dip, bars, flip: flipTx, flash };

  // ------------------------------------------------------------------ finishing (opt-in only)

  // Film grain on a full-frame overlay (from motion-pro): a seeded noise tile is drawn once on a
  // canvas and jumps to a seeded position `fps` times a second, so every render repeats exactly.
  // Blend overlay or soft-light. Opt-in only, never a default: the owner's look is plain and restrained.
  // Owns the overlay's background, opacity and mix-blend-mode.
  // grain(tl, '#grain', { opacity: 0.12, amount: 0.55, size: 256, scale, fps: 12, seed: 11, blend: 'overlay', at, until })
  function grain(tl, target, opts) {
    const o = opts || {};
    const e = el1(target);
    const size = o.size || 256, seed = o.seed != null ? o.seed : 11, gfps = o.fps || 12, amt = o.amount != null ? o.amount : 0.55;
    const c = doc.createElement('canvas');
    c.width = c.height = size;
    const ctx = c.getContext('2d'), img = ctx.createImageData(size, size), r = rng(seed);
    for (let i = 0; i < size * size; i++) {
      const v = clamp(128 + (r() + r() + r() - 1.5) * 255 * amt, 0, 255);
      img.data[i * 4] = img.data[i * 4 + 1] = img.data[i * 4 + 2] = v;
      img.data[i * 4 + 3] = 255;
    }
    ctx.putImageData(img, 0, 0);
    Object.assign(e.style, { backgroundImage: 'url(' + c.toDataURL('image/png') + ')', backgroundSize: (o.scale || size) + 'px',
      mixBlendMode: o.blend || 'overlay', opacity: String(o.opacity != null ? o.opacity : 0.12), pointerEvents: 'none' });
    const at = o.at || 0, until = o.until != null ? o.until : rootDuration(e) || tl.duration();
    drive(tl, at, until, (t) => { const p = grainOffset(t, gfps, seed, size); e.style.backgroundPosition = p[0] + 'px ' + p[1] + 'px'; });
  }
  // Where the grain tile sits at time t: a seeded hash of the grain-frame index. Pure.
  function grainOffset(t, gfps, seed, size) {
    const k = Math.floor(t * gfps + 1e-6);
    return [Math.floor(hash01(k, seed) * size), Math.floor(hash01(k, seed + 3) * size)];
  }

  // RGB split on a hit (from motion-pro): an SVG filter pulls red and blue apart by `px` along
  // `angle` and the split decays over `duration`. A hit, never a look, and opt-in only: the owner rejects
  // chromatic / RGB effects in his YouTube intros. Owns the element's CSS filter while it runs (put it
  // on a wrapper that nothing else filters or smears). rgbSplit(tl, el, at, { px: 10, duration: 0.35, angle: 0 })
  let fxN = 0;
  function rgbSplit(tl, target, at, opts) {
    const o = opts || {};
    const els = toEls(target);
    const id = 'ae-rgb-' + (++fxN);
    const mk = (tag, attrs, parent) => {
      const n = doc.createElementNS(NS, tag);
      Object.keys(attrs).forEach((k) => n.setAttribute(k, attrs[k]));
      parent.appendChild(n);
      return n;
    };
    const f = doc.createElementNS(NS, 'filter');
    [['id', id], ['x', '-5%'], ['y', '-5%'], ['width', '110%'], ['height', '110%'], ['color-interpolation-filters', 'sRGB']].forEach((a) => f.setAttribute(a[0], a[1]));
    const A = '  0 0 0 1 0'; // keep alpha
    mk('feColorMatrix', { in: 'SourceGraphic', type: 'matrix', values: '1 0 0 0 0  0 0 0 0 0  0 0 0 0 0' + A, result: 'r' }, f);
    const oR = mk('feOffset', { in: 'r', dx: '0', dy: '0', result: 'ro' }, f);
    mk('feColorMatrix', { in: 'SourceGraphic', type: 'matrix', values: '0 0 0 0 0  0 1 0 0 0  0 0 0 0 0' + A, result: 'g' }, f);
    mk('feColorMatrix', { in: 'SourceGraphic', type: 'matrix', values: '0 0 0 0 0  0 0 0 0 0  0 0 1 0 0' + A, result: 'b' }, f);
    const oB = mk('feOffset', { in: 'b', dx: '0', dy: '0', result: 'bo' }, f);
    mk('feBlend', { in: 'ro', in2: 'g', mode: 'screen', result: 'rg' }, f);
    mk('feBlend', { in: 'rg', in2: 'bo', mode: 'screen' }, f);
    defsFor(els[0]).appendChild(f);
    const px = o.px != null ? o.px : 10, s = o.duration != null ? o.duration : 0.35, ang = ((o.angle || 0) * Math.PI) / 180;
    drive(tl, Math.max(0, at - F(1)), at + s, (t) => {
      const u = t - at, k = u >= 0 && u < s ? Math.pow(1 - u / s, 2) : 0, on = k > 0.01;
      if (on) {
        const dx = (Math.cos(ang) * px * k).toFixed(2), dy = (Math.sin(ang) * px * k).toFixed(2);
        oR.setAttribute('dx', dx); oR.setAttribute('dy', dy);
        oB.setAttribute('dx', String(-dx)); oB.setAttribute('dy', String(-dy));
      }
      els.forEach((e) => {
        if (on) { if (e._aeRgb !== id) { e.style.filter = 'url(#' + id + ')'; e._aeRgb = id; } }
        else if (e._aeRgb === id) { e.style.filter = ''; e._aeRgb = null; }
      });
    });
  }

  // ------------------------------------------------------------------ finish

  // Pad the timeline to the composition's length and register it for HyperFrames.
  function finish(tl, id, duration) {
    if (duration != null) tl.set({}, {}, duration);
    root.__timelines = root.__timelines || {};
    root.__timelines[id] = tl;
    return tl;
  }

  root.AE = {
    __aeMotion: true, version: '1.1.0',
    // time
    fps, setFps, F, snap, drive, finish, rootDuration,
    // curves
    bez, influence, C, LIB, curve, ease, spring, settle, withBounce: settle, startSlope, endSlope,
    // timing
    dur, react, beats, grid, hit, words,
    // keyframes and motion
    track, keys, smear, wiggle, shake, camera, camera3d, arc, anticipate, drag, exitTo, loop, ramp, controller, link, noise: noise1, rng,
    // text
    splitText, split: splitText, cut, textRange, revealWords, revealLines, textOut, typeOn, trackIn, scramble, roll, count, highlight,
    slam, flip, wiggly, odometer, digitRoll, swap, slot,
    // mattes, paths, transitions
    matte, trim, follow, tx,
    // finishing (opt-in only)
    grain, grainOffset, rgbSplit,
  };
})(typeof window !== 'undefined' ? window : globalThis);
