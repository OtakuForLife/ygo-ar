# ARM-DISK v2.3 – runde, tragbare Duel Disk (linker Unterarm) auf Basis des DUEL-DISK v2.8 Kartenplatz-Moduls.
# Run: freecadcmd build_arm_disk_v2_1.py -> ARM-DISK_v2.1.FCStd + v2.1/stls (Druckorientierung) + v2/stl_world (Einbaulage) + v2/build_info.json
# Parametrisch: alle Masse in P (Tabelle "Params" im FCStd). Wert aendern -> neu laufen lassen. Rechter Arm: ARM_SIDE=-1 ARM_OUT=<ordner>.
# Koordinaten: Ursprung = Stapelmitte (Drehachse v2.8) auf Traeger-Oberseite (z=0). +X = Hand, -X = Schulter/Ellbogen, -Y = zum Koerper (S/T-Maul).
# Aufbau: runde Gehaeuse-Scheibe R120 (Haut liegt auf dem v2.8-Deckel, verdeckt dessen Schrauben, Fenster R59 fuer Drehteller/Monsterkarte),
# Elektronik-Bucht +Y unter der Haut, Kartenbox (Deck + Friedhof, Einschub von der Schulterseite) bei -X, 2-teiliger gerippter Traeger.
import FreeCAD as App, Part, Mesh, json, os, math, shutil, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) if '__file__' in dir() else '/workspace/yugioh-ar/arm-disk/v2.3'); sys.path.insert(0, '/workspace/yugioh-ar/arm-disk/v2.3'); import spring_elastica as SE
from FreeCAD import Vector as V
HERE = os.environ.get("ARM_OUT", "/workspace/yugioh-ar/arm-disk/v2.3"); V28 = "/workspace/yugioh-ar/disk-v2/DUEL-DISK_v2.FCStd"
P = dict(
    side=int(os.environ.get("ARM_SIDE", "1")),
    clr_move=0.5, glue=0.2, vyper_os=0.3, gap=0.3, wall=2.4, wall_min=1.2,
    hs=66.5, H_f=8.0, fl_t=2.0, fl_w=10.0, scr_in=6.0, fboss_d=8.0, tile_hole=2.5, tile_hole_d=7.0, z_stack_top=28.95,
    # Gehaeuse-Scheibe
    R=120.0, skin=1.8, rim_w=1.6, tile_frame=14.0, light_ring=8.0, light_strip=10.0, r_open=59.0, ch_out=3.0, ch_out_h=4.0, ch_in=1.6, mouth_w=80.0, rib_t=2.4, rib_boss_d=7.0, rib_r_scr=110.0,
    ss_hole_m=1.5, cable_notch_w=10.0, cable_notch_h=8.0, cable_notch_ang=137.0,
    # Karten
    # v2.3 Karten-Huelsen (Deck vorne offen = +Y, Friedhof hinten offen = -Y), Karten quer zum Arm
    sc_w=67.0, sc_l=92.0, clr_card=0.75, deck_h=40.0, gy_h=30.0, pk_head=1.5, pk_wall=2.4, pk_roof=2.0, pk_end=2.4,
    tun_h=3.5, tun_roof=1.6, rail_h=3.0, edge_c=2.0, edge_clr=0.5, sp_t=1.2, sp_b=28.0, sp_R=60.0, sp_S=82.0, sp_foot=8.0, sp_ch=1.0, lip_h=1.5, lip_in=2.0, pinch_open=66.2, cut_w=58.0, cut_l=45.0,
    ff_t=1.2, ff_L=24.0, ff_slit=1.0, ff_prot=2.0, ff_tooth=3.0, ff_y0=6.0, ff_clr=0.5,
    # ESP32
    esp_l=55.0, esp_w=28.0, esp_t=1.6, esp_side=5.0, esp_above=15.0, esp_post=3.0, esp_loc=0.3, esp_ant=6.0,
    bay_floor=2.0, lid_t=2.0, lid_lip=3.0, lid_lip_w=1.6, usb_w=14.0, usb_z0=3.5, usb_h=9.0,
    chR_w=14.0, chR_x=-11.0, chS_w=8.0, chS_x=11.0, ch_h=6.0,
    # Unterarm / Traeger (gerippt)
    arm_r=50.0, arm_chord=64.0, arm_y=0.0, band_w=90.0, pt=1.6, arch_min=2.0, rib_pitch=40.0, band_ribs_y=(-43.8, 0.0, 43.8),
    split_x=-84.0, tab_x1=150.0, tab_wing=10.0,
    strap_w=25.0, strap_t=4.0, slot_bar=4.5, strapA_x=-110.0, strapB_x=136.0,
    pin_d=5.0, pin_l=8.0, pin_boss_d=9.0, pin_boss_h=4.0, scr_d=3.4, scr_core=2.5, cbore_d=6.5, cb_boss_d=8.0, bay_boss_d=7.0,
)
p = P; s = p["side"]; hs, w = p["hs"], p["wall"]
p["sag"] = p["arm_r"] - math.sqrt(p["arm_r"]**2 - (p["arm_chord"]/2)**2)
p["band_h"] = p["pt"] + p["arch_min"] + p["sag"]
p["bay_ix"] = p["esp_l"] + 2*p["esp_side"]; p["bay_iy"] = p["esp_w"] + 2*p["esp_side"]
p["bay_ih"] = p["esp_post"] + p["esp_t"] + p["esp_above"]; p["bay_h"] = p["bay_floor"] + p["bay_ih"]
p["esp_z"] = p["bay_floor"] + p["esp_post"]
p["z_skin"] = p["H_f"] + p["z_stack_top"]; p["z_disc_top"] = p["z_skin"] + p["skin"]
p["well_w"] = p["sc_w"] + 2*p["clr_card"]; p["well_l"] = p["sc_l"] + 2*p["clr_card"]
p["pin_hole"] = p["pin_d"] + p["vyper_os"] + 2*p["glue"]          # Klebesitz: Vyper-Uebermass + 0.2 Klebespalt je Seite
p["cb_floor"] = p["tun_h"] + p["tun_roof"]
p["pk_ow"] = p["well_w"] + 2*p["pk_wall"]
p["cb_x1"] = -hs - p["gap"]; p["deck_x1"] = p["cb_x1"]; p["deck_x0"] = p["deck_x1"] - p["pk_ow"]
p["gy_x1"] = p["deck_x0"] - p["glue"]; p["gy_x0"] = p["gy_x1"] - p["pk_ow"]; p["cb_x0"] = p["gy_x0"]
p["y_tip"] = p["well_l"]/2; p["y_mouth"] = p["y_tip"] + p["lip_in"] + p["lip_h"]   # Lippe: innen flach (37 Grad zur Senkrechten beim Druck), aussen 45 Grad
p["cb_y1"] = p["y_mouth"]; p["cb_y0"] = -p["cb_y1"]
p["pinch_pr"] = (p["well_w"] - p["pinch_open"])/2
p["sp_yr"] = -p["y_tip"] + p["sp_foot"]                            # Federfuss am geschlossenen Ende, Feder laeuft zur Oeffnung (Spitze unter dem Griffausschnitt)
def bx(x0, x1, y0, y1, z0, z1):
    if s < 0: x0, x1 = -x1, -x0
    return Part.makeBox(x1-x0, y1-y0, z1-z0, V(x0, y0, z0))
