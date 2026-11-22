# Multicolour best practices (X2D and AMS)

Why it matters: every time the same nozzle changes colour, the printer cuts the filament,
loads the next one and pushes out ("flushes") the old colour before printing again. The
flushed plastic is waste. On a small multicolour part the waste can weigh more than the
part.

## The numbers

- A colour change on the same nozzle wastes roughly **0.35 to 0.5 g** with default flush
  volumes; dark to light costs more than light to dark.
- Bambu's wiki example: a 4-colour cube with **153 changes flushed about 80 g** for
  about 11 g of model.
- On the X2D a **nozzle switch** (left to right) needs no flush, only a short prime. In
  Notebookcheck's test the same multicolour Benchy wasted about 70 g with one nozzle and
  about 20 g with both.
- What this skill measured on a 78 x 24 x 3 mm plaque, black base on the right nozzle and
  four small symbols in the first 4 layers on the left nozzle: 12 changes, about 4.7 g of
  model, about 6.3 g of purge and prime tower, 44 minutes.
- What this skill measured in Bambu Studio 02.09.01.70 (sliced, not printed; Generic PLA,
  0.2 mm layers) on a hollow 60 mm ball of 14.4 g with a logo inlay in 111 of its 357
  layers: one colour 59 min; **logo on the right nozzle 1 h 47 min and 28.5 g** (14.2 g
  of purge); body on the right nozzle 2 h 13 min and the same grams; both colours on the
  left nozzle 4 h 48 min and 87.8 g (73.5 g of purge).
- From the same run, on three objects: using both nozzles costs about 4.5 minutes once,
  then about 24 s and 0.1 g for each layer with a nozzle switch. A swap on the same
  nozzle costs about 2 minutes and 0.55 to 0.75 g, depending on the colour pair.

## Rules, most important first

1. **Count changes, not colours.** Waste grows with (layers that hold several colours on
   the same nozzle) x (colours per layer). Ask: in how many layers do the colours meet?
2. **Colours by height when you can.** If every layer holds a single colour (a base,
   then lettering on top, then an accent), each plate has a fixed number of changes
   (colours minus one), whatever the number of copies. Keep all colours on the left
   nozzle then: moving one to the right nozzle saves a single change, and the right
   nozzle is the slower one (up to 200 mm/s, acceleration up to 1000 mm/s²), meant by
   Bambu mainly for supports. A single STL whose colours change only by height does not
   even need splitting: in Bambu Studio's Preview, right-click the layer slider at the
   first layer of each new colour and choose **Change Filament**.
3. **Two nozzles when the colours meet in many layers: main colour left, accent right.**
   Switching nozzle costs almost no purge, so split the colours across the two nozzles.
   Which one goes where matters: the left nozzle (direct drive, fed by the AMS) is the
   fast one. In Bambu Studio's X2D process the right nozzle (Bowden, external spool)
   prints outer walls at 50 mm/s against 200 mm/s and accelerates at 1,000 mm/s² against
   10,000. So the **main colour** (body, base: most of the plastic) stays in the AMS on
   the left nozzle and the **accent** goes on the external spool and the right nozzle.
   Measured on three objects with the two colours swapped: the same purge, and 1 %, 18 %
   and 24 % more time with the body on the right nozzle (a block with a stripe, a coaster
   with an inlay, the hollow ball above). The check says so when a two-colour job has its
   main colour on the right nozzle. Exceptions: TPU never goes on the right nozzle; with
   three or more colours, if two accents would then swap on the left nozzle in many
   layers, the main colour alone on the right nozzle can win: build both jobs with
   `--check` and compare. The right nozzle cannot reach a 20.5 mm strip at the left edge
   of the plate and prints 5 mm lower, so parts on it need that margin.
4. **Keep accent colours in few layers.** Inlays face down on the plate (the first 3 to 5
   layers, and the face against the plate comes out smooth) or on top. A colour that
   runs the full height of a part on the same nozzle as another colour costs a change on
   every layer.
5. **Do not alternate colours on the same nozzle without need.** Two objects with
   different colours on one plate, sharing layers and the same nozzle, alternate on every
   layer. Print them on separate plates (one 3MF each), or put their colours on different
   nozzles.
6. **Group copies.** Several copies of the same multicolour part on one plate share each
   colour change: waste per part drops. The script builds one copy of each object; to
   fill the plate, the person selects the object in Bambu Studio, adds copies with `+`
   and presses **Arrange** (`A`), which keeps clear of the prime tower. Time and grams
   then grow beyond the guide's numbers, the number of changes much less.
