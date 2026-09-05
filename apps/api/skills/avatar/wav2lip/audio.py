"""
Shikshak AI — Wav2Lip Audio Processor.

Computes 80-channel mel-spectrograms at 16kHz matching the exact
hyperparameters required by Wav2Lip checkpoint weights.
"""
from __future__ import annotations

import librosa
import numpy as np
from scipy import signal

SAMPLE_RATE = 16000
N_FFT = 800
HOP_SIZE = 200
WIN_SIZE = 800
NUM_MELS = 80
FMIN = 55
FMAX = 7600
REF_LEVEL_DB = 20
MIN_LEVEL_DB = -100
MAX_ABS_VALUE = 4.0
PREEMPHASIS = 0.97
SYMMETRIC_MELS = True


def preemphasis(wav: np.ndarray, k: float = PREEMPHASIS) -> np.ndarray:
    return signal.lfilter([1, -k], [1], wav)


def _build_mel_basis() -> np.ndarray:
    return librosa.filters.mel(
        sr=SAMPLE_RATE,
        n_fft=N_FFT,
        n_mels=NUM_MELS,
        fmin=FMIN,
        fmax=FMAX,
    )


_MEL_BASIS = None


def _get_mel_basis() -> np.ndarray:
    global _MEL_BASIS
    if _MEL_BASIS is None:
        _MEL_BASIS = _build_mel_basis()
    return _MEL_BASIS


def _amp_to_db(x: np.ndarray) -> np.ndarray:
    min_level = np.exp(MIN_LEVEL_DB / 20 * np.log(10))
    return 20 * np.log10(np.maximum(min_level, x))


def _normalize(s: np.ndarray) -> np.ndarray:
    if SYMMETRIC_MELS:
        return np.clip(
            (2 * MAX_ABS_VALUE) * ((s - MIN_LEVEL_DB) / (-MIN_LEVEL_DB)) - MAX_ABS_VALUE,
            -MAX_ABS_VALUE,
            MAX_ABS_VALUE,
        )
    return np.clip(MAX_ABS_VALUE * ((s - MIN_LEVEL_DB) / (-MIN_LEVEL_DB)), 0, MAX_ABS_VALUE)


def compute_melspectrogram(wav: np.ndarray) -> np.ndarray:
    """Compute normalized 80-channel mel spectrogram from audio array at 16kHz."""
    preemph_wav = preemphasis(wav, PREEMPHASIS)
    stft = librosa.stft(
        y=preemph_wav,
        n_fft=N_FFT,
        hop_length=HOP_SIZE,
        win_length=WIN_SIZE,
    )
    linear = np.abs(stft)
    mel_basis = _get_mel_basis()
    mel = np.dot(mel_basis, linear)
    mel_db = _amp_to_db(mel) - REF_LEVEL_DB
    return _normalize(mel_db)


def get_mel_chunks_for_frames(
    audio_path: str,
    fps: int = 25,
    mel_step_size: int = 16,
) -> tuple[list[np.ndarray], int]:
    """Load audio, resample to 16kHz, and extract 16-frame mel windows for each video frame."""
    wav, _ = librosa.load(audio_path, sr=SAMPLE_RATE)
    # Rescale to standard level
    max_val = np.max(np.abs(wav))
    if max_val > 0:
        wav = (wav / max_val) * 0.9

    orig_mel = compute_melspectrogram(wav)

    # Mel frames per second = SAMPLE_RATE / HOP_SIZE = 16000 / 200 = 80 mel frames/sec
    # Video fps = 25 => mel frames per video frame = 80 / 25 = 3.2
    # For frame i, mel chunk is centered at i * 3.2 with width 16
    mel_fps = SAMPLE_RATE / HOP_SIZE  # 80.0
    total_video_frames = max(1, int(np.ceil(len(wav) / SAMPLE_RATE * fps)))

    mel_chunks: list[np.ndarray] = []
    for i in range(total_video_frames):
        start_mel = int(i * (mel_fps / fps))
        end_mel = start_mel + mel_step_size

        if end_mel > orig_mel.shape[1]:
            # Pad on the right with minimum value
            pad_width = end_mel - orig_mel.shape[1]
            chunk = np.pad(
                orig_mel[:, start_mel:],
                ((0, 0), (0, pad_width)),
                mode="constant",
                constant_values=-MAX_ABS_VALUE if SYMMETRIC_MELS else 0,
            )
        else:
            chunk = orig_mel[:, start_mel:end_mel]

        mel_chunks.append(chunk)

    return mel_chunks, total_video_frames
