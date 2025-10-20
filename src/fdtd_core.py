# Core FDTD: grid setup and time stepping for 2-D TMz cavity (PEC walls)
import numpy as np
from constants import eps0, mu0, c0
from config import CavityConfig

def make_grid(cfg: CavityConfig):
    dx = cfg.Lx / (cfg.Nx - 1)
    dy = cfg.Ly / (cfg.Ny - 1)
    dt = cfg.CFL / (c0 * np.sqrt((1.0 / dx**2) + (1.0 / dy**2)))
    # default source location if not provided
    isrc = cfg.isrc if cfg.isrc is not None else cfg.Nx // 3
    jsrc = cfg.jsrc if cfg.jsrc is not None else cfg.Ny // 2
    # default probes if not provided
    if not cfg.probes:
        probes = [(cfg.Nx // 4, cfg.Ny // 3),
                  (cfg.Nx // 2 + 7, cfg.Ny // 2 - 5),
                  (3 * cfg.Nx // 4 - 5, 2 * cfg.Ny // 3)]
    else:
        probes = cfg.probes
    return dx, dy, dt, isrc, jsrc, probes

def allocate_fields(Nx: int, Ny: int):
    Ez = np.zeros((Nx, Ny), dtype=np.float64)
    Hx = np.zeros((Nx, Ny - 1), dtype=np.float64)   # half-cell in y
    Hy = np.zeros((Nx - 1, Ny), dtype=np.float64)   # half-cell in x
    return Ez, Hx, Hy

def soft_current(t_half: float, dt: float, t0_factor: float,
                 tau_factor: float, J0: float) -> float:
    t0 = t0_factor * dt
    tau = tau_factor * dt
    return J0 * np.exp(-((t_half - t0) / tau) ** 2)

def step_fields(Ez: np.ndarray, Hx: np.ndarray, Hy: np.ndarray,
                dx: float, dy: float, dt: float,
                isrc: int, jsrc: int, Jz_half: float):
    # Update Hx (uses dEz/dy)
    Hx[:, :] -= (dt / mu0) * (Ez[:, 1:] - Ez[:, :-1]) / dy
    # Update Hy (uses dEz/dx)
    Hy[:, :] += (dt / mu0) * (Ez[1:, :] - Ez[:-1, :]) / dx
    # Update Ez (uses curl H)
    # For interior Ez[i,j], we need Hy[i,j] - Hy[i-1,j] and Hx[i,j] - Hx[i,j-1]
    # Hy has shape (Nx-1, Ny), Hx has shape (Nx, Ny-1)
    # For Ez[1:-1, 1:-1] (interior), we need:
    #   Hy differences: Hy[1:, 1:-1] - Hy[:-1, 1:-1] (shape: Nx-2, Ny-2)
    #   Hx differences: Hx[1:-1, 1:] - Hx[1:-1, :-1] (shape: Nx-2, Ny-2)
    curl_H = ((Hy[1:, 1:-1] - Hy[:-1, 1:-1]) / dx) - ((Hx[1:-1, 1:] - Hx[1:-1, :-1]) / dy)
    Ez[1:-1, 1:-1] += (dt / eps0) * curl_H
    # Inject soft current at interior cell
    if 1 <= isrc <= Ez.shape[0] - 2 and 1 <= jsrc <= Ez.shape[1] - 2:
        Ez[isrc, jsrc] -= (dt / eps0) * Jz_half
    # PEC walls (tangential Ez = 0)
    Ez[0, :] = 0.0; Ez[-1, :] = 0.0; Ez[:, 0] = 0.0; Ez[:, -1] = 0.0

def run_fdtd(cfg: CavityConfig):
    Nx, Ny = cfg.Nx, cfg.Ny
    dx, dy, dt, isrc, jsrc, probes = make_grid(cfg)
    Ez, Hx, Hy = allocate_fields(Nx, Ny)
    trace = np.zeros((len(probes), cfg.Nt), dtype=np.float64)

    for n in range(cfg.Nt):
        t_half = (n + 0.5) * dt
        Jz_half = soft_current(t_half, dt, cfg.t0_factor, cfg.tau_factor, cfg.J0)
        step_fields(Ez, Hx, Hy, dx, dy, dt, isrc, jsrc, Jz_half)
        for p, (ip, jp) in enumerate(probes):
            trace[p, n] = Ez[ip, jp]

    meta = {
        "dx": dx, "dy": dy, "dt": dt,
        "isrc": isrc, "jsrc": jsrc, "probes": probes,
        "Lx": cfg.Lx, "Ly": cfg.Ly, "Nx": Nx, "Ny": Ny
    }
    return Ez, trace, meta
