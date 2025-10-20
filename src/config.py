# Simulation configuration (edit here)
from dataclasses import dataclass

@dataclass
class CavityConfig:
    # Geometry
    Lx: float = 0.30        # [m]
    Ly: float = 0.20        # [m]
    Nx: int = 121           # Ez nodes in x
    Ny: int = 81            # Ez nodes in y

    # Time stepping
    CFL: float = 0.99       # safety factor
    Nt: int = 4500          # total steps

    # Source (soft current at one cell)
    isrc: int | None = None        # will default to Nx//3 at runtime if None
    jsrc: int | None = None        # will default to Ny//2 at runtime if None
    t0_factor: float = 50.0 # t0 = t0_factor * dt
    tau_factor: float = 15.0# tau = tau_factor * dt
    J0: float = 1000.0      # amplitude (1000× stronger for clear visualization)

    # Probes (None -> auto-placed)
    probes: list | None = None

    # Spectrum
    cut_fraction: float = 0.15  # drop early transient before FFT