7. **Thicker layers, fewer changes.** 0.24 or 0.28 mm instead of 0.20 cuts the number of
   layers, and so the changes, for parts where detail is not critical. Measured on the
   hollow ball (logo on the right nozzle): 0.28 mm layers took 1 h 23 min and 24.9 g
   instead of 1 h 47 min and 28.5 g. In the job: `"layer_height": "0.28"`.
8. **One material per print.** PLA with PETG (or other mixes) bond poorly and need
   different temperatures. Mixing is for experts (soluble or breakaway supports).
9. **Dark to light is the expensive change.** Going from black to white needs much more
   flush than white to black. Bambu Studio orders the colours inside each layer to save
   flush, but white or yellow details sharing a nozzle with a dark colour still cost the
   most: that pair is the first to split across the two nozzles.
10. **Prime tower: on, except for a few colour changes by height.** The tower wipes the
    nozzle and steadies its pressure after a change. It is always printed **from the first
    layer up to the layer of the last colour change**, even when there is only one change
    and it sits at the top: a lettering or logo on the last layers of a 20 mm part makes a
    20 mm tower. Measured on a 20.7 mm cap with a logo in the last 6 layers (one change at
    layer 107 of 112, one nozzle): with the tower 6.8 g in all (3.2 g of model, 3.6 g of
    purge, tower about 6 min) and 25 min 33 s; without it 3.8 g (0.7 g of flush) and 23 min
    42 s. So when the colours change **only by height, on one nozzle, at most 3 times, high
    up** (the check's advice says so), set `"enable_prime_tower": "0"` in the job's
    `settings` and tell the person why. The flush still goes into the purge chute; the cost
    is at most a small blob or a thin start on the first layer of the new colour. Keep the
    tower with nozzle switches (it primes the nozzle that was idle), with colours that meet
    in many layers, and on a first multicolour print where looks matter most. A change in
    the first few layers makes a short tower: leave it. Smooth-mode timelapse also builds a
    tower, as tall as the part, even with one colour. **Flush into support** is on by
    default; **flush into infill** is fine only for opaque parts where the mixed colour
    hidden inside does not matter, and does nothing on a hollow part or a thin shell,
    which has no infill to take it.
    **A lighter tower with two nozzles:** `"prime_volume_mode": "Saving"` in the job's
    `settings` primes less on each tower layer. Measured on the hollow ball (logo on the
    right nozzle, 111 switches): 1 h 36 min and 23.2 g (8.8 g of purge) instead of
    1 h 47 min and 28.5 g (14.2 g); with 0.28 mm layers as well, 1 h 17 min and 21.3 g
    (7.1 g of purge). These are slices, not prints: offer it for a second print, once
    the first came out clean, and say that the first line after a switch may be thinner.
    Turning the tower off with nozzle switches gave 1 h 20 min and no purge at all, but
    then nothing primes the nozzle that was idle: do not do it. A narrower tower
    (`prime_tower_width` 20) and the Arachne wall generator changed nothing here.
11. **Flush multiplier stays at 1.0.** 0.8 to 0.9 can be tested on a scrap print once the
    person knows what colour bleeding looks like; never on a first print. In the job it
    is a list with one value per nozzle, `"flush_multiplier": ["0.8", "0.8"]` (a single
    value is refused). It is a small lever next to the nozzle plan: the hollow ball with
    both colours on the left nozzle at 0.8 still took 4 h 25 min and 75.7 g, against
    1 h 47 min and 28.5 g on two nozzles at 1.0.
12. **Zero flush option:** print each colour as a separate part and glue them.
13. **Hollow and light parts feel the purge most.** A thin shell weighs little, so the
    tower and the flushes can double its filament (the ball: 14.4 g of model, 14.2 g of
    purge). In order of effect: fewer layers where the colours meet (a lower logo, an
    inlay near the top or the bottom), the nozzle plan (rule 3), thicker layers (rule 7),
    the lighter tower (rule 10).

## Flush volumes after opening a project

Bambu Studio recalculates flush volumes when the AMS is synced or a colour is changed, if
"Auto calculate flush volume" is on in Preferences (the default). After opening the 3MF
and pressing Sync, the flush table matches the loaded colours. If the person changed a
colour by hand, the "Flushing volumes" button next to the filament list has a
re-calculate option.

## Beginner traps

- **Wrong AMS slot mapping** in the send dialog: the print comes out in the wrong colours.
  Check every line before Send.
- **Wet filament** (crackling, stringing, rough surface): dry it; PLA left out for weeks
  in a humid room is enough.
- **Cardboard spools** in the AMS shed fibres and can slip: use a spool adapter or reel
  the filament onto a plastic spool.
- **TPU and carbon fibre (CF)**: not in the AMS 2 Pro for soft TPU; TPU never on the X2D
  right nozzle. Check Bambu's AMS FAQ before loading anything but PLA, PETG, ABS, ASA.
- **Parts that do not touch the plate**: each colour part must rest on the plate or on
  another part. A thin colour layer "floating" on top of nothing will fail.

## What the check's advice means

| Advice | Meaning | Usual fix |
|---|---|---|
| swaps on the same nozzle in N of M layers | colours alternate through much of the height | move the accent to the other nozzle, keep accents in few layers, or split plates |
| all colours use the left nozzle, put filament N on the other | given only with swaps in many layers (rule 3); colours that change only by height stay on the left nozzle (rule 2) | accent on the external spool and the right nozzle, main colour in the AMS |
| the main colour is on the right nozzle | two colours on two nozzles, the larger one on the slow nozzle (rule 3) | swap them: main colour in the AMS (left nozzle), the other on the external spool |
| purge more than the part | normal on small parts | fewer colours or colour layers, or several copies per plate |
| several objects share the plate | objects make each other change colour | one plate (one 3MF) per object group |
| different materials | poor bonding | one material |
| prime tower off | risky colour changes (not given for a few changes by height on one nozzle) | turn it on |
| prime tower printed up to layer N for only K changes | colours change only by height, high up: the tower is mostly waste | `"enable_prime_tower": "0"` in the job's settings, rebuild |

## Sources

- Reduce waste during filament change (Bambu wiki): https://wiki.bambulab.com/en/software/bambu-studio/reduce-wasting-during-filament-change
- Prime tower (Bambu wiki): https://wiki.bambulab.com/en/software/bambu-studio/parameter/prime-tower
- Filament sequence for different layers (Bambu wiki): https://wiki.bambulab.com/en/software/bambu-studio/parameter/filament-sequence-for-different-layers
- Dual nozzle filament grouping (Bambu wiki): https://wiki.bambulab.com/en/software/bambu-studio/manual/dual-nozzles-slicing-filament-grouping
- View slicing information (Bambu wiki): https://wiki.bambulab.com/en/software/bambu-studio/view-slicing-information
- AMS notes and AMS 2 Pro / HT FAQ (Bambu wiki): https://wiki.bambulab.com/en/knowledge-sharing/notes-ams and https://wiki.bambulab.com/en/ams/manual/ams-2-pro-ams-ht-faq
- Notebookcheck, X2D dual nozzle and waste: https://www.notebookcheck.net/Bambu-Lab-X2D-in-detail-Dual-nozzle-halves-printing-time-and-drastically-reduces-waste.1319597.0.html
- Notebookcheck, X2D Combo review: https://www.notebookcheck.net/Bambu-Lab-X2D-Combo-review-Dual-nozzle-3D-printer-tested.1311491.0.html
- X2D direct drive and auxiliary extrusion (Bambu blog): https://blog.bambulab.com/two-extruders-one-purpose-what-is-x2d-direct-drive-extrusion-and-auxiliary-extrusion/
- UNBC Spark Lab, multicolour printing: https://sparklab.unbc.ca/?p=714
- Flushing volumes guide: https://www.3dprofilefix.com/guides/flushing-volumes-guide.html
- X2D Bambu Studio settings: https://printer-hub.ru/posts/bambu-lab-x2d-bambu-studio-settings
- Forum, flushing volume calibration: https://forum.bambulab.com/t/ams-flushing-volumes-calibration-purge-reduction/37062
- Bambu Studio issues on automatic grouping with two nozzles (why the script uses Custom Mode, `filament_map_mode` `Manual`; both still open in Bambu Studio 02.09.01.70, November 2026): https://github.com/bambulab/BambuStudio/issues/13020 and https://github.com/bambulab/BambuStudio/issues/12915
- Bambu Studio source for the layer slider's "Change Filament" and the X2D's per-nozzle printable area: https://github.com/bambulab/BambuStudio (`src/slic3r/GUI/IMSlider.cpp`, `resources/profiles/BBL/machine/Bambu Lab X2D 0.4 nozzle.json`)
