# FFT-based spectroscopy utilities
import numpy as np

def averaged_spectrum(trace: np.ndarray, dt: float, cut_fraction: float = 0.15):
    """
    trace: shape (P, Nt)
    returns freqs, Savg (both 1-D, rFFT)
    """
    Nt = trace.shape[1]
    cut_n = int(cut_fraction * Nt)
    sig = trace[:, cut_n:]
    # Hann window per probe
    w = np.hanning(sig.shape[1])
    sig_w = sig * w[np.newaxis, :]
    Spec = np.fft.rfft(sig_w, axis=1)
    freqs = np.fft.rfftfreq(sig_w.shape[1], d=dt)
    Savg = np.mean(np.abs(Spec), axis=0)
    # Normalize for plotting
    if np.max(Savg) > 0:
        Savg = Savg / np.max(Savg)
    return freqs, Savg