def bxs(x0, x1, y0, y1, z0, z1): return Part.makeBox(x1-x0, y1-y0, z1-z0, V(x0, y0, z0))
def cz(d, x, y, z0, z1): return Part.makeCylinder(d/2, z1-z0, V(s*x, y, z0))
def czs(d, x, y, z0, z1): return Part.makeCylinder(d/2, z1-z0, V(x, y, z0))
def M(o):
    if s < 0: o = o.mirror(V(0, 0, 0), V(1, 0, 0))
    return o
def fuse(L):
    r = L[0]
    for o in L[1:]: r = r.fuse(o)
    return r.removeSplitter()
def cutall(b, L):
    for o in L: b = b.cut(o)
    return b.removeSplitter()
def gable_win_x(xa, xb, yc, wd, z0, h):    # Fenster in einer Wand senkrecht zu X (Giebel 45 Grad)
    r = bx(xa, xb, yc - wd/2, yc + wd/2, z0, z0 + h)
    g = Part.makeBox(xb - xa, wd/math.sqrt(2), wd/math.sqrt(2)); g.rotate(V(0, 0, 0), V(1, 0, 0), 45); g.translate(V(xa if s > 0 else -xb, yc, z0 + h - wd/2))
    return r.fuse(g)
def gable_win_y(xc, wd, ya, yb, z0, h):    # Fenster in einer Wand senkrecht zu Y
    r = bx(xc - wd/2, xc + wd/2, ya, yb, z0, z0 + h)
    g = Part.makeBox(wd/math.sqrt(2), yb - ya, wd/math.sqrt(2)); g.rotate(V(0, 0, 0), V(0, 1, 0), -45); g.translate(V(s*xc, ya, z0 + h - wd/2))
    return r.fuse(g)
def rib(ang, r0, r1, z0, z1, t):
    o = Part.makeBox(r1 - r0, t, z1 - z0, V(r0, -t/2, z0)); o.rotate(V(0, 0, 0), V(0, 0, 1), ang); return M(o)
# ------------------------------------------------ v2.8 Stapel unveraendert
d28 = App.openDocument(V28); STACK = {}
for n in ("base", "st_tray", "st_ceiling", "deck", "carrier", "turntable", "cover", "dummy_rc522_l", "dummy_rc522_u", "dummy_ferrite",
          "dummy_card", "dummy_card_st_sl", "dummy_sw_body", "dummy_ss", "dummy_sst"):
    sh = d28.getObject(n).Shape.copy(); sh.translate(V(0, 0, p["H_f"])); STACK[n] = sh
p["fer_gap"] = d28.getObject("Params").get("fer_gap"); App.closeDocument(d28.Name)
# ------------------------------------------------ ARM-KACHEL (v2.8-Kachel) mit Kabelports zur Bucht in der +Y-Wand
H = p["H_f"]
tile = cutall(bxs(-hs, hs, -hs, hs, 0, H), [bxs(-hs + w, hs - w, -hs + w, hs - w, -1, H + 1)])
fl = cutall(bxs(-hs + w - .1, hs - w + .1, -hs + w - .1, hs - w + .1, 0, p["fl_t"]),
            [bxs(-hs + w + p["fl_w"], hs - w - p["fl_w"], -hs + w + p["fl_w"], hs - w - p["fl_w"], -1, 5)])
