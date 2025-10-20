# Usage Guide

This guide explains how to use the FDTD PEC Cavity simulator.

---

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/mmaharebi/fdtd-pec-cavity.git
cd fdtd-pec-cavity

# Install dependencies
pip install -r requirements.txt
```

**Requirements:**
- Python 3.8+
- NumPy 1.21+
- Matplotlib 3.4+

---

### 2. Run the Simulation

```bash
python src/main.py
```

This will:
1. Run the FDTD simulation (~2 seconds)
2. Compute frequency spectrum via FFT
3. Compare with analytical resonance frequencies
4. Display validation plots

**Expected output:**
- Console messages showing simulation progress
- Matplotlib window with frequency spectrum plot
- Validation results printed to terminal

---

## Understanding the Output

### Console Output

```
Running FDTD simulation...
  Grid: 121 x 81 cells (dx=dy=2.5 mm)
  Time steps: 4500 (dt=4.8 ps)
  Total time: ~21 ns
  
Computing spectrum...
  Frequency resolution: 46 MHz
  
Analytical modes (TM_z):
  Mode (1,1): 832.05 MHz
  Mode (2,1): 1249.14 MHz
  Mode (4,1): 2498.28 MHz
  ...
  
Validation:
  Mode (1,1): Error = 0.52%
  Mode (2,1): Error = 0.39%
  Mean error: 0.43%
```

### Plots

**Frequency Spectrum:**
- X-axis: Frequency (MHz)
- Y-axis: Normalized amplitude
- Vertical dashed lines: Analytical resonances
- Peaks: Simulated resonances

**Validation Summary:**
- (a) Frequency spectrum with mode labels
- (b) Simulated vs. analytical comparison
- (c) Spatial field distribution
- (d) Error analysis

---

## Customizing the Simulation

### Basic Configuration

Edit `src/config.py` to modify parameters:

```python
@dataclass
class CavityConfig:
    # Cavity dimensions
    Lx: float = 0.30        # Width [m] (default: 30 cm)
    Ly: float = 0.20        # Height [m] (default: 20 cm)
    
    # Grid resolution
    Nx: int = 121           # Grid points in x
    Ny: int = 81            # Grid points in y
    
    # Time stepping
    Nt: int = 4500          # Total time steps
    CFL: float = 0.99       # Stability factor (max: 1.0)
    
    # Source parameters
    J0: float = 1000.0      # Current amplitude [A/m²]
    t0_factor: float = 50.0 # Pulse delay
    tau_factor: float = 15.0 # Pulse width
```

### Common Modifications

**Change cavity size:**
```python
Lx: float = 0.40  # 40 cm wide cavity
Ly: float = 0.25  # 25 cm tall cavity
```

**Higher resolution (slower, more accurate):**
```python
Nx: int = 241     # 2× finer grid
Ny: int = 161
```

**Longer simulation (better frequency resolution):**
```python
Nt: int = 9000    # 2× longer simulation
```

**Different source location:**
```python
isrc: int = 60    # x-position (default: Nx//3)
jsrc: int = 40    # y-position (default: Ny//2)
```

---

## Generating Animations

### Interactive Animation

```bash
# Run main.py with animation enabled (default)
python src/main.py
```

An interactive Matplotlib animation will display showing wave propagation in real-time.

### Save Animation Frames

```bash
# Generate 200 frames saved to animation/ directory
python src/save_animation_frames.py
```

This will:
1. Run simulation in two passes
   - Pass 1: Find maximum field amplitude
   - Pass 2: Generate frames with fixed color scale
2. Save 200 PNG frames to `animation/` directory
3. Report maximum field strength and color scale used

**Output:**
- `animation/frame_0000.png` through `frame_0199.png`
- Each frame: 770×590 pixels at 100 DPI

### Convert to Video

**MP4 (recommended):**
```bash
ffmpeg -framerate 10 -i animation/frame_%04d.png \
  -vf "scale=770:590,pad=ceil(iw/2)*2:ceil(ih/2)*2" \
  -c:v libx264 -pix_fmt yuv420p -crf 18 \
  cavity_animation.mp4
```

**GIF:**
```bash
ffmpeg -i cavity_animation.mp4 \
  -vf "fps=6,scale=500:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=64[p];[s1][p]paletteuse" \
  cavity_animation.gif
