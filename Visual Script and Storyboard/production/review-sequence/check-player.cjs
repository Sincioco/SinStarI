/* Focused, isolated interaction checks. This does not claim browser visual QA. */
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.resolve(__dirname, '../..');
const html = fs.readFileSync(path.join(root, 'review.html'), 'utf8');
const config = JSON.parse(fs.readFileSync(path.join(__dirname, 'sequence.json'), 'utf8'));
// Use a known starting layout without modifying the user's live review preferences.
config.settings.layout = 'overlay';
config.settings.show_labels = true;
for (const clip of config.clips) { delete clip.panel_positions; clip.muted = false; }
const settle = async () => { for (let i = 0; i < 12; i++) await Promise.resolve(); };

class Element {
  constructor() {
    this.listeners = {}; this.dataset = {}; this.style = { setProperty() {} }; this.attributes = {};
    this.value = ''; this.currentTime = 0; this.duration = 5; this.readyState = 4;
    this.classes = new Set(); this.tagName = 'BUTTON';
    this.classList = { add: (...names) => names.forEach(n => this.classes.add(n)),
      remove: (...names) => names.forEach(n => this.classes.delete(n)),
      toggle: (name, on) => on ? this.classes.add(name) : this.classes.delete(name) };
  }
  addEventListener(name, fn) { (this.listeners[name] ||= []).push(fn); }
  removeEventListener() {}
  dispatch(name, extra = {}) { for (const fn of this.listeners[name] || []) fn({ target: this, ...extra }); }
  setAttribute(name, value) { this.attributes[name] = value; }
  replaceChildren(...children) { this.children = children; }
  pause() { this.paused = true; }
  async play() { this.paused = false; }
  load() {}
  click() { this.dispatch('click'); }
  closest() { return ['INPUT', 'TEXTAREA', 'SELECT'].includes(this.tagName) ? this : null; }
}

