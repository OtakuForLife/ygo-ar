# Elastica-Modell der gedruckten Bogenfeder (Rollfeder): Bogen R, Laenge S, Wurzel waagerecht am Boden eingespannt,
# senkrechte Spitzenlast F (Spitze gleitet reibungsfrei unter dem Stapel). Wo die Feder flach auf dem Boden liegt, rollt sie ab
# (Kruemmung 0 => Dehnung nie groesser als beim Flachdruecken: t/2R).
import math
E = 3500.0
def shoot(F, th_tip, S, k0, EI, ds=0.05, pts=False):
    th = th_tip; u = 0.0; h = 0.0; s = 0.0; P = [(0.0, 0.0)]
    while s < S:
        dth = k0 - F * u / EI
        if dth <= 0 and s > 0: break
        th -= dth * ds; u += math.cos(th) * ds; h += math.sin(th) * ds; s += ds
        if pts: P.append((u, h))
    return th, h, s, P
def solve(F, S, R, t, b, pts=False):
    EI = E * b * t ** 3 / 12; k0 = 1 / R
    lo, hi = -0.5, 3.5; glo = shoot(F, lo, S, k0, EI)[0]
    for _ in range(60):
        m = (lo + hi) / 2; gm = shoot(F, m, S, k0, EI)[0]
        if (gm > 0) == (glo > 0): lo, glo = m, gm
        else: hi = m
    th, h, l, P = shoot(F, (lo + hi) / 2, S, k0, EI, pts=pts)
    if not pts: return h, l
    # Punkte von der Wurzel aus: flacher Teil (S-l) + freier Bogen; P ist von der Spitze rueckwaerts (u, h relativ zum Abhebepunkt-Hoehe)
    hr = P[-1][1]; ur = P[-1][0]
    C = [(0.0, 0.0)] + [(S - l + (ur - u), (h - hh) * 0 + (hr - hh) * -1 if False else hr - hh) for u, hh in reversed(P)]
    C = [(0.0, 0.0), (S - l, 0.0)] + [((S - l) + (ur - u), hr - hh) for u, hh in reversed(P)]
    return h, l, C
def F_at(h, S, R, t, b):
    lo, hi = 0.0, 60.0
    for _ in range(40):
        m = (lo + hi) / 2
        if solve(m, S, R, t, b)[0] > h: lo = m
        else: hi = m
    return (lo + hi) / 2
