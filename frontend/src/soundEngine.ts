/**
 * Web Audio API RPG Sound Synthesizer Engine.
 * Generates rich, low-latency procedural audio effects without external MP3 dependencies.
 */

class SoundEngine {
  private ctx: AudioContext | null = null;
  private muted: boolean = false;

  constructor() {
    // Read saved mute state from localStorage
    const savedMute = localStorage.getItem('questflow_sfx_muted');
    this.muted = savedMute === 'true';
  }

  private getContext(): AudioContext | null {
    if (this.muted) return null;
    if (!this.ctx) {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume().catch(() => {});
    }
    return this.ctx;
  }

  public isMuted(): boolean {
    return this.muted;
  }

  public setMuted(val: boolean) {
    this.muted = val;
    localStorage.setItem('questflow_sfx_muted', String(val));
  }

  public toggleMute(): boolean {
    this.setMuted(!this.muted);
    return this.muted;
  }

  /**
   * Satisfying Quest Completion arpeggio
   */
  public playQuestComplete() {
    const ctx = this.getContext();
    if (!ctx) return;

    const now = ctx.currentTime;
    const notes = [523.25, 659.25, 783.99, 1046.50]; // C5, E5, G5, C6
    
    notes.forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'triangle';
      osc.frequency.setValueAtTime(freq, now + idx * 0.08);

      gain.gain.setValueAtTime(0.001, now + idx * 0.08);
      gain.gain.exponentialRampToValueAtTime(0.18, now + idx * 0.08 + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + idx * 0.08 + 0.35);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now + idx * 0.08);
      osc.stop(now + idx * 0.08 + 0.4);
    });
  }

  /**
   * Crisp Gold Coin ping
   */
  public playCoinPickup() {
    const ctx = this.getContext();
    if (!ctx) return;

    const now = ctx.currentTime;
    const freqs = [987.77, 1318.51]; // B5, E6

    freqs.forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(freq, now + idx * 0.06);

      gain.gain.setValueAtTime(0.001, now + idx * 0.06);
      gain.gain.exponentialRampToValueAtTime(0.15, now + idx * 0.06 + 0.01);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + idx * 0.06 + 0.25);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now + idx * 0.06);
      osc.stop(now + idx * 0.06 + 0.3);
    });
  }

  /**
   * Majestic Level-Up Fanfare
   */
  public playLevelUpFanfare() {
    const ctx = this.getContext();
    if (!ctx) return;

    const now = ctx.currentTime;
    const chords = [
      [523.25, 659.25], // C5, E5
      [587.33, 739.99], // D5, F#5
      [659.25, 830.61], // E5, G#5
      [783.99, 987.77, 1046.50, 1318.51, 1567.98] // Grand Major Chord
    ];

    chords.forEach((chordNotes, chordIdx) => {
      const startTime = now + chordIdx * 0.14;
      const duration = chordIdx === chords.length - 1 ? 1.2 : 0.22;

      chordNotes.forEach((freq) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(freq, startTime);

        gain.gain.setValueAtTime(0.001, startTime);
        gain.gain.exponentialRampToValueAtTime(0.12, startTime + 0.04);
        gain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start(startTime);
        osc.stop(startTime + duration + 0.05);
      });
    });
  }

  /**
   * Boss Battle Weapon Strike / Slash
   */
  public playBossSlash() {
    const ctx = this.getContext();
    if (!ctx) return;

    const now = ctx.currentTime;
    // Noise burst + low pitch drop
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sawtooth';
    osc.frequency.setValueAtTime(320, now);
    osc.frequency.exponentialRampToValueAtTime(60, now + 0.18);

    gain.gain.setValueAtTime(0.25, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.2);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start(now);
    osc.stop(now + 0.22);
  }

  /**
   * Equip Gear Click
   */
  public playEquipItem() {
    const ctx = this.getContext();
    if (!ctx) return;

    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(440, now);
    osc.frequency.exponentialRampToValueAtTime(880, now + 0.08);

    gain.gain.setValueAtTime(0.12, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.1);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start(now);
    osc.stop(now + 0.12);
  }

  /**
   * Rare Loot Drop Shimmer
   */
  public playLootDrop() {
    const ctx = this.getContext();
    if (!ctx) return;

    const now = ctx.currentTime;
    const freqs = [784, 988, 1175, 1568, 2093];

    freqs.forEach((f, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = 'sine';
      osc.frequency.setValueAtTime(f, now + i * 0.05);

      gain.gain.setValueAtTime(0.001, now + i * 0.05);
      gain.gain.exponentialRampToValueAtTime(0.1, now + i * 0.05 + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + i * 0.05 + 0.35);

      osc.connect(gain);
      gain.connect(ctx.destination);

      osc.start(now + i * 0.05);
      osc.stop(now + i * 0.05 + 0.4);
    });
  }

  /**
   * Subtle UI Button hover tick
   */
  public playButtonTick() {
    const ctx = this.getContext();
    if (!ctx) return;

    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = 'sine';
    osc.frequency.setValueAtTime(800, now);

    gain.gain.setValueAtTime(0.03, now);
    gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.03);

    osc.connect(gain);
    gain.connect(ctx.destination);

    osc.start(now);
    osc.stop(now + 0.04);
  }
}

export const sound = new SoundEngine();
