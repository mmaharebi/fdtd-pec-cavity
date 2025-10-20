# Theoretical Background

## Maxwell's Equations in 2D

For the transverse magnetic (TM<sub>z</sub>) mode in a 2D cavity, the electromagnetic fields have the following components:

- **Electric field:** E<sub>z</sub>(x, y, t) (only z-component)
- **Magnetic field:** H<sub>x</sub>(x, y, t), H<sub>y</sub>(x, y, t) (only transverse components)

### Governing Equations

The time-domain Maxwell's equations for TM<sub>z</sub> mode are:

$$\frac{\partial H_x}{\partial t} = -\frac{1}{\mu_0} \frac{\partial E_z}{\partial y}$$

$$\frac{\partial H_y}{\partial t} = \frac{1}{\mu_0} \frac{\partial E_z}{\partial x}$$

$$\frac{\partial E_z}{\partial t} = \frac{1}{\epsilon_0} \left( \frac{\partial H_y}{\partial x} - \frac{\partial H_x}{\partial y} \right) + \frac{J_z}{\epsilon_0}$$

where:
- ε₀ = 8.854×10⁻¹² F/m (permittivity of free space)
- μ₀ = 4π×10⁻⁷ H/m (permeability of free space)
- J<sub>z</sub> = source current density

---

## Analytical Solution for PEC Cavity

### Resonant Modes

For a rectangular PEC cavity with dimensions L<sub>x</sub> × L<sub>y</sub>, the resonant frequencies are:

$$f_{mn} = \frac{c}{2}\sqrt{\left(\frac{m}{L_x}\right)^2 + \left(\frac{n}{L_y}\right)^2}$$

where:
- c = 299,792,458 m/s (speed of light)
- m, n = 1, 2, 3, ... (mode indices)

### Field Patterns

The spatial distribution of E<sub>z</sub> for mode (m,n) is:

$$E_z(x,y) = E_0 \sin\left(\frac{m\pi x}{L_x}\right) \sin\left(\frac{n\pi y}{L_y}\right)$$

This satisfies the boundary condition E<sub>z</sub> = 0 at all four walls (x=0, x=L<sub>x</sub>, y=0, y=L<sub>y</sub>).

---

## FDTD Discretization

### Yee Lattice

The FDTD method uses a staggered grid (Yee lattice) where:
- E<sub>z</sub> is sampled at cell centers: (i, j)
- H<sub>x</sub> is sampled at horizontal edges: (i, j+½)
- H<sub>y</sub> is sampled at vertical edges: (i+½, j)

### Leapfrog Time-Stepping

Fields are updated at alternating half time steps:

**H-field update** (from n to n+½):
$$H_x^{n+1/2}(i,j+\tfrac{1}{2}) = H_x^{n-1/2}(i,j+\tfrac{1}{2}) - \frac{\Delta t}{\mu_0 \Delta y} \left[ E_z^n(i,j+1) - E_z^n(i,j) \right]$$

$$H_y^{n+1/2}(i+\tfrac{1}{2},j) = H_y^{n-1/2}(i+\tfrac{1}{2},j) + \frac{\Delta t}{\mu_0 \Delta x} \left[ E_z^n(i+1,j) - E_z^n(i,j) \right]$$

**E-field update** (from n to n+1):
$$E_z^{n+1}(i,j) = E_z^n(i,j) + \frac{\Delta t}{\epsilon_0} \left[ \frac{H_y^{n+1/2}(i+\tfrac{1}{2},j) - H_y^{n+1/2}(i-\tfrac{1}{2},j)}{\Delta x} - \frac{H_x^{n+1/2}(i,j+\tfrac{1}{2}) - H_x^{n+1/2}(i,j-\tfrac{1}{2})}{\Delta y} \right] + \frac{\Delta t J_z^{n+1/2}(i,j)}{\epsilon_0}$$

---

## Stability Condition (CFL)

The FDTD algorithm is stable if the time step satisfies the Courant-Friedrichs-Lewy (CFL) condition:

$$\Delta t \leq \frac{1}{c \sqrt{\frac{1}{\Delta x^2} + \frac{1}{\Delta y^2}}}$$

For safety, we use:
$$\Delta t = 0.99 \times \frac{1}{c \sqrt{\frac{1}{\Delta x^2} + \frac{1}{\Delta y^2}}}$$

---

## Gaussian Pulse Excitation

The source current is a Gaussian pulse in time:

$$J_z(t) = J_0 \exp\left(-\frac{(t - t_0)^2}{2\tau^2}\right)$$

where:
- J₀ = amplitude (1000 A/m²)
- t₀ = time delay (50 Δt ≈ 0.24 ns)
- τ = pulse width (15 Δt ≈ 72 ps)

This pulse has a broad frequency spectrum, exciting multiple cavity modes simultaneously.

---

## Spectral Analysis

The frequency spectrum is computed via FFT of the time-domain E<sub>z</sub> signal at probe locations:

1. **Windowing:** Apply Hanning window to reduce spectral leakage
2. **FFT:** Compute Fast Fourier Transform
3. **Averaging:** Average spectra from multiple probe locations
4. **Peak detection:** Identify resonance frequencies

The FFT frequency resolution is:
$$\Delta f = \frac{1}{T_{total}} = \frac{1}{N_t \Delta t}$$

For our simulation: Δf ≈ 46 MHz

---

## Boundary Conditions

### Perfect Electric Conductor (PEC)

At the cavity walls, we enforce:
$$E_z = 0$$

This is implemented by:
- Setting E<sub>z</sub> = 0 at boundary grid points
- Not updating E<sub>z</sub> at boundaries (remains zero)

The tangential electric field must vanish at a perfect conductor, which for TM<sub>z</sub> mode means E<sub>z</sub> = 0 at all walls.

---

## Numerical Dispersion

The finite-difference approximation introduces numerical dispersion. The numerical phase velocity differs slightly from the physical speed of light:

$$v_p(\omega, \theta) \neq c$$

This causes small errors in resonance frequencies, typically:
- Grid dispersion: ~0.1-0.3%
- Time-stepping error: ~0.1%
- Boundary staircase: <0.1% (rectangular cavity)

Total numerical error: <0.5% for our resolution (10+ cells per wavelength)

---

## References

1. **Yee, K. S.** (1966). "Numerical solution of initial boundary value problems involving Maxwell's equations." *IEEE Trans. Antennas Propag.*, 14(3), 302-307.

2. **Taflove, A., & Hagness, S. C.** (2005). *Computational Electrodynamics: The Finite-Difference Time-Domain Method*. Artech House.

3. **Jackson, J. D.** (1998). *Classical Electrodynamics* (3rd ed.). Wiley. (Cavity resonator theory)
