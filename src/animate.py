# Lightweight re-run for field animation (avoids storing full 3D data)
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from config import CavityConfig
from fdtd_core import make_grid, allocate_fields, step_fields, soft_current

def animate_cavity(cfg: CavityConfig, frames: int = 300, substeps: int = 4):
    dx, dy, dt, isrc, jsrc, _ = make_grid(cfg)
    Ez, Hx, Hy = allocate_fields(cfg.Nx, cfg.Ny)

    fig, ax = plt.subplots(figsize=(6, 4.5))
    im = ax.imshow(Ez.T, extent=[0, cfg.Lx, 0, cfg.Ly], origin='lower',
                   vmin=-1e-6, vmax=1e-6, interpolation='nearest', aspect='auto')
    ax.set_title("$E_z(x,y,t)$ in a PEC cavity")
    ax.set_xlabel("x [m]"); ax.set_ylabel("y [m]")

    def update(frame):
        for k in range(substeps):
            n = frame * substeps + k
            t_half = (n + 0.5) * dt
            Jz_half = soft_current(t_half, dt, cfg.t0_factor, cfg.tau_factor, cfg.J0)
            step_fields(Ez, Hx, Hy, dx, dy, dt, isrc, jsrc, Jz_half)
        im.set_data(Ez.T)
        vmax = max(1e-9, np.max(np.abs(Ez)))
        im.set_clim(-0.5 * vmax, 0.5 * vmax)
        return (im,)

    ani = FuncAnimation(fig, update, frames=frames, blit=False, interval=20)
    plt.tight_layout()
    plt.show()
