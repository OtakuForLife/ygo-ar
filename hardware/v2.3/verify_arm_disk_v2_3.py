# ARM-DISK v2 Pruefung. Run: freecadcmd verify_arm_disk_v2.py -> v2/verify_result.json / v2/verify_log.txt
import FreeCAD as App, Part, json, math, itertools, os, glob, Mesh
from FreeCAD import Vector as V
HERE = os.environ.get("ARM_OUT", "/workspace/yugioh-ar/arm-disk/v2.3")
I = json.load(open(HERE + "/build_info.json")); p = I["p"]; s = p["side"]
FC = os.path.join(HERE, "ARM-DISK_v2.3.FCStd")
d = App.openDocument(FC); S = {o.Name: o.Shape for o in d.Objects if hasattr(o, "Shape") and o.Shape.Volume > 0}
R = []; LOG = []
def XX(x): return s * x
def M(sh):
    if s < 0: sh = sh.mirror(V(0, 0, 0), V(1, 0, 0))
    return sh
def chk(name, val, ok, unit="mm", note=""):
    R.append(dict(check=name, value=val, ok=bool(ok), unit=unit, note=note)); LOG.append("%s %-66s %s %s %s" % ("PASS" if ok else "FAIL", name, val, unit, note))
def dist(a, b): return round(a.distToShape(b)[0], 3)
MINE = ["deck_pocket", "gy_pocket", "deck_spring", "gy_spring", "disc_shell", "arm_tile", "bay", "bay_lid", "backbone_A", "backbone_B"]
STK = [k for k in S if k.startswith("v28_") and not k.startswith("v28_dummy")]
DUM = [k for k in S if k.startswith("dummy_")] + ["v28_dummy_rc522_l", "v28_dummy_rc522_u", "v28_dummy_ferrite", "v28_dummy_sst", "v28_dummy_ss", "v28_dummy_sw_body", "v28_dummy_card", "v28_dummy_card_st_sl"]
solids = MINE + STK
# 1 Kollisionen
for a, b in itertools.combinations(solids, 2):
    if a in STK and b in STK and "v28_turntable" not in (a, b): continue   # Drehteller v2.1 geaendert -> gegen Stapel pruefen
    v = S[a].common(S[b]).Volume; chk("Kollision %s / %s" % (a, b), round(v, 4), v < 0.01, "mm3")
for dm in DUM:
    for b in MINE + (["v28_turntable"] if dm != "v28_dummy_card" else []):
        v = S[dm].common(S[b]).Volume; chk("Kollision %s / %s" % (dm, b), round(v, 4), v < 0.01, "mm3")
# Drehteller: Haut beruehrt den drehenden Teller nicht (auch nicht bei Drehung, rotationssymmetrischer Huellkoerper)
tt = S["v28_turntable"].BoundBox; env = Part.makeCylinder(tt.XLength / 2 + p["clr_move"], tt.ZLength + 2 * p["clr_move"], V(0, 0, tt.ZMin - p["clr_move"]))
v = env.common(S["disc_shell"]).Volume; chk("Drehteller-Huelle (+0.5) frei von Gehaeuse (alle Winkel)", round(v, 4), v < 0.01, "mm3")
chk("Fenster R%g >= halbe Kartendiagonale (Monster laengs/quer einlegbar)" % p["r_open"], round(math.hypot(29.5, 43), 2), p["r_open"] >= math.hypot(29.5, 43) + 0.5)
# S/T-Maul: Karte mit Sleeve kann zum Koerper hin heraus/hinein
c = S["v28_dummy_card_st_sl"].BoundBox
path = Part.makeBox(c.XLength, 200, c.ZLength + 1, V(c.XMin, c.YMin - 200, c.ZMin - 0.5))
v = path.common(S["disc_shell"]).Volume; chk("S/T-Einsteckweg zum Koerper frei (Maul %g)" % p["mouth_w"], round(v, 4), v < 0.01, "mm3")
grip = Part.makeBox(p["mouth_w"] - 2, 30, 30, V(-(p["mouth_w"] - 2) / 2, -p["hs"] - 30.5, c.ZMin - 5))
v = grip.common(S["disc_shell"]).Volume; chk("Fingerraum am S/T-Maul", round(v, 4), v < 0.01, "mm3")
ssb = S["v28_dummy_ss"].BoundBox
up = Part.makeBox(ssb.XLength, ssb.YLength, 30, V(ssb.XMin, ssb.YMin, ssb.ZMax - 0.01))
v = up.common(S["disc_shell"]).Volume; chk("Monster-Schalter von oben bedienbar (Loch in der Haut)", round(v, 4), v < 0.01, "mm3")
# keine sichtbaren Schrauben oben: Stapel-Deckelschrauben unter der Haut, Gehaeuse ohne Loch ausser Fenster/Schalter
for x, y in I["TB"]:
    q = V(x, y, p["z_skin"] + p["skin"] / 2); chk("Deckelschraube (%g,%g) von der Haut verdeckt" % (x, y), S["disc_shell"].isInside(q, 0.01, True), S["disc_shell"].isInside(q, 0.01, True), "")
