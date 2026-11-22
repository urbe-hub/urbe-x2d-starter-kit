"""The hand-off between the two skills: what 3d-print-design writes, x2d-print must read.

Runs the design skill on its two-colour coaster example (with --variants), fills
the job the way x2d-print's SKILL.md says (filament numbers by colour, nozzles from
design.suggested_nozzles), checks it with x2d-print's own job reader, and builds
the .3mf from the design's real STLs with a fake template and fake Bambu Studio
profiles (x2d-print's own test helpers). No Bambu Studio here or in x2d-print's tests
(they use a fake slicer). The .3mf files x2d-print built for the holdout slices in
skills/3d-print-design/references/estimate-calibration.csv were sliced by the real
Bambu Studio 2.09.01.70 command line on the author's Mac; opening them in the Bambu
Studio window was not part of that check.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "skills" / "3d-print-design"
X2D = ROOT / "skills" / "x2d-print"
sys.path.insert(0, str(X2D / "scripts"))
sys.path.insert(0, str(X2D / "tests"))

import bambu_project as bp  # noqa: E402
import test_bambu_project as x2d_helpers  # noqa: E402

# A template as x2d-print reads it: 5 filaments, black is number 5, yellow number 1.
TEMPLATE_COLOURS = {"yellow": 1, "white": 2, "blue": 3, "magenta": 4, "black": 5}
SETTINGS = {
    "filament_settings_id": ["Bambu PLA Basic @BBL X2D"] * 5,
    "filament_type": ["PLA"] * 5,
    "nozzle_diameter": ["0.4", "0.4"],
    "filament_map": ["1"] * 5,
    "layer_height": "0.2",
}


def design_python() -> str:
    venv = DESIGN / ".venv" / "bin" / "python"
    return str(venv) if venv.is_file() else sys.executable


class HandoffTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.project = Path(cls.tmp.name) / "coaster"
        cls.project.mkdir()
        shutil.copy(DESIGN / "examples" / "two-colour-coaster" / "build.py", cls.project / "build.py")
        env = dict(os.environ, PRINT3D_SKILL_DIR=str(DESIGN))
        cls.res = subprocess.run([design_python(), "-P", "build.py", "--variants", "--thin-walls", "0"],
                                 cwd=cls.project, env=env, capture_output=True, text=True, timeout=600)
        cls.job_path = cls.project / "out" / "x2d-job.json"

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def fill(self, option=None):
        """Fill the job as x2d-print's SKILL.md says; `option` picks one of design.nozzle_options."""
        job = json.loads(self.job_path.read_text())
        job["template"] = "template.3mf"
        for obj in job["objects"]:
            for part in obj["parts"]:
                part["filament"] = TEMPLATE_COLOURS[part["colour"]]
        nozzles = job["design"]["suggested_nozzles"]
        if option:
            nozzles = next(o["nozzles"] for o in job["design"]["nozzle_options"] if o["option"] == option)
            job["design"]["suggested_nozzles"] = nozzles
        job["nozzles"] = {str(TEMPLATE_COLOURS[c]): n for c, n in nozzles.items()}
        path = self.job_path.with_name(f"filled-{option or 'suggested'}.json")
        path.write_text(json.dumps(job))
        return path

    def test_design_build_passes_and_writes_format_2(self):
        self.assertEqual(self.res.returncode, 0, self.res.stdout + self.res.stderr)
        job = json.loads(self.job_path.read_text())
        self.assertEqual(job["design"]["format"], 2)
        # the main colour (black) stays on the left nozzle, the fast one; the accent (yellow) goes on
        # the right one: no slower than all left, and less purge
        self.assertEqual(job["design"]["suggested_nozzles"], {"black": "left", "yellow": "right"})
        options = {o["option"]: o for o in job["design"]["nozzle_options"]}
        self.assertEqual(options["accent_right"]["nozzles"], {"black": "left", "yellow": "right"})
        self.assertEqual(options["dominant_right"]["nozzles"], {"black": "right", "yellow": "left"})
        self.assertLessEqual(options["accent_right"]["minutes"], options["all_left"]["minutes"])
        self.assertLess(options["all_left"]["minutes"], options["dominant_right"]["minutes"])
        self.assertEqual({v["name"] for v in job["variants"]}, {"light", "strong"})
        self.assertIn("| light |", self.res.stdout)

    def test_unfilled_job_is_refused_by_x2d_print(self):
        with self.assertRaises(bp.UserError):
            bp.load_job(self.job_path)

    def test_filled_job_reads_in_x2d_print(self):
        job = bp.load_job(self.fill())
        self.assertEqual([p["filament"] for p in job["objects"][0]["parts"]], [5, 1])
        # the suggested plan: yellow (filament 1) on the right nozzle, black (filament 5) left
        self.assertEqual(bp.nozzle_map(job, SETTINGS), ["2", "1", "1", "1", "1"])
        self.assertEqual(job["settings"]["wall_loops"], "3")
        self.assertEqual(bp.nozzle_map(bp.load_job(self.fill("all_left")), SETTINGS), ["1"] * 5)
        # the slow plan: black (filament 5) on the right nozzle, everything else left
        other = bp.load_job(self.fill("dominant_right"))
        self.assertEqual(bp.nozzle_map(other, SETTINGS), ["1", "1", "1", "1", "2"])

    def test_variants_carry_their_settings(self):
        job = bp.load_job(self.fill())
        by = {v["name"]: bp.variant_job(job, v) for v in job["variants"]}
        self.assertEqual(by["light"]["settings"]["wall_loops"], "2")
        self.assertEqual(by["strong"]["settings"]["sparse_infill_density"], "40%")
        self.assertEqual(by["strong"]["settings"]["layer_height"], "0.2")

    def build(self, job):
        """The .3mf x2d-print would write, from a 5-filament fake template."""
        s = x2d_helpers.template_settings(
            filament_settings_id=["PLA A"] * 5, filament_type=["PLA"] * 5,
            filament_colour=["#FFFF00", "#FFFFFF", "#0000FF", "#FF00FF", "#000000"],
            filament_map=["1"] * 5, nozzle_temperature=["220"] * 5,
            textured_plate_temp=["55"] * 5, filament_retraction_length=["0.8"] * 5,
            different_settings_to_system=[""] * 7,
            # the process keys the design skill sets, as a saved Bambu Studio project has them
            layer_height="0.2", sparse_infill_density="15%", top_shell_layers="5",
            bottom_shell_layers="3", enable_support="0")
        paths = x2d_helpers.fake_profiles(Path(self.tmp_profiles.name))  # once per test
        flat = bp.official_code_values(paths, s["printer_settings_id"], s["print_settings_id"],
                                       s["filament_settings_id"])
        report = {"warnings": []}
        data = bp.build_project(job, s, flat, report)
        return zipfile.ZipFile(io.BytesIO(data)), report

    def setUp(self):
        self.tmp_profiles = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp_profiles.cleanup()

    def test_design_stls_become_a_3mf(self):
        job = bp.load_job(self.fill())
        z, report = self.build(job)
        names = set(z.namelist())
        for entry in (bp.SETTINGS_ENTRY, bp.MODEL_ENTRY, "Metadata/model_settings.config"):
            self.assertIn(entry, names)
        for name in names:
            if name.endswith((".model", ".rels", ".xml", "model_settings.config")):
                ET.fromstring(z.read(name))
        meshes = b"".join(z.read(n) for n in names if n.endswith(".model"))
        self.assertGreater(meshes.count(b"<triangle "), 100, "the coaster's triangles are missing")
        s = json.loads(z.read(bp.SETTINGS_ENTRY))
        # filament_map: one entry per template filament, "1" = left nozzle, "2" = right
        want = ["1"] * 5
        for colour, nozzle in job["design"]["suggested_nozzles"].items():
            want[TEMPLATE_COLOURS[colour] - 1] = "1" if nozzle == "left" else "2"
        self.assertEqual(s["filament_map"], want)
        self.assertEqual(s["wall_loops"], "3")
        ms = z.read("Metadata/model_settings.config").decode()
        for part in job["objects"][0]["parts"]:   # each part keeps its filament
            self.assertIn(f'key="extruder" value="{part["filament"]}"', ms)

    def test_two_separate_objects_of_different_colours(self):
        x2d_helpers.write_box_stl(self.project / "out" / "a.stl", 0, 0, 0, 60, 60, 4)
        x2d_helpers.write_box_stl(self.project / "out" / "b.stl", 0, 0, 0, 60, 60, 4)
        job = json.loads(self.fill().read_text())
        job["objects"] = [{"name": "a", "parts": [{"stl": "a.stl", "filament": 5}]},
                          {"name": "b", "parts": [{"stl": "b.stl", "filament": 1}]}]
        job["nozzles"] = {"5": "right", "1": "left"}
        job.pop("variants", None)
        path = self.job_path.with_name("two.json")
        path.write_text(json.dumps(job))
        z, report = self.build(bp.load_job(path))
        ms = z.read("Metadata/model_settings.config").decode()
        self.assertEqual(ms.count("<object "), 2)
        self.assertIn('key="extruder" value="5"', ms)
        self.assertIn('key="extruder" value="1"', ms)
        self.assertIn('key="filament_maps" value="1 1 1 1 2"', ms)
        s = json.loads(z.read(bp.SETTINGS_ENTRY))
        self.assertEqual(s["filament_map"], ["1", "1", "1", "1", "2"])

    def test_design_and_template_agree(self):
        for option in (None, "all_left", "dominant_right"):
            job = bp.load_job(self.fill(option))
            warnings = bp.design_warnings(job, dict(SETTINGS, **job["settings"]), bp.nozzle_map(job, SETTINGS))
            self.assertEqual(warnings, [], (option, warnings))

    def test_other_nozzle_plan_builds(self):
        job = bp.load_job(self.fill("dominant_right"))
        z, report = self.build(job)
        s = json.loads(z.read(bp.SETTINGS_ENTRY))
        self.assertEqual(s["filament_map"], ["1", "1", "1", "1", "2"])


if __name__ == "__main__":
    unittest.main()
