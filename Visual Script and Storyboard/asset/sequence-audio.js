/* One audio owner for original clips, continuous music and live volume controls. */
window.SinStarSequenceAudio = class {
  constructor(videos, announce) {
    this.videos = videos;
    this.announce = announce;
    this.music = [new Audio(), new Audio()];
    this.music.forEach(audio => { audio.preload = 'auto'; });
    this.active = 0;
    this.track = 0;
    this.playing = false;
    this.request = 0;
    this.timer = setInterval(() => this.tick(), 100);
  }
  configure(settings, volumes) {
    this.pause();
    this.settings = settings;
    this.volumes = volumes;
    this.active = this.track = 0;
    this.fadeEnd = null;
    this.started = false;
    this.music.forEach(audio => { audio.removeAttribute('src'); audio.load(); });
    this.setVolumes(volumes);
  }
  initialize() {
    if (this.context) return;
    this.context = new AudioContext();
    this.master = this.context.createGain();
    this.clipGain = this.context.createGain();
    this.musicGain = this.context.createGain();
    this.limiter = this.context.createDynamicsCompressor();
    this.limiter.threshold.value = -1;
    this.limiter.knee.value = 0;
    this.limiter.ratio.value = 20;
    this.clipGain.connect(this.master);
    this.musicGain.connect(this.master);
    this.master.connect(this.limiter).connect(this.context.destination);
    this.videos.forEach(video => this.context.createMediaElementSource(video).connect(this.clipGain));
    this.faders = this.music.map(audio => {
      const gain = this.context.createGain();
      this.context.createMediaElementSource(audio).connect(gain).connect(this.musicGain);
      return gain;
    });
    this.setVolumes(this.volumes);
  }
  setVolumes(value) {
    this.volumes = value;
    if (!this.context) return;
    this.clipGain.gain.value = this.clipMuted ? 0 : value.clip_volume;
    this.musicGain.gain.value = value.music_volume;
    this.master.gain.value = value.master_volume;
  }
  setClipMuted(muted) {
    this.clipMuted = muted;
    if (this.volumes) this.setVolumes(this.volumes);
  }
  prepare(slot, track) {
    this.music[slot].src = this.settings.files[track].replaceAll('\\', '/');
    this.music[slot].load();
  }
  async start() {
    const request = ++this.request;
    this.initialize();
    await this.context.resume();
    if (request !== this.request) return;
    this.playing = true;
    if (!this.settings.files.length) return;
    if (!this.started) {
      this.prepare(0, 0);
      this.prepare(1, 1 % this.settings.files.length);
      this.faders[0].gain.cancelScheduledValues(0);
      this.faders[1].gain.cancelScheduledValues(0);
      this.faders[0].gain.value = 1;
      this.faders[1].gain.value = 0;
      this.started = true;
    }
    await this.music[this.active].play();
    if (request !== this.request) return;
    if (this.fadeEnd !== null) await this.music[1 - this.active].play();
    this.announce(this.settings.files[this.track].split(/[\\/]/).pop());
  }
  pause() {
    this.request++;
    this.playing = false;
    this.music.forEach(audio => audio.pause());
    if (this.context) this.context.suspend();
  }
  tick() {
    if (!this.playing || !this.started) return;
    const current = this.music[this.active];
    if (this.fadeEnd !== null) {
      if (this.context.currentTime < this.fadeEnd) return;
      current.pause();
      this.active = 1 - this.active;
      this.track = (this.track + 1) % this.settings.files.length;
      this.prepare(1 - this.active, (this.track + 1) % this.settings.files.length);
      this.fadeEnd = null;
      this.announce(this.settings.files[this.track].split(/[\\/]/).pop());
      return;
    }
    const remaining = current.duration - current.currentTime;
    if (!Number.isFinite(remaining) || remaining > this.settings.crossfade_seconds) return;
    const next = 1 - this.active;
    const seconds = Math.max(0.05, remaining);
    this.fadeEnd = this.context.currentTime + seconds;
    this.music[next].currentTime = 0;
    this.music[next].play().catch(error => { this.pause(); this.announce('Music paused: ' + error.message); });
    this.faders[this.active].gain.setValueAtTime(1, this.context.currentTime);
    this.faders[this.active].gain.linearRampToValueAtTime(0, this.fadeEnd);
    this.faders[next].gain.setValueAtTime(0, this.context.currentTime);
    this.faders[next].gain.linearRampToValueAtTime(1, this.fadeEnd);
  }
  close() {
    this.pause();
    clearInterval(this.timer);
    if (this.context) this.context.close();
  }
};