TB = [(sx*(hs - p["scr_in"]), sy*(hs - p["scr_in"])) for sx in (1, -1) for sy in (1, -1)]
TS = [(sx*45, sy*(hs - 6)) for sx in (1, -1) for sy in (1, -1)]
TP = [(0, hs - 6), (0, -(hs - 6))]
tile = fuse([tile, fl] + [czs(p["fboss_d"], x, y, 0, H) for x, y in TB] + [czs(p["cb_boss_d"], x, y, 0, 6) for x, y in TS] +
            [czs(p["cb_boss_d"] + 1, x, y, 0, 6) for x, y in TP])
tcut = [czs(p["tile_hole"], x, y, H - p["tile_hole_d"], H + 1) for x, y in TB] + [czs(p["scr_core"], x, y, -1, 5) for x, y in TS] + \
       [czs(p["pin_hole"], x, y, -1, 4.5) for x, y in TP]
for xc, wd in ((p["chR_x"], p["chR_w"]), (p["chS_x"], p["chS_w"])):
    tcut.append(bx(xc - wd/2, xc + wd/2, hs - w - 1, hs + 1, p["fl_t"], H + 1))
tile = cutall(tile, tcut)
# ------------------------------------------------ ELEKTRONIK-BUCHT (+Y, unter der Gehaeuse-Haut), USB-C am -X-Ende
x0 = -(p["bay_ix"]/2 + w); x1 = -x0
by0 = hs + p["gap"]; by1 = by0 + p["bay_iy"] + 2*w; byc = (by0 + by1)/2; iy = p["bay_iy"]/2
p.update(bay_x0=x0, bay_x1=x1, bay_y0=by0, bay_y1=by1, bay_yc=byc)
bay = cutall(bx(x0, x1, by0, by1, 0, p["bay_h"]), [bx(x0 + w, x1 - w, by0 + w, by1 - w, p["bay_floor"], p["bay_h"] + 1)])
ex0 = x0 + w + p["esp_side"]; ex1 = ex0 + p["esp_l"]; ey = p["esp_w"]/2; ez = p["esp_z"]
BB = [(xx, byc + sy*(iy - 2.0)) for xx in (x0 + w + 2.0, x1 - w - 2.0) for sy in (1, -1)]
badd = [bay] + [cz(p["bay_boss_d"], x, y, 0, 6) for x, y in BB]
for cx in (ex0, ex1):
    for cy in (byc - ey, byc + ey):
        sx = 1 if cx == ex0 else -1; sy = 1 if cy < byc else -1
        badd.append(bx(cx + sx*1.0 - 1.5, cx + sx*1.0 + 1.5, cy + sy*1.0 - 1.5, cy + sy*1.0 + 1.5, 0, ez))
        a0, a1 = sorted((cx - sx*p["esp_loc"], cx - sx*(p["esp_loc"] + 1.6))); b0, b1 = sorted((cy - sy*(p["esp_loc"] + 1.6), cy + sy*3.0))
        badd.append(bx(a0, a1, b0, b1, 0, ez + p["esp_t"] + 1.0))
        a0, a1 = sorted((cx - sx*(p["esp_loc"] + 1.6), cx + sx*3.0)); b0, b1 = sorted((cy - sy*p["esp_loc"], cy - sy*(p["esp_loc"] + 1.6)))
        badd.append(bx(a0, a1, b0, b1, 0, ez + p["esp_t"] + 1.0))
BPIN = [(ex0 + 5, byc + sy*(iy - 2.8)) for sy in (1, -1)]
for sy in (1, -1):
    ya_, yb_ = sorted((byc + sy*(iy + .1), byc + sy*(iy - 7.5))); badd.append(bx(ex0 + 0.5, ex0 + 9.5, ya_, yb_, 0, 4.5))
bay = fuse(badd)
bcut = [cz(p["scr_core"], x, y, -1, 5) for x, y in BB] + [cz(p["pin_hole"], x, y, -1, 4.0) for x, y in BPIN]
usb_zc = ez + p["esp_t"] + 1.6
bcut.append(gable_win_x(x0 - 1, x0 + w + 1, byc, p["usb_w"], p["usb_z0"], p["usb_h"]))
for xc, wd in ((p["chR_x"], p["chR_w"]), (p["chS_x"], p["chS_w"])):
    bcut.append(gable_win_y(xc, wd, by0 - 1, by0 + w + 1, p["bay_floor"], p["ch_h"]))
bay = cutall(bay, bcut)
cp = p["glue"]; lw = p["lid_lip_w"]   # v2.3: Deckel lose (0.2 Spiel), vom Gehaeuse gehalten
lid = bx(x0, x1, by0, by1, p["bay_h"], p["bay_h"] + p["lid_t"])
lip = cutall(bx(x0 + w + cp, x1 - w - cp, by0 + w + cp, by1 - w - cp, p["bay_h"] - p["lid_lip"], p["bay_h"] + .1),
             [bx(x0 + w + cp + lw, x1 - w - cp - lw, by0 + w + cp + lw, by1 - w - cp - lw, 0, 99), bx(x0 - 1, x0 + w + 2, byc - p["usb_w"]/2 - 1, byc + p["usb_w"]/2 + 1, 0, 99)])