function player(initial, storage = new Map(), failSave = false) {
  const nodes = new Map([...html.matchAll(/id="([^"]+)"/g)].map(match => [match[1], new Element()]));
  const arrows = [...html.matchAll(/data-panel="([^"]+)" data-corner="([^"]+)"/g)].map(match => {
    const button = new Element(); button.dataset = { panel: match[1], corner: match[2] }; return button;
  });
  const document = new Element();
  document.getElementById = id => { assert(nodes.has(id), 'Missing HTML control: ' + id); return nodes.get(id); };
  document.querySelectorAll = () => arrows;
  document.createElement = () => new Element();
  nodes.get('sequence-stage').requestFullscreen = async () => { document.fullscreenElement = nodes.get('sequence-stage'); };
  document.exitFullscreen = async () => { document.fullscreenElement = null; };
  let exported;
  const server = structuredClone(initial), timers = new Map(); let nextTimer = 0;
  class AudioOwner {
    constructor() { player.audio = this; }
    configure(music, value) { this.value = value; }
    setVolumes(value) { this.value = value; }
    setClipMuted(value) { this.muted = value; }
    async start() { this.playing = true; }
    pause() { this.playing = false; }
    close() {}
  }
  const window = new Element(); window.SinStarSequenceAudio = AudioOwner;
  class LocalURL extends URL {}
  LocalURL.createObjectURL = blob => { exported = JSON.parse(blob.parts[0]); return 'blob:test'; };
  LocalURL.revokeObjectURL = () => {};
  const sandbox = { window, document, URL: LocalURL, URLSearchParams, location: new URL('http://localhost:8765/review.html'),
    performance: { now: () => 100 }, console, Blob: class { constructor(parts) { this.parts = parts; } },
    setInterval: () => 0, clearInterval() {}, setTimeout: fn => { timers.set(++nextTimer, fn); return nextTimer; },
    clearTimeout: id => timers.delete(id), localStorage: { getItem: k => storage.get(k), setItem: (k,v) => storage.set(k,v), removeItem: k => storage.delete(k) },
    fetch: async (url, options) => {
      if (options?.method !== 'POST') return { ok: true, json: async () => structuredClone(server) };
      if (failSave) return { ok: false };
      const patch = JSON.parse(options.body);
      for (const group of ['settings', 'audio']) Object.assign(server[group], patch[group]);
      for (const [id, value] of Object.entries(patch.clips || {})) Object.assign(server.clips.find(c => c.id === id), value);
      return { ok: true };
    } };
  vm.createContext(sandbox);
  for (const name of ['sequence-settings.js', 'sequence-player.js']) vm.runInContext(fs.readFileSync(path.join(root, 'asset', name), 'utf8'), sandbox);
  return { nodes, arrows, document, server, storage, window, audio: player.audio,
    export: () => { nodes.get('save-sequence').click(); return exported; },
    flush: async () => { const work = [...timers.values()]; timers.clear(); work.forEach(fn => fn()); await settle(); } };
}

(async () => {
  const p = player(config); await settle();
  const node = id => p.nodes.get(id);
  node('sequence-jump').value = '1'; node('sequence-jump').dispatch('change'); await settle();
  assert(node('scene-info-panel').classes.has('lower-left'), 'Scene information defaults to lower-left');
  assert(node('scene-context-panel').classes.has('lower-right'), 'Scene context defaults to lower-right');
  let prevented = false;
  p.document.dispatch('keydown', { code: 'Space', repeat: false, preventDefault() { prevented = true; } }); await settle();
  assert(prevented); assert.equal(node('sequence-play').textContent, 'Pause');
  const arrow = (panel, corner) => p.arrows.find(b => b.dataset.panel === panel && b.dataset.corner === corner).click();
  arrow('scene_info', 'upper-left');
  assert(node('scene-info-panel').classes.has('upper-left'), 'Moves during playback');
  arrow('scene_context', 'upper-right');
  node('mute-clip').checked = true; node('mute-clip').dispatch('change'); assert(p.audio.muted);
  node('next').click(); await settle();
  assert(!p.audio.muted, 'Next clip retains its own audio');
  arrow('scene_info', 'lower-right');
  assert(node('scene-context-panel').classes.has('lower-left'), 'Corner collision swaps only current clip');
  node('previous').click(); await settle();
  assert(node('scene-info-panel').classes.has('upper-left')); assert(p.audio.muted);
  assert.equal(node('sequence-play').textContent, 'Pause', 'Moving panels does not pause');
  node('review-layout').value = 'side-by-side'; node('review-layout').dispatch('change');
  assert(node('sequence-stage').classes.has('side-by-side'));
  await p.flush();
  assert.equal(p.server.clips[0].panel_positions.scene_info, 'upper-left'); assert(p.server.clips[0].muted);
  assert.equal(p.server.settings.layout, 'side-by-side');
  const reopened = player(p.server); await settle();
  reopened.nodes.get('next').click(); await settle();
  assert(reopened.nodes.get('scene-info-panel').classes.has('upper-left')); assert(reopened.audio.muted);
  assert(reopened.nodes.get('scene-context-panel').classes.has('upper-right'), 'Saved context position overrides the lower-right default');
  const exported = p.export(); assert(exported.clips[0].muted); assert.equal(exported.settings.layout, 'side-by-side');
  p.document.dispatch('keydown', { code: 'Space', repeat: false, preventDefault() {} }); await settle();
  assert.equal(node('sequence-play').textContent, 'Play Sequence');
  p.document.dispatch('keydown', { code: 'Space', repeat: true, preventDefault() {} }); await settle();
  assert.equal(node('sequence-play').textContent, 'Play Sequence', 'Held space does not toggle repeatedly');
  const input = new Element(); input.tagName = 'INPUT';
  p.document.dispatch('keydown', { target: input, code: 'Space', preventDefault() { assert.fail('Typing must retain Space'); } });
  const key = async code => { p.document.dispatch('keydown', { code, preventDefault() {} }); await settle(); };
  await key('End'); assert.equal(Number(node('sequence-jump').value), config.clips.length, 'End selects the last video, not credits');
  await key('ArrowRight'); assert.equal(Number(node('sequence-jump').value), config.clips.length, 'Next is bounded at the last video');
  await key('ArrowLeft'); assert.equal(Number(node('sequence-jump').value), config.clips.length - 1);
  await key('Home'); assert.equal(Number(node('sequence-jump').value), 1, 'Home selects first video');
  await key('ArrowLeft'); assert.equal(Number(node('sequence-jump').value), 1, 'Previous is bounded at the first video');
  await key('ArrowRight'); assert.equal(Number(node('sequence-jump').value), 2);
  assert.equal(node('sequence-play').textContent, 'Play Sequence', 'Navigation stays paused');
  const activeVideo = ['sequence-video-a','sequence-video-b'].map(node).find(video => !video.hidden);
  activeVideo.currentTime = 2;
  await key('ArrowUp'); assert.equal(node('review-layout').value, 'overlay');
  assert(!node('sequence-stage').classes.has('side-by-side'));
  assert.equal(activeVideo.currentTime, 2, 'Switching layout does not restart the clip');
  assert.equal(node('sequence-play').textContent, 'Play Sequence', 'Layout toggle stays paused');
  await p.flush(); assert.equal(p.server.settings.layout, 'overlay', 'Keyboard layout is saved for rendering');
  await key('ArrowUp'); assert.equal(node('review-layout').value, 'side-by-side');
  assert(node('sequence-stage').classes.has('side-by-side'));
  await p.flush(); assert.equal(p.server.settings.layout, 'side-by-side');
  await key('ArrowDown'); assert(p.document.fullscreenElement);
  await key('ArrowDown'); assert.equal(p.document.fullscreenElement, null);
  await key('Space'); await key('ArrowRight'); assert.equal(node('sequence-play').textContent, 'Pause', 'Navigation preserves playback');
  await key('ArrowUp'); assert.equal(node('sequence-play').textContent, 'Pause', 'Layout toggle preserves active playback');
  const fallback = player(config, new Map(), true); await settle();
  fallback.nodes.get('next').click(); await settle();
  fallback.arrows.find(b => b.dataset.panel === 'scene_info' && b.dataset.corner === 'lower-right').click();
  await fallback.flush(); assert(fallback.storage.size > 0);
  const recovered = player(config, fallback.storage, true); await settle(); recovered.nodes.get('next').click(); await settle();
  assert(recovered.nodes.get('scene-info-panel').classes.has('lower-right'), 'Browser recovery restores unsaved per-clip layout');
  const resetConfig = structuredClone(config);
  resetConfig.panel_layout_version = (config.panel_layout_version || 0) + 1;
  const oldCache = new Map([['SinStarSequenceSettings:v1:production/review-sequence/sequence.json', JSON.stringify({
    panel_layout_version: config.panel_layout_version || 0,
    clips: { [config.clips[0].id]: { muted: true, panel_positions: { scene_info: 'upper-left', scene_context: 'upper-right' } } },
    audio: { music_volume: 0.25 }
  })]]);
  const reset = player(resetConfig, oldCache); await settle(); reset.nodes.get('next').click(); await settle();
  assert(reset.nodes.get('scene-info-panel').classes.has('lower-left'), 'Old cached information position cannot undo a reset');
  assert(reset.nodes.get('scene-context-panel').classes.has('lower-right'), 'Old cached context position cannot undo a reset');
  assert(reset.audio.muted, 'Layout reset preserves mute settings');
  assert.equal(reset.audio.value.music_volume, 0.25, 'Layout reset preserves volume settings');
  await reset.flush(); assert.equal(reset.server.clips[0].panel_positions, undefined);
  const css = fs.readFileSync(path.join(root, 'asset/sequence-player.css'), 'utf8');
  assert(css.includes('.sequence-left:hover .panel-move'));
  assert(css.includes('inset: 0 0 0 70%'), 'Information column is on the right');
  console.log('Passed: all seven keyboard shortcuts, navigation bounds/state, live panel movement, per-clip layout/mute isolation, swaps, side-by-side, auto-save, reload, export, browser recovery.');
})().catch(error => { console.error(error); process.exitCode = 1; });
