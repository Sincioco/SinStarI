/* Direct playback of the same editable JSON used by the movie renderer. */
(() => {
  'use strict';
  const get = id => document.getElementById(id);
  const videos = [get('sequence-video-a'), get('sequence-video-b')];
  const audio = new window.SinStarSequenceAudio(videos, name => { get('music-track').textContent = name; });
  const state = { config: null, entries: [], index: 0, active: 0, playing: false, ready: false,
    request: 0, playRequest: 0, elapsed: 0, lastTick: performance.now(), finished: false };
  const configPath = new URLSearchParams(location.search).get('config') || 'production/review-sequence/sequence.json';
  const preferences = new window.SinStarSequenceSettings(configPath, () => {
    labels(current());
    audio.setVolumes(state.config.audio);
  });
  const status = text => { get('sequence-status').textContent = text; };
  const clock = seconds => `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, '0')}`;
  const source = path => new URL(path.replaceAll('\\', '/'), location.href).href;
  const current = () => state.entries[state.index];
  const currentVideo = () => videos[state.active];
  const isVideo = entry => entry && entry.kind === 'clip';
  const duration = () => isVideo(current())
    ? Number(current().duration_seconds ?? (currentVideo().duration - Number(current().start_seconds || 0)))
    : Number(current()?.seconds || 0);

  function controls() {
    get('sequence-stage').classList.toggle('is-paused', !state.playing);
    get('sequence-play').textContent = state.playing ? 'Pause' : state.finished ? 'Replay Sequence' : 'Play Sequence';
    get('sequence-play').disabled = !state.ready;
    get('previous').disabled = state.index <= 0;
    get('next').disabled = state.index >= state.entries.length - 1;
    get('sequence-jump').value = String(state.index);
  }
  function pause() {
    state.playing = false;
    state.playRequest++;
    videos.forEach(video => video.pause());
    audio.pause();
    controls();
  }
  async function play() {
    if (state.finished) await show(0, false);
    if (!state.ready) return;
    const request = ++state.playRequest;
    try {
      // Both original sound and music begin from this explicit user action.
      state.playing = true;
      state.lastTick = performance.now();
      await audio.start();
      if (request !== state.playRequest || !state.playing) return;
      if (isVideo(current())) await currentVideo().play();
      if (request === state.playRequest) { status(`Playing ${state.index + 1} of ${state.entries.length}`); controls(); }
    } catch (error) {
      if (request !== state.playRequest) return;
      pause();
      status('Playback needs attention. Select Play Sequence to retry. ' + error.message);
    }
  }
  function prepare(video, entry) {
    if (video.dataset.clipId === entry.id) return;
    video.dataset.clipId = entry.id;
    video.src = source(entry.file);
    video.load();
  }
  function preloadNext() {
    const next = state.entries[state.index + 1];
    if (isVideo(next)) prepare(videos[1 - state.active], next);
  }
  function ready(video) {
    if (video.readyState >= 2) return Promise.resolve();
    return new Promise((resolve, reject) => {
      let timeout;
      const clean = () => { clearTimeout(timeout); video.removeEventListener('loadeddata', loaded); video.removeEventListener('error', failed); };
      const loaded = () => { clean(); resolve(); };
      const failed = () => { clean(); reject(new Error('Local clip unavailable. Use Next to continue.')); };
      video.addEventListener('loadeddata', loaded, { once: true });
      video.addEventListener('error', failed, { once: true });
      timeout = setTimeout(failed, 15000);
    });
  }
  function labels(entry) {
    if (!entry) return;
    const sideBySide = state.config.settings.layout === 'side-by-side';
    const showLabels = state.config.settings.show_labels !== false;
    get('show-labels').checked = showLabels;
    get('review-layout').value = sideBySide ? 'side-by-side' : 'overlay';
    get('sequence-stage').classList.toggle('side-by-side', sideBySide && entry.kind === 'clip' && showLabels);
    get('mute-clip').disabled = entry.kind !== 'clip';
    get('mute-clip').checked = entry.muted === true;
    audio.setClipMuted(entry.muted === true);
    get('sequence-labels').hidden = entry.kind !== 'clip' || !get('show-labels').checked;
    if (entry.kind !== 'clip') return;
    positionPanels();
    get('sequence-chapter').textContent = entry.chapter;
    get('sequence-scene').textContent = entry.scene + ' — ' + entry.scene_title;
    get('sequence-filename').textContent = entry.file.split(/[\\/]/).pop();
    get('sequence-context').textContent = entry.context;
    const notes = state.config.scene_notes?.[entry.scene] || {};
    get('sequence-purpose').textContent = notes.purpose || 'Review the visual continuity and performance of this clip.';
    get('sequence-development').textContent = notes.character_development || 'No additional note supplied.';
    get('sequence-revelation').textContent = notes.revelation || 'No additional note supplied.';
    get('sequence-connections').textContent = notes.connections || 'No additional note supplied.';
    get('sequence-counter').textContent = `${String(state.index).padStart(3, '0')} / ${state.entries.length - 2}` + (entry.take ? ' · ' + entry.take : '');
  }
  async function show(index, keepPlaying = state.playing) {
    if (index < 0 || index >= state.entries.length) return;
    const request = ++state.request;
    state.playRequest++;
    state.index = index;
    state.elapsed = 0;
    state.ready = false;
    state.finished = false;
    state.playing = keepPlaying;
    videos.forEach(video => video.pause());
    controls();
    const entry = current();
    status('Loading ' + (entry.scene_title || entry.title) + '…');
    try {
      if (isVideo(entry)) {
        const slot = videos.findIndex(video => video.dataset.clipId === entry.id);
        const selected = slot < 0 ? 1 - state.active : slot;
        const video = videos[selected];
        prepare(video, entry);
        await ready(video);
        if (request !== state.request) return;
        video.currentTime = Number(entry.start_seconds || 0);
        state.active = selected;
        videos.forEach((item, i) => { item.hidden = i !== selected; });
        get('sequence-still').hidden = true;
        get('sequence-credits').hidden = true;
      } else {
        videos.forEach(video => { video.hidden = true; });
        get('sequence-still').hidden = entry.kind !== 'opening';
        get('sequence-credits').hidden = entry.kind !== 'credits';
      }
      labels(entry);
      state.ready = true;
      state.lastTick = performance.now();
      status(`${state.playing ? 'Playing' : 'Ready'} · ${entry.scene_title || entry.title}`);
      controls();
      preloadNext();
      tick();
      if (isVideo(entry) && state.playing) currentVideo().play().catch(error => {
        if (request !== state.request || !state.playing) return;
        pause(); status(error.message);
      });
    } catch (error) {
      if (request !== state.request) return;
      pause();
      labels(entry);
      state.ready = true;
      console.warn('Sequence preview:', entry.file, error);
      status(error.message);
      controls();
    }
  }
  function advance() {
    if (state.index + 1 < state.entries.length) show(state.index + 1, true);
    else {
      pause();
      state.finished = true;
      status('Sequence complete. Replay it or choose any clip above.');
      controls();
    }
  }
  function tick() {
    const now = performance.now();
    if (state.ready && current()) {
      if (isVideo(current())) state.elapsed = Math.max(0, currentVideo().currentTime - Number(current().start_seconds || 0));
      else if (state.playing) state.elapsed += (now - state.lastTick) / 1000;
      const seconds = duration();
      if (Number.isFinite(seconds) && seconds > 0) {
        get('clip-seek').max = seconds;
        get('clip-seek').value = Math.min(state.elapsed, seconds);
        get('clip-time').textContent = `${clock(state.elapsed)} / ${clock(seconds)}`;
        if (state.playing && state.elapsed >= seconds - 0.015) advance();
      }
    }
    state.lastTick = now;
  }
  function creditContent(config) {
    const credits = config.credits;
    get('sequence-still').src = source(config.opening.image);
    get('sequence-credits').style.backgroundImage = `url("${source(credits.background)}")`;
    get('credit-logo').src = source(credits.logo);
    get('credit-creator').textContent = credits.creator;
    get('credit-statement').textContent = credits.statement;
    get('credit-links').replaceChildren(...credits.links.map(([name, value]) => {
      const p = document.createElement('p');
      p.textContent = name + '  ' + value;
      return p;
    }));
  }
  async function configure(config, fromFile = false) {
    pause();
    if (!Array.isArray(config.clips) || !config.audio || !config.opening || !config.credits) throw Error('Use a review sequence JSON file.');
    for (const key of ['clip_volume', 'music_volume', 'master_volume']) {
      const number = Number(config.audio[key]);
      if (!Number.isFinite(number) || number < 0 || number > 2) throw Error(key + ' must be from 0 to 2.');
      config.audio[key] = number;
    }
    const clips = config.clips.filter(clip => clip.enabled !== false);
    if (!clips.length || new Set(clips.map(clip => clip.id)).size !== clips.length) throw Error('Clips need unique IDs.');
    state.config = config;
    preferences.configure(config, fromFile);
    state.entries = [{ kind: 'opening', title: 'Opening · Game Poster', ...config.opening },
      ...clips.map(clip => Object.assign(clip, { kind: 'clip' })),
      { kind: 'credits', title: 'Ending Credits', seconds: config.credits.seconds }];
    audio.configure(config.music, config.audio);
    get('sequence-stage').style.setProperty('--panel-opacity', config.settings.panel_opacity);
    get('sequence-jump').replaceChildren(...state.entries.map((entry, index) => {
      const option = document.createElement('option');
      option.value = index;
      option.textContent = entry.kind === 'clip' ? `${index}. ${entry.scene} · ${entry.scene_title}${entry.take ? ' · ' + entry.take : ''}` : entry.title;
      return option;
    }));
    get('sequence-jump').disabled = false;
    get('save-sequence').disabled = false;
    for (const name of ['clip', 'music', 'master']) {
      const value = config.audio[name + '_volume'];
      get(name + '-volume').value = value;
      get(name + '-volume-value').textContent = value.toFixed(2);
    }
    creditContent(config);
    await show(0, false);
  }
  async function reload() {
    try {
      const url = new URL(configPath, location.href);
      if (url.origin !== location.origin) throw Error('Choose a JSON file from this website folder.');
      const response = await fetch(url, { cache: 'no-store' });
      if (!response.ok) throw Error('Could not load the sequence JSON.');
      await configure(await response.json());
    } catch (error) { pause(); status(location.protocol === 'file:' ? 'Open Play Sequence.cmd to use the local player, or choose Open JSON.' : error.message); }
  }
  function moveClip(direction) {
    for (let index = state.index + direction; index >= 0 && index < state.entries.length; index += direction) {
      if (isVideo(state.entries[index])) { show(index); break; }
    }
  }
  get('sequence-play').addEventListener('click', () => state.playing ? pause() : play());
  let lastWheel = -Infinity;
  videos.forEach(video => {
    const visibleClip = () => isVideo(current()) && video === currentVideo() && !video.hidden;
    video.addEventListener('click', () => {
      if (state.ready && visibleClip()) state.playing ? pause() : play();
    });
    video.addEventListener('mousedown', event => {
      if (event.button !== 1 || !visibleClip()) return;
      event.preventDefault();
      toggleFullscreen();
    });
    video.addEventListener('wheel', event => {
      if (!visibleClip() || event.ctrlKey || event.metaKey || !event.deltaY) return;
      event.preventDefault();
      const now = performance.now();
      if (!state.ready || now - lastWheel < 300) return;
      lastWheel = now;
      moveClip(Math.sign(event.deltaY));
    }, { passive: false });
    video.addEventListener('contextmenu', event => {
      if (!visibleClip()) return;
      event.preventDefault();
      if (!state.ready) return;
      video.currentTime = Number(current().start_seconds || 0);
      tick();
      play();
    });
  });
  get('previous').addEventListener('click', () => show(state.index - 1));
  get('next').addEventListener('click', () => show(state.index + 1));
  get('sequence-jump').addEventListener('change', event => show(Number(event.target.value)));
  get('show-labels').addEventListener('change', event => preferences.edit({ settings: { show_labels: event.target.checked } }));
  get('review-layout').addEventListener('change', event => preferences.edit({ settings: { layout: event.target.value } }));
  get('mute-clip').addEventListener('change', event => {
    if (isVideo(current())) preferences.mute(current(), event.target.checked);
  });
  function positionPanels() {
    const positions = preferences.positions(current());
    const corners = preferences.corners;
    for (const [name, id] of [['scene_info', 'scene-info-panel'], ['scene_context', 'scene-context-panel']]) {
      get(id).classList.remove(...corners);
      get(id).classList.add(positions[name]);
    }
    document.querySelectorAll('[data-corner]').forEach(button => button.setAttribute('aria-pressed', String(positions[button.dataset.panel] === button.dataset.corner)));
  }
  document.querySelectorAll('[data-corner]').forEach(button => button.addEventListener('click', () => {
    if (isVideo(current())) preferences.move(current(), button.dataset.panel, button.dataset.corner);
  }));
  document.addEventListener('keydown', event => {
    const keys = ['Space', 'Home', 'End', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'];
    if (!keys.includes(event.code) || event.altKey || event.ctrlKey || event.metaKey ||
        event.target.closest('input,textarea,select,[contenteditable="true"]')) return;
    event.preventDefault();
    if (event.repeat || !state.entries.length) return;
    switch (event.code) {
      case 'Space': state.playing ? pause() : play(); break;
      case 'Home': show(state.entries.findIndex(isVideo)); break;
      case 'End': show(state.entries.findLastIndex(isVideo)); break;
      case 'ArrowUp':
        preferences.edit({ settings: {
          layout: state.config.settings.layout === 'side-by-side' ? 'overlay' : 'side-by-side'
        } });
        break;
      case 'ArrowDown': toggleFullscreen(); break;
      case 'ArrowLeft': moveClip(-1); break;
      case 'ArrowRight': moveClip(1); break;
    }
  });
  get('clip-seek').addEventListener('input', event => {
    state.elapsed = Number(event.target.value);
    state.lastTick = performance.now();
    if (isVideo(current())) currentVideo().currentTime = state.elapsed + Number(current().start_seconds || 0);
    tick();
  });
  async function toggleFullscreen() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else await get('sequence-stage').requestFullscreen();
    } catch (error) { status('Full screen could not open. ' + error.message); }
  }
  get('fullscreen').addEventListener('click', toggleFullscreen);
  get('reload-sequence').addEventListener('click', reload);
  get('open-sequence').addEventListener('change', async event => {
    try { if (event.target.files[0]) await configure(JSON.parse(await event.target.files[0].text()), true); }
    catch (error) { status(error.message); }
    event.target.value = '';
  });
  for (const name of ['clip', 'music', 'master']) get(name + '-volume').addEventListener('input', event => {
    if (!state.config) return;
    const value = Number(event.target.value);
    get(name + '-volume-value').textContent = value.toFixed(2);
    preferences.edit({ audio: { [name + '_volume']: value } });
  });
  get('save-sequence').addEventListener('click', () => {
    const url = URL.createObjectURL(new Blob([JSON.stringify(state.config, null, 2) + '\n'], { type: 'application/json' }));
    const link = document.createElement('a');
    link.href = url; link.download = configPath.split('/').pop() || 'sequence.json'; link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  });
  videos.forEach(video => video.addEventListener('ended', () => { if (state.playing && state.ready && video === currentVideo()) advance(); }));
  const timer = setInterval(tick, 100);
  window.addEventListener('pagehide', event => { pause(); preferences.save(); if (!event.persisted) { audio.close(); clearInterval(timer); } });
  reload();
})();
