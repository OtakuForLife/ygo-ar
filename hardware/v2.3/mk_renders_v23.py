import subprocess, os, json
from PIL import Image, ImageDraw, ImageFont
H = "/workspace/yugioh-ar/arm-disk/v2.3"; os.makedirs(H + "/renders", exist_ok=True); os.chdir(H + "/renders")
C = {"deck_spring_one": "[0.85,0.25,0.2]", "deck_pocket": "[0.15,0.35,0.75]", "deck_spring": "[0.85,0.25,0.2]", "dummy_deck_cards": "[0.95,0.9,0.75]", "dummy_deck_one": "[0.95,0.9,0.75]"}
def scene(name, parts, alpha={}, extra=""):
    L = ['color(%s) difference(){ import("%s/stl_world/%s.stl"); translate([-95,-200,-50]) cube([400,400,200]); }' % (C[n], H, n) for n in parts]
    open("_%s.scad" % name, "w").write("\n".join(L) + extra)
def render(name, png, cam, size="1000,800"):
    r = subprocess.run("xvfb-run -a /workspace/bin/openscad --imgsize=%s --colorscheme=Tomorrow --projection=p --camera=%s -o %s _%s.scad" % (size, cam, png, name), shell=True, capture_output=True, text=True)
    if r.returncode: print(png, r.stderr[-300:])
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
scene("full", ["deck_pocket", "deck_spring", "dummy_deck_cards"], {"deck_pocket": 0.35})
render("full", "_full.png", "40,-30,60,-103,0,26")
scene("one", ["deck_pocket", "deck_spring_one", "dummy_deck_one"], {"deck_pocket": 0.35})
render("one", "_one.png", "40,-30,60,-103,0,26")
a, b = Image.open("_full.png").convert("RGB"), Image.open("_one.png").convert("RGB")
o = Image.new("RGB", (2000, 980), "white"); o.paste(a, (0, 170)); o.paste(b, (1000, 170)); d = ImageDraw.Draw(o)
d.text((16, 10), "ARM-DISK v2.3 – Kartenhalt ohne Tor und ohne Rast (Schnitt längs durch die Deck-Hülse, Öffnung rechts)", fill=(20, 20, 20), font=ImageFont.truetype(FB, 28))
for i, l in enumerate(["Bogenfeder (rot) drückt den Stapel von unten an die Decke, die Halte-Kante am Dach sperrt die oberste Karte. Zum Ziehen drückt man den Stapel durch den Griffausschnitt nach unten.",
                       "Links: volles Deck (60 Karten, 6,0 N Federkraft) · rechts: eine einzelne Karte (0,61 N, bleibt an der Decke) · Dehnung der Feder höchstens 1,0 %",
                       "Die Friedhof-Hülse ist genauso aufgebaut, nur hinten offen und 30 mm hoch."]):
    d.text((16, 48 + 28 * i), l, fill=(70, 70, 70), font=ImageFont.truetype(F, 20))
fo = ImageFont.truetype(FB, 21)
d.text((20, 132), "Links: volles Deck, Feder fast flach", fill=(150, 30, 20), font=fo)
d.text((1020, 132), "Rechts: eine Karte, Feder fast frei", fill=(150, 30, 20), font=fo)
o.save("01_kartenhalt_feder.png"); os.remove("_full.png"); os.remove("_one.png"); print("ok")
