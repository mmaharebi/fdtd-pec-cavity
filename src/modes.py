# Analytical TMz modes for a rectangular PEC cavity
from typing import List, Tuple
import numpy as np
from constants import c0

def analytic_modes(Lx: float, Ly: float, fmax: float,
                   mmax: int = 50, nmax: int = 50) -> tuple[np.ndarray, List[Tuple[int,int]]]:
    fs = []
    mn = []
    for m in range(1, mmax + 1):
        for n in range(1, nmax + 1):
            fmn = 0.5 * c0 * np.sqrt((m / Lx) ** 2 + (n / Ly) ** 2)
            if fmn <= fmax:
                fs.append(fmn); mn.append((m, n))
    order = np.argsort(fs)
    return np.array(fs)[order], [mn[k] for k in order]