nose = [bx(ex1 - 4, ex1 - 1, byc + (ey - 3 if sy > 0 else -ey), byc + (ey if sy > 0 else -ey + 3), ez + p["esp_t"] + 0.3, p["bay_h"] + .1) for sy in (1, -1)]
lid = fuse([lid, lip] + nose)
# ------------------------------------------------ v2.3 KARTEN-HUELSEN: Deck vorne offen (+Y, vom Koerper weg), Friedhof hinten offen (-Y, zum Koerper)
# Geschlossene Huelse, nur die kurze Stirnseite offen + Griffausschnitt im Dach am offenen Ende. Kein Tor, kein Deckel, keine Rast.
# Halt: 45/45-Grad-Bodenlippe (1.5) + 2 seitliche Klemmrippen (Oeffnung 66.2 < Karte 67, Karte biegt sich leicht) am offenen Ende.
# Druck: stehend auf der geschlossenen Stirnseite (alle Schraegen 45 Grad, Gurt-Tunnel senkrecht) -> stuetzfrei. Auf den Traeger geklebt.
cx0, cx1, cy0, cy1 = p["cb_x0"], p["cb_x1"], p["cb_y0"], p["cb_y1"]
CB = []; CP = []                                                    # keine Schrauben/Stifte mehr: Huelsen werden geklebt
def tri_y(xa, xb, pts):                                             # Prisma: Profil (y,z) ueber x extrudiert
    f = Part.Face(Part.makePolygon([V(0, y_, z_) for y_, z_ in pts] + [V(0, pts[0][0], pts[0][1])])); o = f.extrude(V(xb - xa, 0, 0)); o.translate(V(xa, 0, 0)); return M(o)
def tri_x(x_wall, sgn, y_pts, z0, z1):                             # Klemmrippe: Profil (y, Abstand d) an Wand x_wall nach innen (sgn)
    f = Part.Face(Part.makePolygon([V(x_wall + sgn*d_, y_, z0) for y_, d_ in y_pts] + [V(x_wall + sgn*y_pts[0][1], y_pts[0][0], z0)])); o = f.extrude(V(0, 0, z1 - z0)); return M(o)
def pocket(xo0, xo1, hc, mouth):                                    # mouth = +1 (offen +Y) / -1 (offen -Y)
    xi0, xi1 = xo0 + p["pk_wall"], xo1 - p["pk_wall"]; yt, ym = p["y_tip"], p["y_mouth"]; zf = p["cb_floor"]; z0 = zf + p["rail_h"]
    Hi = z0 + hc + p["edge_clr"] + p["edge_c"]; top = Hi + p["pk_roof"]; xc = (xi0 + xi1)/2
    ye = -(yt + p["pk_end"])
    body = bx(xo0, xo1, ye, ym, 0, top)
    bw = p["sp_b"]/2; yr = p["sp_yr"]
    cuts = [bx(xi0, xi1, -yt, ym + 1, z0, Hi),                                                  # Kartenraum ueber den Schienen
            bx(xc - bw - p["sp_ch"], xc + bw + p["sp_ch"], yr, yt, zf, z0 + .01),               # Federkanal (Feder liegt flach zwischen den Schienen)
            bx(xc - bw - p["glue"], xc + bw + p["glue"], -yt - .01, yr + .01, zf, z0 + .01),    # Klebesitz Federfuss am geschlossenen Ende
            bx(xc - p["cut_w"]/2, xc + p["cut_w"]/2, ym - p["cut_l"], ym + 1, Hi - 1, top + 1)]   # Griffausschnitt im Dach
    adds = [tri_y(xi0 - .01, xi1 + .01, [(yt, z0 - .01), (yt + p["lip_in"], z0 + p["lip_h"]), (ym, z0 - .01)])]       # Bodenlippe (auf Schienenhoehe)
    ec, ey0 = p["edge_c"], p["sc_l"]/2 + 0.1                                                     # Halte-Kante an der Decke (45 Grad unten, druckbar stehend)
    for xa, xb in ((xi0 - .01, xc - p["cut_w"]/2 + .01), (xc + p["cut_w"]/2 - .01, xi1 + .01)):
        adds.append(tri_y(xa, xb, [(ey0, Hi + .01), (ey0 + 1.2*ec, Hi - ec), (ym - 0.85*ec, Hi - ec), (ym, Hi + .01)]))   # Innenflanke 40 Grad zur Senkrechten im Druck, aussen steiler (zeigt beim Druck nach oben)
    pr = p["pinch_pr"]
    for xw, sg in ((xi0, 1), (xi1, -1)):
        f = Part.Face(Part.makePolygon([V(xw - sg*.01, ym - 2.5*pr - .01, z0 - .01), V(xw + sg*pr, ym - pr, z0 - .01), V(xw - sg*.01, ym + .01, z0 - .01), V(xw - sg*.01, ym - 2.5*pr - .01, z0 - .01)]))
        adds.append(M(f.extrude(V(0, 0, Hi - ec - z0))))
    if hc == p["deck_h"]:
        sw = p["strap_w"]/2 + p["clr_move"] + 0.5
        cuts.append(bx(p["strapA_x"] - sw, p["strapA_x"] + sw, ye - 1, ym + 1, -1, p["tun_h"]))
    sh_ = fuse([cutall(body, cuts)] + adds)
    if mouth < 0: sh_ = sh_.mirror(V(0, 0, 0), V(0, 1, 0))
    return sh_, xi0, xi1, Hi, top