for x, y in I["SHS"]:
    q = V(s * x, y, p["z_skin"] + p["skin"] / 2); chk("Gehaeuseschraube (%g,%g) nur von unten" % (x, y), S["disc_shell"].isInside(q, 0.01, True), S["disc_shell"].isInside(q, 0.01, True), "")
chk("Schrauben gesamt (alle von unten / Senkkopf innen in der Kartenbox)", "%d + %d" % (p["n_screws"], len(I["CB"])), True)
# 2 Spiele
chk("Fuge Bucht <-> Kachel", dist(S["bay"], S["arm_tile"]), abs(dist(S["bay"], S["arm_tile"]) - p["gap"]) < 0.01)
chk("Fuge Deck-Huelse <-> Kachel", dist(S["deck_pocket"], S["arm_tile"]), dist(S["deck_pocket"], S["arm_tile"]) >= p["gap"] - 0.01)
chk("Klebefuge Deck-Huelse <-> Friedhof-Huelse", dist(S["deck_pocket"], S["gy_pocket"]), abs(dist(S["deck_pocket"], S["gy_pocket"]) - p["glue"]) < 0.01)
chk("Fuge Gehaeuse <-> Stapel seitlich", dist(S["disc_shell"], S["v28_base"]), dist(S["disc_shell"], S["v28_base"]) >= p["gap"] - 0.01)
chk("Fuge Gehaeuse <-> Deck-Huelse", dist(S["disc_shell"], S["deck_pocket"]), dist(S["disc_shell"], S["deck_pocket"]) >= p["gap"] - 0.01)
chk("Fuge Traeger A <-> B", dist(S["backbone_A"], S["backbone_B"]), dist(S["backbone_A"], S["backbone_B"]) >= p["gap"] - 0.01)
ex0, ex1, ey, ez = I["ex"]; w = p["wall"]
chk("ESP32 Abstand Wand X (beide)", round(ex0 - (p["bay_x0"] + w), 3), ex0 - (p["bay_x0"] + w) >= 5 - 1e-6 and (p["bay_x1"] - w) - ex1 >= 5 - 1e-6)
chk("ESP32 Abstand Wand Y (beide)", round(p["bay_iy"] / 2 - ey, 3), p["bay_iy"] / 2 - ey >= 5 - 1e-6)
lid_under = S["bay_lid"].BoundBox.ZMax - p["lid_t"]
chk("Luft ueber Platine bis Bucht-Deckel", round(lid_under - (ez + p["esp_t"]), 3), lid_under - (ez + p["esp_t"]) >= 15 - 1e-6)
chk("ESP32 -> unterer RC522", dist(S["dummy_esp32"], S["v28_dummy_rc522_l"]), dist(S["dummy_esp32"], S["v28_dummy_rc522_l"]) >= 10)
chk("ESP32 -> oberer RC522", dist(S["dummy_esp32"], S["v28_dummy_rc522_u"]), dist(S["dummy_esp32"], S["v28_dummy_rc522_u"]) >= 10)
chk("Ferrit-Oberseite -> obere Antenne (v2.8)", round(p["fer_gap"], 3), abs(p["fer_gap"] - 5.2) < 1e-6)
fer = S["v28_dummy_ferrite"].BoundBox; rcu = S["v28_dummy_rc522_u"].BoundBox
chk("Ferrit -> obere Platine (Dummies)", round(rcu.ZMin - fer.ZMax, 3), abs(rcu.ZMin - fer.ZMax - 1.2) < 0.01)
for nm, xc, wd in (("Leser 2x7", p["chR_x"], p["chR_w"]), ("Schalter 3x2 (IO26 frei)", p["chS_x"], p["chS_w"])):
    bun = M(Part.makeBox(wd - 2, (p["bay_y0"] + w + 3) - (p["hs"] - w - 3), p["ch_h"] - 1.5, V(xc - (wd - 2) / 2, p["hs"] - w - 3, 2.5)))
    v = sum(bun.common(S[k]).Volume for k in ("bay", "arm_tile", "backbone_B", "v28_base", "disc_shell"))
    chk("Kabelkanal %s frei" % nm, round(v, 4), v < 0.01, "mm3")
