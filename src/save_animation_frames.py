#!/usr/bin/env python3
"""
Save animation frames to disk for ffmpeg conversion
"""
import numpy as np
import matplotlib.pyplot as plt
import os
from config import CavityConfig
from fdtd_core import make_grid, allocate_fields, step_fields, soft_current

def save_animation_frames(cfg: CavityConfig, frames: int = 300, substeps: int = 10):
    """
    Save animation frames showing Ez field evolution.
    
    Args:
        cfg: Configuration
        frames: Number of frames to save
        substeps: Time steps between frames
    """
    # Create output directory
    os.makedirs("animation", exist_ok=True)
    
    print(f"Generating {frames} frames with {substeps} substeps each...")
    print(f"J0 = {cfg.J0} A/m²")
    
    # Initialize simulation
    dx, dy, dt, isrc, jsrc, _ = make_grid(cfg)
    Ez, Hx, Hy = allocate_fields(cfg.Nx, cfg.Ny)
    
    # First pass: find maximum field amplitude for fixed color scale
    print("Pass 1: Scanning for maximum field amplitude...")
    Ez_temp = Ez.copy()
    Hx_temp = Hx.copy()
    Hy_temp = Hy.copy()
    
    max_Ez = 0.0
    for frame in range(frames):
        for k in range(substeps):
            n = frame * substeps + k
            t_half = (n + 0.5) * dt
            Jz_half = soft_current(t_half, dt, cfg.t0_factor, cfg.tau_factor, cfg.J0)
            step_fields(Ez_temp, Hx_temp, Hy_temp, dx, dy, dt, isrc, jsrc, Jz_half)
        max_Ez = max(max_Ez, np.max(np.abs(Ez_temp)))
    
    print(f"Maximum |Ez| found: {max_Ez:.3e} V/m")
    
    # Set fixed color scale
    vmax = max_Ez * 1.1  # 10% margin
    vmin = -vmax
    
    # Second pass: generate and save frames
    print(f"Pass 2: Generating frames with fixed scale [{vmin:.3e}, {vmax:.3e}] V/m...")
    
    # Reset simulation
    Ez, Hx, Hy = allocate_fields(cfg.Nx, cfg.Ny)
    
    # Create x, y coordinates
    x = np.linspace(0, cfg.Lx, cfg.Nx)
    y = np.linspace(0, cfg.Ly, cfg.Ny)
    
    for frame in range(frames):
        # Advance simulation
        for k in range(substeps):
            n = frame * substeps + k
            t_half = (n + 0.5) * dt
            Jz_half = soft_current(t_half, dt, cfg.t0_factor, cfg.tau_factor, cfg.J0)
            step_fields(Ez, Hx, Hy, dx, dy, dt, isrc, jsrc, Jz_half)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 6), dpi=100)  # Changed to 6 for even dimensions
        
        # Plot Ez field
        im = ax.imshow(Ez.T, 
                      extent=[0, cfg.Lx, 0, cfg.Ly],
                      origin='lower',
                      vmin=vmin, 
                      vmax=vmax,
                      cmap='RdBu_r',
                      interpolation='bilinear',
                      aspect='auto')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax, label='$E_z$ [V/m]')
        
        # Labels and title
        time_ns = (frame * substeps * dt) * 1e9
        ax.set_xlabel('x [m]', fontsize=12)
        ax.set_ylabel('y [m]', fontsize=12)
        ax.set_title(f'$E_z(x,y,t)$ in PEC Cavity (t = {time_ns:.2f} ns)', fontsize=13)
        
        # Fixed axis limits
        ax.set_xlim(0, cfg.Lx)
        ax.set_ylim(0, cfg.Ly)
        
        # Mark source location
        x_src = x[isrc]
        y_src = y[jsrc]
        ax.plot(x_src, y_src, 'k*', markersize=8, label='Source')
        ax.legend(loc='upper right', fontsize=9)
        
        plt.tight_layout()
        
        # Save frame
        filename = f"animation/frame_{frame:04d}.png"
        plt.savefig(filename, dpi=100, bbox_inches='tight')
        plt.close(fig)
        
        if (frame + 1) % 20 == 0:
            print(f"  Saved frame {frame + 1}/{frames}")
    
    print(f"\n✅ Successfully saved {frames} frames to animation/")
    print(f"   Maximum |Ez| = {max_Ez:.3e} V/m")
    print(f"   Color scale: [{vmin:.3e}, {vmax:.3e}] V/m")
    print(f"\nNext steps:")
    print(f"  1. Convert to MP4: ffmpeg -framerate 20 -i animation/frame_%04d.png -c:v libx264 -pix_fmt yuv420p -crf 18 Ez_animation.mp4")
    print(f"  2. Convert to GIF: ffmpeg -i Ez_animation.mp4 -vf 'fps=10,scale=640:-1:flags=lanczos' Ez_animation.gif")

if __name__ == "__main__":
    cfg = CavityConfig()
    save_animation_frames(cfg, frames=300, substeps=10)