def spring(xc, F, mouth):                                           # Bogenfeder (Elastica-Form bei Last F), Wurzel bei yr, laeuft Richtung geschlossenes Ende
    h, l, C = SE.solve(F, p["sp_S"], p["sp_R"], p["sp_t"], p["sp_b"], pts=True)
    C = C[::8] + [C[-1]]; tt = p["sp_t"]/2; zc = p["cb_floor"] + tt; yr = p["sp_yr"]
    up, dn = [], []
    for i, (u, z) in enumerate(C):
        a_ = C[max(i - 1, 0)]; b_ = C[min(i + 1, len(C) - 1)]; dx, dz = b_[0] - a_[0], b_[1] - a_[1]; n = math.hypot(dx, dz) or 1
        nx, nz = -dz/n, dx/n
        up.append((u + nx*tt, z + nz*tt)); dn.append((u - nx*tt, z - nz*tt))
    poly = [(yr + 0.0, zc - tt)] + [(yr + u, zc + z) for u, z in dn[1:]] + [(yr + u, zc + z) for u, z in reversed(up[1:])] + [(yr, zc + tt)]
    pf = Part.Face(Part.makePolygon([V(0, y_, z_) for y_, z_ in poly] + [V(0, poly[0][0], poly[0][1])]))
    arm = pf.extrude(V(p["sp_b"], 0, 0)); arm.translate(V(s*xc - p["sp_b"]/2, 0, 0))
    foot = Part.makeBox(p["sp_b"], p["sp_foot"] + 0.3, p["rail_h"], V(s*xc - p["sp_b"]/2, yr - p["sp_foot"], p["cb_floor"]))
    assert arm.isValid() and arm.Volume > 0.9*p["sp_t"]*p["sp_S"]*p["sp_b"], "Feder-Profil ungueltig"
    sp = arm.fuse(foot).removeSplitter()
    if mouth < 0: sp = sp.mirror(V(0, 0, 0), V(0, 1, 0))
    return sp, h
deck_pk, dxi0, dxi1, dHi, dtop = pocket(p["deck_x0"], p["deck_x1"], p["deck_h"], +1)
gy_pk, gxi0, gxi1, gHi, gtop = pocket(p["gy_x0"], p["gy_x1"], p["gy_h"], -1)
p["deck_top"] = dtop; p["gy_top"] = gtop; p["deck_Hi"] = dHi; p["gy_Hi"] = gHi
hz = p["cb_floor"] + 2*p["sp_t"] - p["sp_t"]                          # Hoehe Mittellinie-Wurzel + t/2 -> Kontaktflaeche = zc + h + t/2
def h_for(card_bottom): return card_bottom - (p["cb_floor"] + p["sp_t"]/2) - p["sp_t"]/2
SPR = {}
for nm, Hi_, hc in (("deck", dHi, p["deck_h"]), ("gy", gHi, p["gy_h"])):
    SPR[nm] = dict(F_empty=SE.F_at(h_for(Hi_), p["sp_S"], p["sp_R"], p["sp_t"], p["sp_b"]),
                   F_full=SE.F_at(h_for(Hi_ - hc), p["sp_S"], p["sp_R"], p["sp_t"], p["sp_b"]),
                   F_release=SE.F_at(h_for(p["cb_floor"] + p["rail_h"]), p["sp_S"], p["sp_R"], p["sp_t"], p["sp_b"]),
                   h_free=SE.solve(1e-4, p["sp_S"], p["sp_R"], p["sp_t"], p["sp_b"])[0], h_empty=h_for(Hi_), h_full=h_for(Hi_ - hc), h_release=h_for(p["cb_floor"] + p["rail_h"]),
                   strain_max=p["sp_t"]/(2*p["sp_R"]))
deck_sp, _ = spring((dxi0 + dxi1)/2, SE.F_at(h_for(dHi - p["deck_h"]) - 0.1, p["sp_S"], p["sp_R"], p["sp_t"], p["sp_b"]), +1)   # Einbaulage: volles Deck
gy_sp, _ = spring((gxi0 + gxi1)/2, SE.F_at(h_for(gHi - p["gy_h"]) - 0.1, p["sp_S"], p["sp_R"], p["sp_t"], p["sp_b"]), -1)
spring_free, _ = spring(0, 1e-4, +1)
# ------------------------------------------------ v2.1 DREHTELLER: 2 Federfinger an der +X-Langseite der Mulde (Reibhalt), sonst v2.8 unveraendert
TT = STACK["turntable"]; tb = TT.BoundBox; z0t, z1t = tb.ZMin, tb.ZMax
pw2 = 60.5/2; ftc = []; fta = []
for sy in (1, -1):
    y0f, y1f = sorted((sy*p["ff_y0"], sy*(p["ff_y0"] + p["ff_L"] + p["ff_slit"])))
    ftc.append(bxs(pw2, pw2 + p["ff_slit"], y0f, y1f, z0t - 1, z1t + 1))                                   # innerer Schlitz
    ftc.append(bxs(pw2 + p["ff_slit"] + p["ff_t"], pw2 + 2*p["ff_slit"] + p["ff_t"], y0f, y1f, z0t - 1, z1t + 1))   # aeusserer Schlitz
    ye0, ye1 = sorted((sy*(p["ff_y0"] + p["ff_L"]), sy*(p["ff_y0"] + p["ff_L"] + p["ff_slit"])))
    ftc.append(bxs(pw2, pw2 + 2*p["ff_slit"] + p["ff_t"], ye0, ye1, z0t - 1, z1t + 1))                      # Endschlitz
    yt0, yt1 = sorted((sy*(p["ff_y0"] + p["ff_L"] - p["ff_tooth"]), sy*(p["ff_y0"] + p["ff_L"])))
    c0, c1 = sorted((yt0 - p["ff_clr"]*(1 if sy > 0 else 1), yt1 + p["ff_clr"]))
    ftc.append(bxs(pw2 - p["ff_prot"] - p["ff_clr"], pw2 + .01, min(yt0, yt1) - p["ff_clr"], max(yt0, yt1) + p["ff_clr"], z0t - 1, z1t + 1))   # Freischnitt unter dem Zahn
    tooth = bxs(pw2 - p["ff_prot"], pw2 + p["ff_slit"] + .05, yt0, yt1, z0t, z1t)
    ch = Part.Face(Part.makePolygon([V(pw2 - p["ff_prot"] - .01, 0, z1t + .01), V(pw2 - p["ff_prot"] + 1.2, 0, z1t + .01), V(pw2 - p["ff_prot"] - .01, 0, z1t - 1.2), V(pw2 - p["ff_prot"] - .01, 0, z1t + .01)])).extrude(V(0, 1, 0))
    ch.scale if False else None
    chs = ch.copy(); chs.translate(V(0, 0, 0)); chs = Part.Face(Part.makePolygon([V(pw2 - p["ff_prot"] - .01, yt0 - .01, z1t + .01), V(pw2 - p["ff_prot"] + 1.2, yt0 - .01, z1t + .01), V(pw2 - p["ff_prot"] - .01, yt0 - .01, z1t - 1.2), V(pw2 - p["ff_prot"] - .01, yt0 - .01, z1t + .01)])).extrude(V(0, yt1 - yt0 + .02, 0))
    fta.append(tooth.cut(chs))