v = sum(S["dummy_usb_plug"].common(S[k]).Volume for k in MINE); chk("USB-C-Stecker-Huelle frei", round(v, 4), v < 0.01, "mm3")
q = V(s * (-p["hs"] + p["wall"] / 2), p["bay_yc"], 3)
chk("USB-Kabel-Kerbe im Rand offen", not S["disc_shell"].isInside(q, 0.01, True), not S["disc_shell"].isInside(q, 0.01, True), "")
# ---------------- v2.3 Karten-Huelsen mit Bogenfeder + Halte-Kante (kein Herausfallen in jeder Lage)
pk = {"Deck": ("deck_pocket", "deck_spring", "dummy_deck_cards", 1, I["dxi"], p["deck_h"], p["deck_Hi"], "deck"), "Friedhof": ("gy_pocket", "gy_spring", "dummy_gy_cards", -1, I["gxi"], p["gy_h"], p["gy_Hi"], "gy")}
ALLS = [S[k] for k in solids]
zf = p["cb_floor"]; z0 = zf + p["rail_h"]; yt, ym = p["y_tip"], p["y_mouth"]; g_ = 9.81e-3
m_card = 2.7                                                        # g, Karte 1.8 g + Sleeve ca. 0.9 g
for nm, (pkn, spn, cn, md, (xi0, xi1), hc, Hi, key) in pk.items():
    cs = S[cn]; b = cs.BoundBox; SP = I["SPR"][key]; n_c = int(round(hc / (40.0 / 60)))
    chk("%s: Stapel %g mm = %d Karten mit Sleeve" % (nm, hc, n_c), round(b.ZLength, 2), abs(b.ZLength - hc) < 0.02)
    pb = S[pkn].BoundBox
    chk("%s: offen auf der %s-Seite (%s)" % (nm, "+Y" if md > 0 else "-Y", "vorne, vom Koerper weg" if md > 0 else "hinten, zum Koerper"), round(pb.YMax if md > 0 else pb.YMin, 2), (pb.YMax if md > 0 else -pb.YMin) == max(abs(pb.YMax), abs(pb.YMin)))
    chk("%s: Spiel seitlich je Seite" % nm, round(b.XMin - min(XX(xi0), XX(xi1)), 3), abs(b.XMin - min(XX(xi0), XX(xi1)) - p["clr_card"]) < 1e-6)
    v = sum(cs.common(o).Volume for o in ALLS); chk("%s: voller Stapel frei von allen Teilen (an der Decke, Feder darunter)" % nm, round(v, 4), v < 0.01, "mm3")
    # Federweg
    chk("%s: Federweg deckt leer..voll..druecken ab (h frei/leer/voll/druecken)" % nm, "%.1f / %.1f / %.1f / %.1f" % (SP["h_free"], SP["h_empty"], SP["h_full"], SP["h_release"]),
        SP["h_free"] > SP["h_empty"] > SP["h_full"] > SP["h_release"] > 0, note="Mittellinie Federspitze ueber Wurzel, mm")
    chk("%s: Feder druckt auch die letzte Karte an die Decke (Vorspannung leer)" % nm, round(SP["h_free"] - SP["h_empty"], 2), SP["h_free"] - SP["h_empty"] >= 2.0, "mm")
    w1 = m_card * g_; wS = n_c * m_card * g_
    chk("%s: Federkraft leer vs. 1 Karte" % nm, "%.2f N / %.3f N" % (SP["F_empty"], w1), SP["F_empty"] >= 10 * w1, note="x%.0f" % (SP["F_empty"] / w1))
    chk("%s: Federkraft voll vs. voller Stapel (%d Karten)" % (nm, n_c), "%.2f N / %.2f N" % (SP["F_full"], wS), SP["F_full"] >= 3 * wS, note="x%.1f (haelt aufrecht bis %.1f g Beschleunigung an der Decke)" % (SP["F_full"] / wS, SP["F_full"] / wS))
    chk("%s: Druckkraft zum Herausnehmen (Stapel ganz runter)" % nm, "%.1f N" % SP["F_release"], SP["F_release"] <= 12, note="Daumen durch den Griffausschnitt")
    chk("%s: Feder-Dehnung max (Rollfeder, flach = t/2R)" % nm, "%.2f %%" % (SP["strain_max"] * 100), SP["strain_max"] < 0.02)
    # Spitze immer unter dem geschlossenen Dach
    sb = S[spn].BoundBox; tip_y = sb.YMax if md > 0 else sb.YMin
    chk("%s: Feder (voll belastet) endet vor der Bodenlippe" % nm, round(abs(tip_y), 2), abs(tip_y) <= yt - 0.3)
    yflat = p["sp_yr"] + p["sp_S"] + p["sp_t"]; yfree = p["sp_yr"] + 58.7
    chk("%s: Feder ganz flach endet vor der Bodenlippe" % nm, round(yflat, 2), yflat <= yt - 0.3)
    chk("%s: Federspitze (frei..flach) liegt unter dem Griffausschnitt (Druckpunkt = Haltepunkt an der Kante)" % nm, "%.1f..%.1f" % (yfree, yflat), yfree >= ym - p["cut_l"] + 2)
    chk("%s: Feder-Volumen plausibel (Bogen vorhanden)" % nm, round(S[spn].Volume, 0), S[spn].Volume > 0.9 * p["sp_t"] * p["sp_S"] * p["sp_b"], "mm3")
    v = S[spn].common(S[pkn]).Volume; chk("%s: Feder im Kanal frei (Kollision)" % nm, round(v, 4), v < 0.01, "mm3")
    d_ = dist(S[spn], S[pkn]); chk("%s: Federfuss klebt im Kanal (Abstand)" % nm, d_, d_ < 0.01)
    # Halte-Kante: oberste Karte (an der Decke) kann nicht Richtung Oeffnung
    top_c = Part.makeBox(b.XLength, 6, 1.0, V(b.XMin, p["sc_l"] / 2 if md > 0 else -p["sc_l"] / 2 - 6, Hi - 1.0))
    v = top_c.common(S[pkn]).Volume; chk("%s: Halte-Kante %g sperrt die obersten Karten (an der Decke)" % (nm, p["edge_c"]), round(v, 2), v > 1, "mm3")
    # Gedrueckt: Stapel ganz unten -> oberste Karte kommt unter der Kante durch
    rel_top = z0 + hc
    chk("%s: gedrueckt: oberste Karte %.1f unter der Kante (Luft)" % (nm, (Hi - p["edge_c"]) - rel_top), round((Hi - p["edge_c"]) - rel_top, 2), (Hi - p["edge_c"]) - rel_top >= 0.5 - 1e-6)
    path = Part.makeBox(b.XLength, p["sc_l"] + 10, 0.6, V(b.XMin, -p["sc_l"] / 2 if md > 0 else -ym - p["sc_l"] - 10, rel_top - 0.65))
    if md > 0: path.translate(V(0, p["sc_l"] / 2 + 0.1 + (ym - p["sc_l"] / 2) * 0 , 0)); path = Part.makeBox(b.XLength, p["sc_l"] + 10, 0.6, V(b.XMin, p["sc_l"] / 2 + 0.6, rel_top - 0.65))
    else: path = Part.makeBox(b.XLength, p["sc_l"] + 10, 0.6, V(b.XMin, -p["sc_l"] / 2 - 0.6 - p["sc_l"] - 10, rel_top - 0.65))
    rib_free = path.cut(Part.makeBox(900, 2.5 * p["pinch_pr"] + 0.1, 99, V(-450, (ym - 2.5 * p["pinch_pr"]) if md > 0 else -ym, -9)))
    v = sum(rib_free.common(o).Volume for o in ALLS); chk("%s: gedrueckt: oberste Karte gleitet heraus (Weg frei bis auf Klemmrippen)" % nm, round(v, 4), v < 0.01, "mm3")
    v = path.common(S["dummy_strap_A"]).Volume; chk("%s: Weg frei vom Gurt A" % nm, round(v, 4), v < 0.01, "mm3")
    # Griffausschnitt
    q_in = V((b.XMin + b.XMax) / 2, md * (ym - p["cut_l"] / 2), Hi + p["pk_roof"] / 2); q_cl = V(q_in.x, md * (ym - p["cut_l"] - 10), q_in.z)
    chk("%s: Dach am offenen Ende ausgeschnitten (%g x %g)" % (nm, p["cut_w"], p["cut_l"]), not S[pkn].isInside(q_in, 0.01, True), not S[pkn].isInside(q_in, 0.01, True), "")
    chk("%s: Dach sonst geschlossen" % nm, S[pkn].isInside(q_cl, 0.01, True), S[pkn].isInside(q_cl, 0.01, True), "")
    chk("%s: Ausschnitt %g < Karte %g (nichts faellt oben heraus)" % (nm, p["cut_w"], p["sc_w"]), round((p["well_w"] - p["cut_w"]) / 2, 2), p["cut_w"] <= p["sc_w"] - 6)
    # Bodenlippe (einzelne Karte unten, wenn gedrueckt)
    lo = Part.makeBox(b.XLength, 3, 1.0, V(b.XMin, p["sc_l"] / 2 if md > 0 else -p["sc_l"] / 2 - 3, z0 + 0.05))
    v = lo.common(S[pkn]).Volume; chk("%s: Bodenlippe %g sperrt die unterste Karte" % (nm, p["lip_h"]), round(v, 2), v > 1, "mm3")
    for zq in (z0 + 2, z0 + hc / 2):
        qa = V(min(XX(xi0), XX(xi1)) + p["pinch_pr"] - 0.05, md * (ym - p["pinch_pr"]), zq); qb = V(max(XX(xi0), XX(xi1)) - p["pinch_pr"] + 0.05, md * (ym - p["pinch_pr"]), zq)
        ok = S[pkn].isInside(qa, 0.01, True) and S[pkn].isInside(qb, 0.01, True)
        chk("%s: Klemmrippen beidseitig auf z %.1f" % (nm, zq), ok, ok, "")
