"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

/**
 * Shikshak AI — LessonPlayer component.
 *
 * Professional custom classroom video player:
 * - Direct HTTP 206 Range seeking support (no restarts on click or seek)
 * - Custom interactive scrubber time bar with dragging & hover preview
 * - Robust -10s and +10s seek buttons with safe duration bounds
 * - Fullscreen, volume/mute, and playback rate (1x, 1.25x, 1.5x, 2x)
 * - Synchronized caption overlay with high-contrast gradient
 * - Synchronized scrolling transcript drawer
 * - Keyboard shortcuts: Space (play/pause), ←/J (-10s), →/L (+10s), M (mute), F (fullscreen)
 */
export interface LessonPlayerProps {
  videoUrl: string | null;
  status: "pending" | "rendering" | "ready" | "failed";
  narrationScript: string;
  language: string;
  onLanguageChange: (lang: string) => void;
}

const LOADING_MESSAGES: Record<string, string> = {
  pending: "Planning your lesson…",
  rendering: "Rendering your interactive teacher & scientific visuals…",
};

/** Format seconds into mm:ss string. */
function formatTime(seconds: number): string {
  if (!Number.isFinite(seconds) || seconds < 0) return "0:00";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
}

/** Split narration into sentences for transcript sync. */
function splitSentences(text: string): string[] {
  if (!text) return [];
  return text
    .split(/(?<=[.!?।])\s+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

export function LessonPlayer({
  videoUrl,
  status,
  narrationScript,
  language,
  onLanguageChange,
}: LessonPlayerProps) {
  const containerRef = React.useRef<HTMLDivElement>(null);
  const videoRef = React.useRef<HTMLVideoElement>(null);
  const progressBarRef = React.useRef<HTMLDivElement>(null);
  const transcriptRef = React.useRef<HTMLDivElement>(null);

  const [isPlaying, setIsPlaying] = React.useState(false);
  const [currentTime, setCurrentTime] = React.useState(0);
  const [duration, setDuration] = React.useState(0);
  const [bufferedEnd, setBufferedEnd] = React.useState(0);
  const [isMuted, setIsMuted] = React.useState(false);
  const [volume, setVolume] = React.useState(1);
  const [playbackRate, setPlaybackRate] = React.useState(1);
  const [showCaptions, setShowCaptions] = React.useState(true);
  const [transcriptOpen, setTranscriptOpen] = React.useState(false);
  const [seekFeedback, setSeekFeedback] = React.useState<{ text: string; id: number } | null>(null);
  const [isDragging, setIsDragging] = React.useState(false);
  const [hoverTime, setHoverTime] = React.useState<number | null>(null);

  const sentences = React.useMemo(
    () => splitSentences(narrationScript),
    [narrationScript],
  );

  // Estimate which sentence is currently being spoken based on video time
  const activeSentenceIdx = React.useMemo(() => {
    if (!duration || !sentences.length) return 0;
    const progress = currentTime / Math.max(1, duration);
    return Math.min(
      sentences.length - 1,
      Math.floor(progress * sentences.length),
    );
  }, [currentTime, duration, sentences]);

  // Auto-scroll transcript to active sentence
  React.useEffect(() => {
    if (!transcriptOpen) return;
    const container = transcriptRef.current;
    if (!container) return;
    const activeEl = container.querySelector(`[data-sentence="${activeSentenceIdx}"]`);
    if (activeEl) {
      activeEl.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }, [activeSentenceIdx, transcriptOpen]);

  // Video event handlers
  const handleTimeUpdate = React.useCallback(() => {
    const vid = videoRef.current;
    if (!vid) return;
    if (!isDragging) {
      setCurrentTime(vid.currentTime);
    }
    if (vid.buffered.length > 0) {
      try {
        setBufferedEnd(vid.buffered.end(vid.buffered.length - 1));
      } catch {
        // buffered range may shift
      }
    }
  }, [isDragging]);

  const handleLoadedMetadata = React.useCallback(() => {
    const vid = videoRef.current;
    if (!vid) return;
    if (Number.isFinite(vid.duration) && vid.duration > 0) {
      setDuration(vid.duration);
    }
  }, []);

  const handleDurationChange = React.useCallback(() => {
    const vid = videoRef.current;
    if (vid && Number.isFinite(vid.duration) && vid.duration > 0) {
      setDuration(vid.duration);
    }
  }, []);

  // Play / Pause Toggle
  const togglePlay = React.useCallback(() => {
    const vid = videoRef.current;
    if (!vid) return;
    if (vid.paused) {
      vid.play().catch(() => {});
    } else {
      vid.pause();
    }
  }, []);

  // Seek helper (-10s / +10s) with strict safe duration fallback
  const handleSeek = React.useCallback((offsetSeconds: number) => {
    const vid = videoRef.current;
    if (!vid) return;

    const dur = Number.isFinite(vid.duration) && vid.duration > 0
      ? vid.duration
      : duration > 0
      ? duration
      : 3600;

    const current = Number.isFinite(vid.currentTime) ? vid.currentTime : 0;
    const targetTime = Math.max(0, Math.min(dur, current + offsetSeconds));

    vid.currentTime = targetTime;
    setCurrentTime(targetTime);

    setSeekFeedback({
      text: offsetSeconds > 0 ? `+${offsetSeconds}s ⤏` : `⤎ ${Math.abs(offsetSeconds)}s`,
      id: Date.now(),
    });
    setTimeout(() => setSeekFeedback(null), 800);
  }, [duration]);

  // Custom Scrubber Click / Drag Seek
  const seekToPosition = React.useCallback(
    (clientX: number) => {
      const bar = progressBarRef.current;
      const vid = videoRef.current;
      if (!bar || !vid) return;

      const rect = bar.getBoundingClientRect();
      const ratio = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
      const dur = Number.isFinite(vid.duration) && vid.duration > 0 ? vid.duration : duration;

      if (dur > 0) {
        const target = ratio * dur;
        vid.currentTime = target;
        setCurrentTime(target);
      }
    },
    [duration]
  );

  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    setIsDragging(true);
    seekToPosition(e.clientX);
  };

  React.useEffect(() => {
    if (!isDragging) return;

    const handleMouseMove = (e: MouseEvent) => {
      seekToPosition(e.clientX);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    window.addEventListener("mousemove", handleMouseMove);
    window.addEventListener("mouseup", handleMouseUp);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
      window.removeEventListener("mouseup", handleMouseUp);
    };
  }, [isDragging, seekToPosition]);

  const handleMouseMoveHover = (e: React.MouseEvent<HTMLDivElement>) => {
    const bar = progressBarRef.current;
    if (!bar) return;
    const rect = bar.getBoundingClientRect();
    const ratio = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
    const dur = Number.isFinite(duration) && duration > 0 ? duration : 0;
    setHoverTime(ratio * dur);
  };

  const handleMouseLeaveHover = () => {
    setHoverTime(null);
  };

  // Keyboard navigation
  React.useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (["INPUT", "TEXTAREA", "SELECT"].includes((e.target as HTMLElement)?.tagName)) {
        return;
      }

      if (e.key === " " || e.key === "k" || e.key === "K") {
        e.preventDefault();
        togglePlay();
      } else if (e.key === "ArrowLeft" || e.key === "j" || e.key === "J") {
        e.preventDefault();
        handleSeek(-10);
      } else if (e.key === "ArrowRight" || e.key === "l" || e.key === "L") {
        e.preventDefault();
        handleSeek(10);
      } else if (e.key === "m" || e.key === "M") {
        e.preventDefault();
        const vid = videoRef.current;
        if (vid) {
          vid.muted = !vid.muted;
          setIsMuted(vid.muted);
        }
      } else if (e.key === "f" || e.key === "F") {
        e.preventDefault();
        if (!document.fullscreenElement) {
          containerRef.current?.requestFullscreen?.();
        } else {
          document.exitFullscreen?.();
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [togglePlay, handleSeek]);

  // Volume & speed helpers
  const handleVolumeChange = (newVol: number) => {
    setVolume(newVol);
    const vid = videoRef.current;
    if (vid) {
      vid.volume = newVol;
      vid.muted = newVol === 0;
      setIsMuted(newVol === 0);
    }
  };

  const toggleMute = () => {
    const vid = videoRef.current;
    if (!vid) return;
    vid.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const cycleSpeed = () => {
    const speeds = [1, 1.25, 1.5, 2];
    const nextIdx = (speeds.indexOf(playbackRate) + 1) % speeds.length;
    const nextSpeed = speeds[nextIdx];
    setPlaybackRate(nextSpeed);
    if (videoRef.current) {
      videoRef.current.playbackRate = nextSpeed;
    }
  };

  const toggleFullscreen = () => {
    if (!document.fullscreenElement) {
      containerRef.current?.requestFullscreen?.();
    } else {
      document.exitFullscreen?.();
    }
  };

  const currentCaption = sentences[activeSentenceIdx] || "";
  const progressPercent = duration > 0 ? Math.min(100, (currentTime / duration) * 100) : 0;
  const bufferedPercent = duration > 0 ? Math.min(100, (bufferedEnd / duration) * 100) : 0;

  return (
    <div ref={containerRef} className="w-full select-none">
      {/* Video Canvas Stage */}
      <div
        className="relative aspect-video w-full overflow-hidden rounded-xl bg-black group border border-white/10 shadow-inner cursor-pointer"
        onClick={status === "ready" ? togglePlay : undefined}
      >
        {videoUrl && status === "ready" ? (
          <>
            <video
              ref={videoRef}
              src={videoUrl}
              className="h-full w-full object-contain pointer-events-none"
              autoPlay
              muted={isMuted}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
              onTimeUpdate={handleTimeUpdate}
              onLoadedMetadata={handleLoadedMetadata}
              onDurationChange={handleDurationChange}
              playsInline
            >
              {showCaptions && (
                <track
                  kind="captions"
                  srcLang={language}
                  label={language}
                  default
                />
              )}
            </video>

            {/* Center Play/Pause Watermark on Pause */}
            {!isPlaying && (
              <div className="pointer-events-none absolute inset-0 flex items-center justify-center bg-black/30 transition-all">
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-black/75 text-white backdrop-blur-md border border-white/20 shadow-2xl transition-transform transform scale-100 group-hover:scale-110">
                  <svg className="w-7 h-7 fill-current ml-1" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </div>
              </div>
            )}

            {/* Visual seek feedback toast */}
            {seekFeedback && (
              <div className="pointer-events-none absolute inset-0 flex items-center justify-center animate-fade-in z-20">
                <div className="rounded-2xl bg-black/85 px-6 py-3 text-lg font-bold text-sky-400 backdrop-blur-md shadow-2xl border border-sky-500/30">
                  {seekFeedback.text}
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="flex h-full w-full items-center justify-center text-center text-white p-6">
            <div>
              {status === "rendering" && (
                <div className="mb-4 flex justify-center">
                  <div className="h-10 w-10 animate-spin rounded-full border-3 border-sky-500/20 border-t-sky-400" />
                </div>
              )}
              <div className="mb-3 text-4xl">
                {status === "failed" ? "⚠️" : "🧪"}
              </div>
              <p className="text-body-md font-medium text-white/90">
                {status === "failed"
                  ? "Video render unavailable — transcript below"
                  : LOADING_MESSAGES[status] ?? "Loading lesson…"}
              </p>
            </div>
          </div>
        )}

        {/* Subtitle Bar (Bottom Overlay) */}
        {showCaptions && currentCaption && status === "ready" && (
          <div className="pointer-events-none absolute bottom-3 inset-x-0 text-center px-4 z-10">
            <span className="inline-block rounded-lg bg-black/80 px-3.5 py-1.5 text-xs md:text-sm font-medium text-white shadow-lg border border-white/10 backdrop-blur-md max-w-[90%] leading-relaxed">
              {currentCaption}
            </span>
          </div>
        )}
      </div>

      {/* Modern Custom Video Player Control Deck */}
      <div className="mt-3 space-y-2 rounded-xl bg-black/40 p-3 border border-white/10 backdrop-blur-sm">
        {/* Interactive Scrubber Timeline */}
        <div
          ref={progressBarRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMoveHover}
          onMouseLeave={handleMouseLeaveHover}
          className="group relative flex h-4 w-full cursor-pointer items-center py-1.5"
          title="Click or drag to seek"
        >
          {/* Base Track */}
          <div className="relative h-1.5 w-full rounded-full bg-white/20 transition-all group-hover:h-2">
            {/* Buffered Progress */}
            <div
              className="absolute left-0 top-0 h-full rounded-full bg-white/30 transition-all"
              style={{ width: `${bufferedPercent}%` }}
            />
            {/* Played Progress */}
            <div
              className="absolute left-0 top-0 h-full rounded-full bg-gradient-to-r from-sky-500 to-indigo-400"
              style={{ width: `${progressPercent}%` }}
            />
            {/* Scrubber Knob */}
            <div
              className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 h-3.5 w-3.5 rounded-full bg-white shadow-md border-2 border-sky-400 transition-transform transform scale-90 group-hover:scale-125"
              style={{ left: `${progressPercent}%` }}
            />
          </div>

          {/* Hover Time Tooltip */}
          {hoverTime !== null && (
            <div
              className="pointer-events-none absolute -top-7 -translate-x-1/2 rounded bg-black/90 px-2 py-0.5 text-[10px] font-mono font-semibold text-sky-300 border border-white/10 shadow"
              style={{
                left: `${duration > 0 ? Math.min(100, Math.max(0, (hoverTime / duration) * 100)) : 0}%`,
              }}
            >
              {formatTime(hoverTime)}
            </div>
          )}
        </div>

        {/* Toolbar Buttons Row */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-white">
          {/* Left: Play/Pause, -10s, +10s, Volume, Timestamp */}
          <div className="flex items-center gap-1.5 sm:gap-2">
            {/* Play/Pause Button */}
            <button
              type="button"
              onClick={togglePlay}
              disabled={status !== "ready"}
              className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/10 hover:bg-white/20 active:scale-95 disabled:opacity-40 transition-all"
              aria-label={isPlaying ? "Pause" : "Play"}
              title={isPlaying ? "Pause (Space)" : "Play (Space)"}
            >
              {isPlaying ? (
                <svg className="w-4 h-4 fill-current" viewBox="0 0 24 24">
                  <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
                </svg>
              ) : (
                <svg className="w-4 h-4 fill-current ml-0.5" viewBox="0 0 24 24">
                  <path d="M8 5v14l11-7z" />
                </svg>
              )}
            </button>

            {/* Rewind -10s Button */}
            <button
              type="button"
              onClick={() => handleSeek(-10)}
              disabled={status !== "ready"}
              className="flex items-center gap-1 rounded-lg bg-white/10 px-2.5 py-1.5 text-xs font-semibold hover:bg-white/20 active:scale-95 disabled:opacity-40 transition-all"
              title="Rewind 10 seconds (← or J)"
              aria-label="Rewind 10 seconds"
            >
              <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M1 4v6h6M3.51 15a9 9 0 1 0 2.13-9.36L1 10" />
              </svg>
              <span className="hidden sm:inline">-10s</span>
            </button>

            {/* Forward +10s Button */}
            <button
              type="button"
              onClick={() => handleSeek(10)}
              disabled={status !== "ready"}
              className="flex items-center gap-1 rounded-lg bg-white/10 px-2.5 py-1.5 text-xs font-semibold hover:bg-white/20 active:scale-95 disabled:opacity-40 transition-all"
              title="Forward 10 seconds (→ or L)"
              aria-label="Forward 10 seconds"
            >
              <span className="hidden sm:inline">+10s</span>
              <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                <path d="M23 4v6h-6M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
              </svg>
            </button>

            {/* Volume / Mute */}
            <div className="flex items-center gap-1 group/vol ml-1">
              <button
                type="button"
                onClick={toggleMute}
                className="flex h-8 w-8 items-center justify-center rounded-lg hover:bg-white/10 transition-colors"
                title={isMuted ? "Unmute (M)" : "Mute (M)"}
                aria-label="Mute toggle"
              >
                {isMuted || volume === 0 ? (
                  <svg className="w-4 h-4 text-rose-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                    <path strokeLinecap="round" strokeLinejoin="round" d="M17 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4 text-white/90" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
                  </svg>
                )}
              </button>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={isMuted ? 0 : volume}
                onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
                className="hidden sm:inline-block w-14 h-1 accent-sky-400 cursor-pointer bg-white/20 rounded"
                title="Volume"
              />
            </div>

            {/* Time Stamp Display */}
            <span className="font-mono text-xs text-white/80 ml-1">
              {formatTime(currentTime)} <span className="text-white/40">/</span> {formatTime(duration)}
            </span>
          </div>

          {/* Right: Speed, Captions, Transcript Drawer, Fullscreen, Language */}
          <div className="flex items-center gap-1.5 sm:gap-2">
            {/* Speed Toggle */}
            <button
              type="button"
              onClick={cycleSpeed}
              className="rounded-md bg-white/10 px-2 py-1 text-xs font-mono font-semibold text-sky-300 hover:bg-white/20 transition-colors"
              title="Playback speed"
            >
              {playbackRate}x
            </button>

            {/* Captions Toggle */}
            <button
              type="button"
              onClick={() => setShowCaptions((s) => !s)}
              className={cn(
                "flex items-center gap-1 rounded-md px-2 py-1 text-xs font-semibold transition-all active:scale-95",
                showCaptions
                  ? "bg-sky-500/20 text-sky-300 border border-sky-500/40"
                  : "bg-white/5 text-white/50 hover:bg-white/10"
              )}
              title="Toggle captions"
              aria-label="Toggle captions"
            >
              <span>CC</span>
            </button>

            {/* Transcript Drawer Toggle */}
            <button
              type="button"
              onClick={() => setTranscriptOpen((o) => !o)}
              className={cn(
                "flex items-center gap-1 rounded-md px-2.5 py-1 text-xs font-medium transition-all active:scale-95",
                transcriptOpen
                  ? "bg-white/20 text-white font-semibold"
                  : "bg-white/5 text-white/60 hover:bg-white/10 hover:text-white"
              )}
              title="Toggle synchronized transcript"
            >
              <span>📝</span>
              <span className="hidden sm:inline">Transcript</span>
            </button>

            {/* Language Selector */}
            <select
              value={language}
              onChange={(e) => onLanguageChange(e.target.value)}
              className="rounded-md border border-white/15 bg-white/10 px-2 py-1 text-xs font-medium text-white focus:outline-none"
            >
              <option value="en" className="bg-[#121620] text-white">EN</option>
              <option value="hi" className="bg-[#121620] text-white">हिन्दी</option>
              <option value="hi-Latn" className="bg-[#121620] text-white">Hinglish</option>
              <option value="ta" className="bg-[#121620] text-white">தமிழ்</option>
              <option value="te" className="bg-[#121620] text-white">తెలుగు</option>
            </select>

            {/* Fullscreen Button */}
            <button
              type="button"
              onClick={toggleFullscreen}
              className="flex h-8 w-8 items-center justify-center rounded-lg hover:bg-white/10 transition-colors"
              title="Fullscreen (F)"
              aria-label="Toggle fullscreen"
            >
              <svg className="w-4 h-4 text-white/80" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth="2">
                <path strokeLinecap="round" strokeLinejoin="round" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Synchronized Scrolling Transcript (Expandable Drawer) */}
      {transcriptOpen && narrationScript && status === "ready" && (
        <div
          ref={transcriptRef}
          className="mt-3 max-h-36 overflow-y-auto rounded-lg bg-black/40 p-3.5 scrollbar-thin border border-white/10 text-xs leading-relaxed"
        >
          <div className="flex items-center justify-between mb-2 pb-1 border-b border-white/10">
            <p className="text-[11px] font-bold text-white/60 uppercase tracking-wider">
              Synchronized Narration
            </p>
            <span className="text-[10px] text-white/40">
              Click any sentence to seek video
            </span>
          </div>
          {sentences.map((sentence, idx) => (
            <span
              key={idx}
              data-sentence={idx}
              className={cn(
                "inline transition-colors duration-200 cursor-pointer hover:underline mr-1",
                idx === activeSentenceIdx
                  ? "text-sky-300 font-semibold bg-sky-500/20 rounded px-1"
                  : idx < activeSentenceIdx
                    ? "text-white/40"
                    : "text-white/70"
              )}
              onClick={() => {
                const vid = videoRef.current;
                if (vid && duration > 0) {
                  const targetTime = (idx / sentences.length) * duration;
                  vid.currentTime = targetTime;
                  setCurrentTime(targetTime);
                }
              }}
            >
              {sentence}{" "}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