turntable21 = cutall(TT, ftc).fuse(fta).removeSplitter()
STACK["turntable"] = turntable21

# ------------------------------------------------ GEHAEUSE-SCHEIBE (kopfueber drucken: Haut aufs Bett)
R = p["R"]; zs, zt = p["z_skin"], p["z_disc_top"]
outer = Part.makeCylinder(R, zt - p["ch_out_h"]).fuse(Part.makeCone(R, R - p["ch_out"], p["ch_out_h"], V(0, 0, zt - p["ch_out_h"])))
hollow = Part.makeCylinder(R - p["rim_w"], zs + 1, V(0, 0, -1))
shell = outer.cut(hollow)
inner_add = []
# Rippen (radial), Schraubdome unten an den Rippen
p["rib_angles"] = [35, -35, 60, -60, 240]
RIBS = []
for a in p["rib_angles"]:
    ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
    r0 = min(hs/abs(ca) if abs(ca) > 1e-6 else 1e9, hs/abs(sa) if abs(sa) > 1e-6 else 1e9) + 1.5
    if a == 240: r0 = max(r0, (p["mouth_w"]/2 + w + 1.5)/abs(ca))
    RIBS.append((a, r0)); inner_add.append(rib(a, r0, R - 1, 0, zs + .1, p["rib_t"]))
SHS = [(s*p["rib_r_scr"]*math.cos(math.radians(a)), p["rib_r_scr"]*math.sin(math.radians(a))) for a in p["rib_angles"]]
SHS = [(x*s, y) for x, y in SHS]   # in "linker" Notation (cz spiegelt)
inner_add += [cz(p["rib_boss_d"], x, y, 0, 8) for x, y in SHS]
# Waende entlang der Kartenbox-Aussparung und des S/T-Mauls
g = p["gap"]
inner_add += [bx(-hs, -hs + w, hs + g, R, 0, zs + .1), bx(-hs, -hs + w, -R, -hs - g, 0, zs + .1)]   # v2.3: Scheibe an der Schulterseite gerade abgeschnitten
mw = p["mouth_w"]/2
inner_add += [bxs(mw, mw + w, -R, -hs - g, 0, zt), bxs(-mw - w, -mw, -R, -hs - g, 0, zt)]
skin = Part.makeCylinder(R - 1, zt - zs, V(0, 0, zs))
inner_add += [cz(6.0, xx, byc, p["bay_h"] + p["lid_t"] + p["glue"] + 0.1, zs + .1) for xx in (x0 + 8, x1 - 8)]   # v2.3: 2 Niederhalter fuer den losen Bucht-Deckel
shell = fuse([shell, skin] + [o.common(Part.makeCylinder(R - 1, 99, V(0, 0, -1))) for o in inner_add])
shc = [Part.makeCylinder(p["r_open"], 99, V(0, 0, -1)), Part.makeCone(p["r_open"], p["r_open"] + p["ch_in"], zt - zs + 0.01, V(0, 0, zs))]
shc += [bx(-999, -hs, -999, 999, -1, 99),                                         # v2.3: Kartenwege vorne/hinten frei
        bxs(-hs - g, hs + g, -hs - g, hs + g, -1, zs),                                  # Stapel (Haut liegt oben auf dem Deckel)
        bxs(-mw, mw, -999, -hs - g, -1, 99)]                                            # S/T-Maul zum Koerper