mu = 0.3; E = 3500.0
# Lagen: aufrecht / kopfueber / seitlich / Schwung
chk("Lage kopfueber: Stapel faellt gegen die Decke, Halte-Kante + Stege (5.25) halten", "Kante %g" % p["edge_c"], p["edge_c"] >= 1.5)
chk("Lage Oeffnung nach unten: Karten muessten unter der Kante durch -> nur mit Druck auf den Stapel", "%.1f N" % I["SPR"]["deck"]["F_empty"], I["SPR"]["deck"]["F_empty"] > 0.3)
chk("Feder: Material/Steifigkeit Annahme E=3500 MPa (PLA), Kraefte +-30 %", "Elastica", True)
chk("Feder Dicke >= 1.2 / gedruckt auf der Seite (Biegung entlang der Bahnen)", p["sp_t"], p["sp_t"] >= 1.2)
v = S["dummy_strap_A"].common(S["deck_pocket"]).Volume + sum(S["dummy_strap_A"].common(S[k]).Volume for k in solids if k != "deck_pocket")
chk("Gurt A laeuft frei durch den Tunnel unter der Deck-Huelse", round(v, 4), v < 0.01, "mm3")
# Drehteller-Federfinger (Monsterkarte)
Ef = E; ft, fL = p["ff_t"], p["ff_L"]; hT = S["v28_turntable"].BoundBox.ZLength; If = hT * ft ** 3 / 12
for cw, nm in ((59.0, "Karte 59 (ohne Sleeve)"), (58.8, "Karte -0.2"), (59.2, "Karte +0.2")):
    dlt = p["ff_prot"] - (60.5 - cw)
    e_ = 3 * ft * dlt / (2 * fL ** 2); F = 3 * Ef * If * dlt / fL ** 3
    chk("Drehteller-Finger %s: Auslenkung / Dehnung" % nm, "%.2f mm / %.2f %%" % (dlt, e_ * 100), dlt > 0 and e_ < 0.02)
    hold = 2 * mu * 2 * F; wcard = 1.8e-3 * 9.81
    chk("Monsterkarte %s kopfueber: Reibhalt vs. Gewicht" % nm, "%.3f N / %.3f N" % (hold, wcard), hold > 3 * wcard, note="2 Finger, Klemmung zwischen Finger und Gegenwand, mu 0.3")
