/* Review preferences: per-clip layout/mute, local recovery and renderer JSON saves. */
window.SinStarSequenceSettings = class {
  constructor(configPath, changed) {
    this.path = configPath;
    this.changed = changed;
    this.key = 'SinStarSequenceSettings:v1:' + configPath;
    this.corners = ['upper-left', 'upper-right', 'lower-left', 'lower-right'];
    this.pending = {};
    this.saving = false;
    this.notice = document.getElementById('settings-status');
  }
  configure(config, fromFile = false) {
    clearTimeout(this.timer);
    this.config = config;
    this.fromFile = fromFile;
    this.pending = {};
    if (!fromFile) {
      try {
        const saved = JSON.parse(localStorage.getItem(this.key) || 'null');
        if (saved && typeof saved === 'object' && !Array.isArray(saved)) {
          this.apply(saved);
          this.pending = saved;
        }
      } catch { /* A restricted browser can still save directly to the local server. */ }
    }
    this.notice.textContent = fromFile ? 'Opened JSON: use Save JSON to keep edits in this file.' : 'Settings loaded from the render JSON.';
    if (Object.keys(this.pending).length) this.schedule();
  }
  positions(clip) {
    const defaults = { scene_info: 'upper-left', scene_context: 'upper-right' };
    const result = { ...defaults };
    for (const value of [this.config.panel_positions, clip?.panel_positions]) {
      for (const name of Object.keys(defaults)) if (this.corners.includes(value?.[name])) result[name] = value[name];
    }
    if (result.scene_info === result.scene_context) result.scene_context = this.corners.find(corner => corner !== result.scene_info);
    return result;
  }
  apply(patch) {
    for (const [id, value] of Object.entries(patch.clips || {})) {
      const clip = this.config.clips.find(item => item.id === id);
      if (!clip || !value) continue;
      if (typeof value.muted === 'boolean') clip.muted = value.muted;
      if (value.panel_positions) clip.panel_positions = this.positions({ panel_positions: value.panel_positions });
    }
    if (['overlay', 'side-by-side'].includes(patch.settings?.layout)) this.config.settings.layout = patch.settings.layout;
    if (typeof patch.settings?.show_labels === 'boolean') this.config.settings.show_labels = patch.settings.show_labels;
    for (const name of ['clip_volume', 'music_volume', 'master_volume']) {
      const value = patch.audio?.[name];
      if (typeof value === 'number' && Number.isFinite(value) && value >= 0 && value <= 2) this.config.audio[name] = value;
    }
  }
  edit(patch) {
    this.apply(patch);
    for (const group of ['clips', 'settings', 'audio']) {
      if (!patch[group]) continue;
      this.pending[group] = { ...this.pending[group], ...patch[group] };
    }
    try { if (!this.fromFile) localStorage.setItem(this.key, JSON.stringify(this.pending)); } catch { }
    this.changed();
    this.schedule();
  }
  move(clip, name, corner) {
    const positions = this.positions(clip);
    const other = name === 'scene_info' ? 'scene_context' : 'scene_info';
    if (positions[other] === corner) positions[other] = positions[name];
    positions[name] = corner;
    this.edit({ clips: { [clip.id]: { muted: clip.muted === true, panel_positions: positions } } });
  }
  mute(clip, muted) {
    this.edit({ clips: { [clip.id]: { muted, panel_positions: this.positions(clip) } } });
  }
  schedule() {
    clearTimeout(this.timer);
    if (this.fromFile) { this.notice.textContent = 'Changes kept in this session. Save JSON for rendering.'; return; }
    this.notice.textContent = 'Saving settings for the MP4…';
    this.timer = setTimeout(() => this.save(), 250);
  }
  async save() {
    if (this.fromFile || this.saving || !Object.keys(this.pending).length) return;
    this.saving = true;
    const patch = this.pending;
    const config = this.config;
    this.pending = {};
    try {
      const response = await fetch('/__sinstar/review-settings', { method: 'POST', keepalive: true,
        headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ config: this.path, ...patch }) });
      if (!response.ok) throw Error('Local JSON save unavailable');
      if (this.config !== config) return;
      if (Object.keys(this.pending).length) this.schedule();
      else {
        try { localStorage.removeItem(this.key); } catch { }
        this.notice.textContent = 'Saved for the MP4. Render again to update the movie.';
      }
    } catch {
      if (this.config !== config) return;
      for (const group of ['clips', 'settings', 'audio']) {
        if (patch[group]) this.pending[group] = { ...patch[group], ...this.pending[group] };
      }
      let remembered = false;
      try { localStorage.setItem(this.key, JSON.stringify(this.pending)); remembered = true; } catch { }
      this.notice.textContent = (remembered ? 'Saved in this browser. ' : 'Changes are only in this session. ') +
        'Use Save JSON for rendering, or restart Start Website.cmd for automatic file saves.';
    } finally {
      this.saving = false;
      if (this.config !== config && !this.fromFile && Object.keys(this.pending).length) this.schedule();
    }
  }
};