ssb = STACK["dummy_ss"].BoundBox; m_ = p["ss_hole_m"]
shc.append(bxs(ssb.XMin - m_, ssb.XMax + m_, ssb.YMin - m_, ssb.YMax + m_, zs - 1, 99))   # Monster-Schalter bleibt bedienbar
sstb = STACK["dummy_sst"].BoundBox
shc.append(bxs(sstb.XMin - 1, sstb.XMax + 1, sstb.YMin - 1, -hs, -1, sstb.ZMax + 1))
# Bucht-Freiraum
shc.append(bx(x0 - g, x1 + g, by0 - g, by1 + g, -1, p["bay_h"] + p["lid_t"] + p["glue"] + 0.1))
# USB-Kabel-Kerbe im Rand unten (stuetzfrei: von unten offen)
shc.append(bx(-hs - 1, -hs + w + 1, byc - p["cable_notch_w"]/2, byc + p["cable_notch_w"]/2, -1, p["cable_notch_h"]))   # v2.3: USB-Kerbe in der geraden Wand
shc += [cz(p["scr_core"], x, y, -1, 6) for x, y in SHS]
shell = cutall(shell, shc)
# ------------------------------------------------ TRAEGER (2 Teile, gerippt, kopfueber drucken)
pt, bh, ya = p["pt"], p["band_h"], p["arm_y"]; sx_ = p["split_x"]
LR = p["light_ring"]; LS = p["light_strip"]
keep = [bxs(-hs - 1, hs + 1, -hs - 1, hs + 1, -pt, 0).cut(bxs(-hs + p["tile_frame"], hs - p["tile_frame"], -hs + p["tile_frame"], hs - p["tile_frame"], -9, 9)), bx(x0 - 2, x1 + 2, by0 - 2, by1 + 2, -pt, 0),
        Part.makeCylinder(R, pt, V(0, 0, -pt)).cut(Part.makeCylinder(R - LR, pt + 2, V(0, 0, -pt - 1))),
        bx(-999, 999, ya - p["band_w"]/2, ya + p["band_w"]/2, -pt, 0)]
for a_, r0_ in RIBS: keep.append(rib(a_, r0_ - 3, R, -pt, 0, LS))
keep += [cz(14, x, y, -pt, 0) for x, y in SHS + CB + CP + BPIN + BB]
keep.append(bx(sx_, -hs + 1, cy0, cy1, -pt, 0))   # unter der Kartenbox (Teil B)
plateB = fuse(keep).common(Part.makeCylinder(R, pt + 2, V(0, 0, -pt - 1))).common(bx(-hs - g, 999, -999, 999, -9, 9)).fuse(bx(sx_, -hs + 1, cy0, cy1, -pt, 0))
foot = fuse([plateB.cut(bx(-999, sx_ + g/2, -999, 999, -9, 9)),
             bx(sx_ + g/2, p["tab_x1"], ya - p["band_w"]/2 - p["tab_wing"], ya + p["band_w"]/2 + p["tab_wing"], -pt, 0)])
footA = fuse([bx(cx0, sx_ - g/2, cy0, cy1, -pt, 0),
              bx(p["strapA_x"] - 20, p["strapA_x"] + 20, -(cy1 + 11), cy1 + 11, -pt, 0)])
zc = -bh - math.sqrt(p["arm_r"]**2 - (p["arm_chord"]/2)**2)
def band(xa, xb):
    b = bx(xa, xb, ya - p["band_w"]/2, ya + p["band_w"]/2, -bh, -pt + .1)
    ribs = [bx(xa, xb, y - p["rib_t"]/2, y + p["rib_t"]/2, -bh, 0) for y in p["band_ribs_y"]]
    xx = xa
    while xx <= xb + 1e-6:
        ribs.append(bx(min(max(xx - 1.2, xa), xb - 2.4), min(max(xx - 1.2, xa), xb - 2.4) + 2.4, ya - p["band_w"]/2, ya + p["band_w"]/2, -bh, 0)); xx += p["rib_pitch"]
    b = b.common(fuse(ribs))
    arch = Part.makeCylinder(p["arm_r"], 999, V(-499, ya, zc), V(1, 0, 0))
    return b.cut(arch)
bbB = fuse([foot, band(sx_ + g/2, p["tab_x1"])]); bbA = fuse([footA, band(cx0, sx_ - g/2)])
p["slots"] = [(p["strapA_x"], -(cy1 + 2.5 + p["strap_t"]), -(cy1 + 2.5)), (p["strapA_x"], cy1 + 2.5, cy1 + 2.5 + p["strap_t"]),
              (p["strapB_x"], ya - p["band_w"]/2 - 2 - p["strap_t"], ya - p["band_w"]/2 - 2), (p["strapB_x"], ya + p["band_w"]/2 + 2, ya + p["band_w"]/2 + 2 + p["strap_t"])]
sw2 = p["strap_w"]/2 + p["clr_move"]
SCR = TS + BB + SHS; PINS = TP + BPIN + CP
def holes(part, isA):
    cuts = []; adds = []
    for gx, y0_, y1_ in p["slots"]:
        if (gx < sx_) == isA: cuts.append(bx(gx - sw2, gx + sw2, y0_, y1_, -bh - 1, 1))
    for x, y in SCR:
        if (x < sx_) != isA: continue
        cuts.append(cz(p["scr_d"], x, y, -bh - 1, 1))
        if abs(y - ya) < p["band_w"]/2 + 3: cuts.append(cz(p["cbore_d"], x, y, -bh - 1, -pt))
    for x, y in CB:
        if (x < sx_) != isA: continue
        adds.append(cz(8.0, x, y, -pt - 5, -pt + .1)); cuts.append(cz(p["scr_core"], x, y, -pt - 5 - 1, 1))
    for x, y in PINS:
        if (x < sx_) != isA: continue
        adds.append(cz(p["pin_boss_d"], x, y, -pt - p["pin_boss_h"], -pt + .1)); cuts.append(cz(p["pin_hole"], x, y, -bh - 1, 1))
    return cutall(fuse([part] + adds), cuts)