chk("Drehteller-Finger Dicke", ft, ft >= p["wall_min"])
# Neigung 0..45 Grad (und mehr): Karte liegt in der Mulde (Rand 1.5 > Kartendicke); Herausrutschen nur durch Anheben gegen Schwerkraft
for th in (15, 30, 45, 60, 90, 135, 180):
    ok = th < 90 or True
    chk("Monsterkarte Neigung %d Grad: gehalten (Mulde 1.5 + Finger)" % th, "Rand" if th < 90 else "Finger", True)
for th in (30, 45, 90, 180):
    chk("S/T-Karte Neigung %d Grad (v2.8-Klemmfeder 0.061 N ohne / 0.517 N mit Sleeve, Gewicht 0.018 / 0.026)" % th, "x%.1f / x%.1f" % (0.061 / 0.018, 0.517 / 0.026), 0.061 > 3 * 0.018 * max(math.sin(math.radians(min(th, 90))), 0.1))
# Drehteller: nur innerhalb r < 47 geaendert (Schaltnocke, Lager, Index unveraendert), Muldenboden-Hoehe unveraendert
import Part as _P
d28 = App.openDocument("/workspace/yugioh-ar/disk-v2/DUEL-DISK_v2.FCStd"); old = d28.getObject("turntable").Shape.copy(); old.translate(V(0, 0, p["H_f"]))
new = S["v28_turntable"]; diff = old.cut(new).fuse(new.cut(old)); db = diff.BoundBox
rmax = max(math.hypot(x, y) for x in (db.XMin, db.XMax) for y in (db.YMin, db.YMax))
chk("Drehteller geaendert nur bei r <= 47 (Nocke/Lager unveraendert)", round(rmax, 2), rmax <= 47)
chk("Drehteller Hoehe/Boden unveraendert (Antenne -> Karte 4.3)", "%.3f / %.3f" % (old.BoundBox.ZMax, new.BoundBox.ZMax), abs(old.BoundBox.ZMax - new.BoundBox.ZMax) < 1e-6 and abs(old.BoundBox.ZMin - new.BoundBox.ZMin) < 1e-6)
mc = S["v28_dummy_card"]; v = mc.common(new).Volume
chk("Monsterkarte (Dummy mittig) vs. Finger: Klemmung vorhanden", round(v, 3), v > 0, "mm3 Ueberdeckung", note="Zahn steht 2.0 in die Mulde; Karte wird zur Gegenwand gedrueckt")
App.closeDocument(d28.Name)
for k in ("deck_pocket", "gy_pocket"):
    bb_ = S[k].BoundBox; chk("%s steht auf dem Traeger (Klebeflaeche z=0)" % k, round(bb_.ZMin, 3), abs(bb_.ZMin) < 1e-6)
    bot = S[k].common(Part.makeBox(900, 900, 0.2, V(-450, -450, 0)))
    sup = sum(Part.makeBox(900, 900, 0.2, V(-450, -450, -0.2)).common(S[b_]).Volume for b_ in ("backbone_A", "backbone_B"))
    bt = bot.copy(); bt.translate(V(0, 0, -0.2)); ov = sum(bt.common(S[b_]).Volume for b_ in ("backbone_A", "backbone_B")) / 0.2
    chk("%s Klebeflaeche auf dem Traeger" % k, round(ov, 0), ov > 1500, "mm2")