```

---

## Understanding the Physics

### What You're Seeing

The simulation shows electromagnetic waves in a metal cavity:

1. **Initial pulse (0-5 ns):** Gaussian current creates E<sub>z</sub> field
2. **Propagation (5-15 ns):** Circular wave expands at speed of light
3. **Reflections (15-25 ns):** Waves bounce off PEC walls
4. **Interference (25-35 ns):** Standing wave patterns form
5. **Resonance (35-45 ns):** Cavity modes build up

### Resonant Frequencies

The cavity supports resonant frequencies given by:

$$f_{mn} = \frac{c}{2}\sqrt{\left(\frac{m}{L_x}\right)^2 + \left(\frac{n}{L_y}\right)^2}$$

where:
- c = 3×10⁸ m/s (speed of light)
- m, n = 1, 2, 3, ... (mode indices)
- L<sub>x</sub>, L<sub>y</sub> = cavity dimensions

**For 30×20 cm cavity:**
- (1,1) mode: 832 MHz
- (2,1) mode: 1249 MHz
- (4,1) mode: 2498 MHz
- etc.

### Why Some Modes Are Missing

The source at (x,y) = (L<sub>x</sub>/3, L<sub>y</sub>/2) doesn't excite modes where:
- m = 3k (multiples of 3) → source on nodal line in x
- n = 2k (even) → source on nodal line in y

This is **correct physics** — you can't excite a mode if the source is at a node.

---

## Troubleshooting

### Simulation doesn't run

**Problem:** Import errors
```
ModuleNotFoundError: No module named 'numpy'
```

**Solution:**
```bash
pip install numpy matplotlib
```

---

**Problem:** Simulation is unstable (fields blow up)

**Solution:** Reduce CFL factor in `config.py`:
```python
CFL: float = 0.95  # More conservative (slower)
```

---

### No animation appears

**Problem:** Matplotlib backend issues

**Solution:** Try different backend:
```python
# Add to top of main.py
import matplotlib
matplotlib.use('TkAgg')  # or 'Qt5Agg'
import matplotlib.pyplot as plt
```

---

### Animation generation fails

**Problem:** FFmpeg not installed

**Solution:**
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from ffmpeg.org
```

---

## Performance Notes

### Computation Time

| Configuration | Time Steps | Grid Size | Time |
|--------------|-----------|-----------|------|
| Default | 4500 | 121×81 | ~2 sec |
| High-res | 4500 | 241×161 | ~8 sec |
| Long run | 9000 | 121×81 | ~4 sec |
| Both | 9000 | 241×161 | ~16 sec |

*On typical laptop (Intel i5/i7)*

### Memory Usage

- Simulation: ~50 MB
- Animation (200 frames): ~200 MB
- Full data storage: ~500 MB (if saving all timesteps)

---

## Advanced Usage

### Custom Source Functions

Edit `src/fdtd_core.py`, modify `soft_current()`:

```python
def soft_current(t, dt, t0_factor, tau_factor, J0):
    """Customize this for different excitations"""
    # Gaussian pulse (default)
    t0 = t0_factor * dt
    tau = tau_factor * dt
    return J0 * np.exp(-((t - t0)**2) / (2 * tau**2))
    
    # Alternative: Sine wave
    # f0 = 1e9  # 1 GHz
    # return J0 * np.sin(2 * np.pi * f0 * t)
```

### Multiple Probes

Edit `src/config.py`:

```python
# Add specific probe locations [(i1,j1), (i2,j2), ...]
probes: list = [(30, 40), (60, 40), (90, 40)]
```

### Export Field Data

```python
# In main.py, save simulation results
Ez, trace, meta = run_fdtd(cfg)
np.savez('results.npz', Ez=Ez, trace=trace, **meta)
```

---

## File Descriptions

### Source Code

- **main.py** — Entry point, orchestrates simulation
- **fdtd_core.py** — Core FDTD algorithm (time-stepping)
- **config.py** — Simulation parameters (edit this)
- **constants.py** — Physical constants (c, ε₀, μ₀)
- **modes.py** — Analytical resonance calculations
- **spectrum.py** — FFT spectral analysis
- **animate.py** — Interactive animation display
- **save_animation_frames.py** — Export frames for video

### Documentation

- **THEORY.md** — Maxwell's equations, FDTD method, discretization
- **VALIDATION.md** — Detailed validation, error analysis, convergence

---

## Further Reading

### FDTD Method
- Yee, K. S. (1966). "Numerical solution of Maxwell's equations." *IEEE Trans. Antennas Propag.*
- Taflove & Hagness (2005). *Computational Electrodynamics: The FDTD Method*

### Cavity Resonators
- Pozar, D. M. (2011). *Microwave Engineering*, Chapter on cavity resonators
- Jackson, J. D. (1998). *Classical Electrodynamics*, Waveguides and cavities

### Applications
- Microwave filters and resonators
- Particle accelerator RF cavities
- Antenna design and analysis
- Electromagnetic compatibility (EMC)

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on:
- Reporting bugs
- Suggesting enhancements
- Submitting pull requests

---

## Questions?

- **Issues:** [Open an issue](https://github.com/mmaharebi/fdtd-pec-cavity/issues)
- **Discussions:** [Start a discussion](https://github.com/mmaharebi/fdtd-pec-cavity/discussions)
- **Email:** mmaharebi@gmail.com

---

**Happy simulating! 🚀**