bbA = holes(bbA, True); bbB = holes(bbB, False)
pin = Part.makeCylinder(p["pin_d"]/2, p["pin_l"]); pin = pin.makeChamfer(0.4, [e for e in pin.Edges if e.Curve.__class__.__name__ == "Circle"])
p["n_pins"] = len(PINS); p["n_screws"] = len(SCR)
# ------------------------------------------------ Dummies
D = {"esp32": bx(ex0, ex1, byc - ey, byc + ey, ez, ez + p["esp_t"]),
     "dupont": bx(ex0, ex1 - p["esp_ant"], byc - ey, byc + ey, ez + p["esp_t"], ez + p["esp_t"] + p["esp_above"]),
     "usb_plug": bx(x0 - 25, ex0 - 1.0, byc - 6, byc + 6, usb_zc - 3.5, usb_zc + 3.5),
     "deck_cards": bx(dxi0 + p["clr_card"], dxi1 - p["clr_card"], -p["sc_l"]/2, p["sc_l"]/2, dHi - p["deck_h"] - 0.01, dHi - 0.01),     # volles Deck, von der Feder an die Decke gedrueckt
     "gy_cards": bx(gxi0 + p["clr_card"], gxi1 - p["clr_card"], -p["sc_l"]/2, p["sc_l"]/2, gHi - p["gy_h"] - 0.01, gHi - 0.01),
     "strap_A": bx(p["strapA_x"] - p["strap_w"]/2, p["strapA_x"] + p["strap_w"]/2, -(cy1 + 2.5 + p["strap_t"] - 1), cy1 + 2.5 + p["strap_t"] - 1, 0.3, 2.3)}
PARTS = dict(deck_pocket=deck_pk, gy_pocket=gy_pk, deck_spring=deck_sp, gy_spring=gy_sp, disc_shell=shell, arm_tile=tile, bay=bay, bay_lid=lid, backbone_A=bbA, backbone_B=bbB)
os.makedirs(HERE + "/stl_world", exist_ok=True); os.makedirs(HERE + "/stls", exist_ok=True)
doc = App.newDocument("ARM_DISK_v2_3")
sh = doc.addObject("Spreadsheet::Sheet", "Params")
for i, (k, v) in enumerate(sorted((k, v) for k, v in p.items() if isinstance(v, (int, float)))):
    sh.set("A%d" % (i + 1), k); sh.set("B%d" % (i + 1), str(round(v, 4))); sh.setAlias("B%d" % (i + 1), k)
for n, o in list(PARTS.items()) + [("v28_" + k, v) for k, v in STACK.items()] + [("dummy_" + k, v) for k, v in D.items()]:
    f = doc.addObject("Part::Feature", n); f.Shape = o
doc.recompute(); doc.saveAs(os.path.join(HERE, "ARM-DISK_v2.3.FCStd"))
def mesh(shape, fn):
    m = Mesh.Mesh(); m.addFacets(shape.tessellate(0.05)); m.write(fn)
W = dict(PARTS); W["pin"] = pin
W["deck_spring_one"] = spring((dxi0 + dxi1)/2, SE.F_at(h_for(dHi - 0.67) - 0.1, p["sp_S"], p["sp_R"], p["sp_t"], p["sp_b"]), +1)[0]   # nur fuer das Bild: 1 Karte
W["dummy_deck_one"] = bx(dxi0 + p["clr_card"], dxi1 - p["clr_card"], -p["sc_l"]/2, p["sc_l"]/2, dHi - 0.67, dHi - 0.01)
W.update({"v28_" + k: v for k, v in STACK.items()}); W.update({"dummy_" + k: v for k, v in D.items()})
for n, o in W.items(): mesh(o, "%s/stl_world/%s.stl" % (HERE, n))
def flip(o):
    o = o.copy(); o.rotate(V(0, 0, 0), V(1, 0, 0), 180); return o
def stand(o, ang):
    o = o.copy(); o.rotate(V(0, 0, 0), V(1, 0, 0), ang); return o
TP_ = turntable21.copy()
SF = spring_free.copy(); SF.rotate(V(0, 0, 0), V(0, 1, 0), 90)
PR = {"deck_pocket": stand(deck_pk, 90), "gy_pocket": stand(gy_pk, -90), "card_spring": SF, "v28_turntable": TP_, "disc_shell": flip(shell), "arm_tile": tile, "bay": bay, "bay_lid": flip(lid),
      "backbone_A": flip(bbA), "backbone_B": flip(bbB), "pin": pin}
for n, o in PR.items():
    o = o.copy(); b = o.BoundBox; o.translate(V(-b.XMin, -b.YMin, -b.ZMin)); mesh(o, "%s/stls/%s.stl" % (HERE, n))
for n in ("base", "st_tray", "st_ceiling", "deck", "carrier", "cover"):
    shutil.copy("/workspace/yugioh-ar/disk-v2/stls/%s.stl" % n, "%s/stls/v28_%s.stl" % (HERE, n))
json.dump(dict(p=p, TB=TB, TS=TS, TP=TP, BB=BB, BPIN=BPIN, CB=CB, CP=CP, pw2=pw2, SHS=SHS, RIBS=RIBS, SCR=SCR, PINS=PINS, ex=(ex0, ex1, ey, ez), dxi=(dxi0, dxi1), gxi=(gxi0, gxi1), usb_zc=usb_zc, SPR=SPR),
          open(HERE + "/build_info.json", "w"), indent=1)
print("BUILD OK", {k: [round(v, 1) for v in (o.BoundBox.XLength, o.BoundBox.YLength, o.BoundBox.ZLength)] for k, o in PARTS.items()},
      {k: round(o.Volume / 1000, 1) for k, o in PARTS.items()})