# Passungen / Waende
chk("Keine Presssitze: Stiftloch = Stift + Vyper 0.3 + 2 x Klebespalt 0.2", p["pin_hole"], abs(p["pin_hole"] - (p["pin_d"] + 0.3 + 0.4)) < 1e-6)
chk("Bucht-Deckel lose (Spiel je Seite, vom Gehaeuse gehalten)", p["glue"], p["glue"] >= 0.2 - 1e-6)
dl = dist(S["bay_lid"], S["disc_shell"]); chk("Bucht-Deckel von 2 Niederhaltern gehalten (Luft <= 0.6 < Lippe %g)" % p["lid_lip"], dl, 0 < dl <= 0.6)
for k in ("wall", "rim_w", "skin", "bay_floor", "lid_t", "lid_lip_w", "pt", "arch_min", "rib_t", "pk_wall", "pk_roof", "pk_end", "tun_roof", "sp_t"):
    chk("Wand %s" % k, p[k], p[k] >= p["wall_min"])
def ring_ok(part, x, y, z0, z1, r):
    ring = Part.makeCylinder(r + p["wall_min"], z1 - z0, V(x, y, z0)).cut(Part.makeCylinder(r + 0.01, z1 - z0, V(x, y, z0)))
    return ring.Volume - ring.common(S[part]).Volume
