#!/usr/bin/env python3
"""v2.8 Ueberhang-Analyse fuer STL in Druckorientierung (Bett = Z-Minimum).
Unsupported = nach unten zeigende Flaechen flacher als 45 Grad (nz < -0.7071), nicht auf dem Bett,
ausser: Bruecken (waagerecht, an zwei gegenueberliegenden Seiten verankert, Spannweite <= 10 mm),
Dach kleiner waagerechter Loecher (Breite <= 3.6 mm Projektion ~ Loch <= 5 mm), Restflaechen < 0.5 mm2 (Tessellierung).
Inseln = Bereiche ohne Material darunter am Rand (beginnen in der Luft) zaehlen immer."""
import numpy as np, struct, sys, os, json, math
def load(p):
    b = open(p, "rb").read()
    if b[:5] == b"solid" and b"facet" in b[:400]:
        v = [list(map(float, l.split()[1:4])) for l in b.decode(errors="ignore").splitlines() if l.strip().startswith("vertex")]
        return np.array(v).reshape(-1, 3, 3)
    n = struct.unpack("<I", b[80:84])[0]
    a = np.frombuffer(b[84:84 + n * 50], dtype=np.dtype([("n", "<3f4"), ("v", "<9f4"), ("a", "<u2")]))
    return a["v"].reshape(-1, 3, 3).astype(float)
def analyse(p, span_max=10.0, hole_w=3.6, noise=0.5):
    T = load(p); z0 = T[:, :, 2].min()
    e1 = T[:, 1] - T[:, 0]; e2 = T[:, 2] - T[:, 0]; N = np.cross(e1, e2); A = np.linalg.norm(N, axis=1) / 2
    ok = A > 1e-12; nz = np.zeros(len(T)); nz[ok] = N[ok, 2] / (2 * A[ok])
    bed = T[:, :, 2].max(axis=1) < z0 + 0.02
    bed_area = A[bed & (nz < -0.99)].sum()
    down = (nz < -0.7075) & ~bed & ok
    # Kanten-Nachbarschaft
    key = lambda a, b: (tuple(np.round(a, 4)), tuple(np.round(b, 4)))
    em = {}
    for i in range(len(T)):
        for k in range(3):
            a, b = T[i, k], T[i, (k + 1) % 3]; kk = key(a, b) if tuple(np.round(a, 4)) < tuple(np.round(b, 4)) else key(b, a)
            em.setdefault(kk, []).append(i)
    nb = [[] for _ in range(len(T))]
    for kk, fs in em.items():
        for f in fs:
            for g in fs:
                if f != g: nb[f].append((g, kk))
    seen = np.zeros(len(T), bool); regs = []
    for i in np.where(down)[0]:
        if seen[i]: continue
        st = [i]; seen[i] = True; r = []
        while st:
            f = st.pop(); r.append(f)
            for g, _ in nb[f]:
                if down[g] and not seen[g]: seen[g] = True; st.append(g)
        regs.append(r)
    unsup = 0.0; bridges = 0.0; islands = 0; det = []
    for r in regs:
        r = np.array(r); ar = A[r].sum(); zr = T[r, :, 2].mean()
        pts = T[r, :, :2].reshape(-1, 2)
        anch = []
        for f in r:
            for g, kk in nb[f]:
                if down[g]: continue
                if T[g, :, 2].min() < T[f, :, 2].min() - 0.01: anch += [np.array(kk[0][:2]), np.array(kk[1][:2])]
        if T[r, :, 2].min() < z0 + 0.02: anch.append(pts.min(0)); anch.append(pts.max(0))
        flat = (nz[r] < -0.99).all(); AN = np.array(anch) if anch else None
        if ar < noise and nz[r].min() > -0.76: continue   # Tessellierungs-Splitter an 45-Grad-Kegeln
        if not anch: islands += 1; unsup += ar; det.append(("Insel", round(ar, 2), round(zr, 2), [round(x, 1) for x in pts.mean(0)])); continue
        wmin = 1e9; brid = False; hole = False
        for ang in np.arange(0, 180, 5):
            v = np.array([math.cos(math.radians(ang)), math.sin(math.radians(ang))]); u = pts @ v; ua = AN @ v
            w = u.max() - u.min(); wmin = min(wmin, w)
            two = ua.min() < u.min() + 1.0 and ua.max() > u.max() - 1.0
            if two and w <= span_max + 1e-6 and flat: brid = True
            if two and w <= hole_w: hole = True
        if brid: bridges += ar; continue
        if hole: continue
        w = wmin
        if ar < noise: continue
        unsup += ar; det.append(("Ueberhang", round(ar, 2), round(zr, 2), [round(x, 1) for x in pts.mean(0)], round(w, 1)))
    bb = T.reshape(-1, 3); fp = (bb[:, 0].max() - bb[:, 0].min()) * (bb[:, 1].max() - bb[:, 1].min()); h = bb[:, 2].max() - z0
    return dict(file=os.path.basename(p), unsupported_mm2=round(unsup, 2), islands=islands, bridges_mm2=round(bridges, 1), bed_mm2=round(bed_area, 1),
                height=round(h, 1), tall_thin=bool(bed_area < 0.15 * fp and h > 3 * math.sqrt(max(bed_area, 1e-9))), details=sorted(det, key=lambda d: -d[1])[:6])
if __name__ == "__main__":
    out = [analyse(p) for p in sys.argv[2:]]
    json.dump(out, open(sys.argv[1], "w"), indent=1)
    for o in out: print("%-28s unsup %8.2f  islands %d  bridges %7.1f  bed %8.1f  h %5.1f %s" % (o["file"], o["unsupported_mm2"], o["islands"], o["bridges_mm2"], o["bed_mm2"], o["height"], "TALL-THIN" if o["tall_thin"] else ""))
