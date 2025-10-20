# Orchestrates: run FDTD, compute spectrum, overlay analytic modes, optional animation
import matplotlib.pyplot as plt
from config import CavityConfig
from fdtd_core import run_fdtd
from spectrum import averaged_spectrum
from modes import analytic_modes

def main(do_animation: bool = True):
    cfg = CavityConfig()
    Ez, trace, meta = run_fdtd(cfg)
    freqs, Savg = averaged_spectrum(trace, meta["dt"], cfg.cut_fraction)

    # Analytical mode markers
    fmax = freqs[-1]
    f_ana, mn = analytic_modes(meta["Lx"], meta["Ly"], fmax)

    # --- Plot spectrum
    plt.figure(figsize=(10, 4))
    plt.plot(freqs / 1e6, Savg, lw=1.3, label="Averaged |FFT| of probes")
    for f in f_ana:
        plt.axvline(f / 1e6, ymin=0, ymax=0.15, linewidth=0.6, linestyle='--', alpha=0.35)
    for k in range(min(8, len(f_ana))):
        plt.text((f_ana[k] / 1e6), 0.17, f"({mn[k][0]},{mn[k][1]})",
                 rotation=90, va='bottom', ha='center', fontsize=8)
    plt.title("2-D TM$_z$ PEC cavity: spectrum vs analytical resonances")
    plt.xlabel("Frequency [MHz]"); plt.ylabel("Normalized magnitude")
    plt.legend(loc="upper right")
    plt.tight_layout()
    plt.show()

    # --- Optional quick animation (re-runs a short pass)
    if do_animation:
        from animate import animate_cavity
        animate_cavity(cfg, frames=300, substeps=4)

if __name__ == "__main__":
    main(do_animation=True)