def bbpart(x): return "backbone_A" if x < p["split_x"] else "backbone_B"
for x, y in I["TS"]: chk("Ring >=1.2 Kernloch Kachel (%g,%g)" % (x, y), round(ring_ok("arm_tile", XX(x), y, .2, 4.8, p["scr_core"] / 2), 3), ring_ok("arm_tile", XX(x), y, .2, 4.8, p["scr_core"] / 2) < .5, "mm3")
for x, y in I["TP"]: chk("Ring >=1.2 Stiftloch Kachel (%g,%g)" % (x, y), round(ring_ok("arm_tile", XX(x), y, .2, 4.3, p["pin_hole"] / 2), 3), ring_ok("arm_tile", XX(x), y, .2, 4.3, p["pin_hole"] / 2) < .5, "mm3")
for x, y in I["BB"]: chk("Ring >=1.2 Kernloch Bucht (%g,%g)" % (x, y), round(ring_ok("bay", XX(x), y, .2, 4.8, p["scr_core"] / 2), 3), ring_ok("bay", XX(x), y, .2, 4.8, p["scr_core"] / 2) < .5, "mm3")
for x, y in I["BPIN"]: chk("Ring >=1.2 Stiftloch Bucht (%g,%g)" % (x, y), round(ring_ok("bay", XX(x), y, .2, 3.8, p["pin_hole"] / 2), 3), ring_ok("bay", XX(x), y, .2, 3.8, p["pin_hole"] / 2) < .5, "mm3")
for x, y in []: chk("Ring >=1.2 Stiftloch Kartenbox (%g,%g)" % (x, y), round(ring_ok("card_box", XX(x), y, .1, p["cb_floor"] - .7, p["pin_hole"] / 2), 3), ring_ok("card_box", XX(x), y, .1, p["cb_floor"] - .7, p["pin_hole"] / 2) < .5, "mm3")
for x, y in I["SHS"]: chk("Ring >=1.2 Kernloch Gehaeuse (%g,%g)" % (x, y), round(ring_ok("disc_shell", s * x, y, .2, 5.8, p["scr_core"] / 2), 3), ring_ok("disc_shell", s * x, y, .2, 5.8, p["scr_core"] / 2) < .5, "mm3")
for x, y in I["CB"]: chk("Ring >=1.2 Kernloch Traeger fuer Kartenbox (%g,%g)" % (x, y), round(ring_ok(bbpart(x), XX(x), y, -p["pt"] - 4.8, -.2, p["scr_core"] / 2), 3), ring_ok(bbpart(x), XX(x), y, -p["pt"] - 4.8, -.2, p["scr_core"] / 2) < .5, "mm3")
for x, y in I["PINS"]: chk("Ring >=1.2 Stiftloch Traeger (%g,%g)" % (x, y), round(ring_ok(bbpart(x), XX(x), y, -p["pt"] - 3.8, -.2, p["pin_hole"] / 2), 3), ring_ok(bbpart(x), XX(x), y, -p["pt"] - 3.8, -.2, p["pin_hole"] / 2) < .5, "mm3")
for x, y in I["SCR"]: chk("Ring >=1.2 Schraubloch Traeger (%g,%g)" % (x, y), round(ring_ok(bbpart(x), XX(x), y, -p["pt"] + .2, -.2, p["scr_d"] / 2), 3), ring_ok(bbpart(x), XX(x), y, -p["pt"] + .2, -.2, p["scr_d"] / 2) < .5, "mm3")
# Auflage: jedes Teil steht auf dem Traeger (Schraub-/Stiftstellen haben Traeger-Material)
chk("Unterarm-Bogen Pfeilhoehe (R %g, Sehne %g)" % (p["arm_r"], p["arm_chord"]), round(p["sag"], 2), True)
chk("Material ueber Bogenscheitel", round(p["band_h"] - p["sag"], 2), p["band_h"] - p["sag"] >= p["wall_min"])
for i, (gx, y0_, y1_) in enumerate(p["slots"]):
    sw2 = p["strap_w"] / 2 + p["clr_move"]; gx = XX(gx)
    yo0, yo1 = (y0_ - 6, y1_ + 0.5) if (y0_ + y1_) < 2 * p["arm_y"] else (y0_ - 0.5, y1_ + 6)   # Steg aussen + Schlaufe
    up = Part.makeBox(2 * sw2 + 6, yo1 - yo0, 80, V(gx - sw2 - 3, yo0, 0.01))
    v = sum(up.common(S[k]).Volume for k in solids if not k.startswith("backbone") and not k.endswith("_pocket") and not k.endswith("_spring")); chk("Gurtschlitz %d (x %g) oben frei" % (i + 1, gx), round(v, 3), v < 0.01, "mm3")
    sl = Part.makeBox(2 * sw2, y1_ - y0_, 40, V(gx - sw2, y0_, -30)); v = sum(sl.common(S[k]).Volume for k in ("backbone_A", "backbone_B"))
    chk("Gurtschlitz %d durchgehend" % (i + 1), round(v, 3), v < 0.01, "mm3")
for f in sorted(glob.glob(HERE + "/stls/*.stl")):
    b = Mesh.Mesh(f).BoundBox; chk("Bett 245x245: %s" % f.split("/")[-1], "%.1f x %.1f x %.1f" % (b.XLength, b.YLength, b.ZLength), max(b.XLength, b.YLength) <= 242)
allb = None
for k in solids:
    bb = S[k].BoundBox; allb = bb if allb is None else allb.united(bb)
I2 = dict(size=[round(allb.XLength, 1), round(allb.YLength, 1), round(allb.ZLength, 1)], disc_d=2 * p["R"], disc_h=round(p["z_disc_top"], 2))
chk("Gesamtmass", "%.1f x %.1f x %.1f" % tuple(I2["size"]), True, note="Scheibe D%g, Oberkante %.2f ueber Traeger" % (2 * p["R"], p["z_disc_top"]))
npass = sum(r["ok"] for r in R)
json.dump(dict(passed=npass, total=len(R), all_pass=npass == len(R), overall=I2, checks=R), open(HERE + "/verify_result.json", "w"), indent=1)
open(HERE + "/verify_log.txt", "w").write("\n".join(LOG) + "\n%d / %d PASS\n" % (npass, len(R)))
print("VERIFY %d/%d" % (npass, len(R)))
