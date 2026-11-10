import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import lexicon  # noqa: E402

EXAMPLE = os.path.join(ROOT, "examples", "lexicon.example.json")
SCRIPT = os.path.join(ROOT, "scripts", "lexicon.py")


def good_entry(**over):
    e = {"name": "whip pan", "field": "camera", "means": "A pan so fast the frame smears into streaks.",
         "tell": "Motion blur hides the picture for a few frames.", "not": ["pan"],
         "knobs": ["direction", "frames of blur"], "ask": "Whip pan to the right over 6 frames."}
    e.update(over)
    return e


class CheckTests(unittest.TestCase):
    def test_example_lexicon_is_clean(self):
        self.assertEqual(lexicon.check(lexicon.load(EXAMPLE)), [])

    def test_missing_field_reported(self):
        e = good_entry()
        del e["tell"]
        self.assertTrue(any("missing 'tell'" in p for p in lexicon.check([e])))

    def test_single_knob_rejected(self):
        self.assertTrue(any("at least 2 knobs" in p for p in lexicon.check([good_entry(knobs=["speed"])])))

    def test_no_lookalike_flagged(self):
        e = good_entry()
        del e["not"]
        self.assertTrue(any("look-alike" in p for p in lexicon.check([e])))

    def test_contrast_counts_as_lookalike(self):
        e = good_entry(contrast="Unlike a pan, the picture is unreadable mid-move.")
        del e["not"]
        self.assertEqual(lexicon.check([e]), [])

    def test_ask_without_knob_value_flagged(self):
        probs = lexicon.check([good_entry(ask="Do a whip pan here.")])
        self.assertTrue(any("sets no knob" in p for p in probs))

    def test_circular_definition_flagged(self):
        probs = lexicon.check([good_entry(means="A whip pan done quickly.")])
        self.assertTrue(any("itself" in p for p in probs))

    def test_duplicate_alias_flagged(self):
        a = good_entry(aliases=["swish"])
        b = good_entry(name="swish pan", aliases=["swish"], means="Fast blurry pan.")
        self.assertTrue(any("already used" in p for p in lexicon.check([a, b])))

    def test_load_accepts_bare_list(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as fh:
            json.dump([good_entry()], fh)
        try:
            self.assertEqual(len(lexicon.load(fh.name)), 1)
        finally:
            os.unlink(fh.name)


class FindTests(unittest.TestCase):
    def setUp(self):
        self.entries = lexicon.load(EXAMPLE)

    def top(self, q):
        hits = lexicon.find(self.entries, q)
        return hits[0][1] if hits else None

    def test_english_description(self):
        self.assertEqual(self.top("the camera floats around the cup"), "orbit")

    def test_chinese_description(self):
        self.assertEqual(self.top("文字从线后面冒出来"), "mask reveal")

    def test_alias_hit(self):
        self.assertEqual(self.top("push in"), "dolly in")

    def test_sound_field(self):
        self.assertEqual(self.top("music gets quieter when talking"), "sidechain duck")

    def test_no_match(self):
        self.assertEqual(lexicon.find(self.entries, "zzzz qqqq"), [])

    def test_stopwords_do_not_score(self):
        self.assertEqual(lexicon.find(self.entries, "the of and"), [])


class LintTests(unittest.TestCase):
    def setUp(self):
        self.entries = lexicon.load(EXAMPLE)

    def test_fog_only_is_vague(self):
        r = lexicon.lint("Make the intro smooth and cinematic.")
        self.assertEqual(r["verdict"], "VAGUE")
        self.assertIn("smooth", r["fog"])

    def test_chinese_fog_is_vague(self):
        r = lexicon.lint("标题要有高级感，丝滑一点")
        self.assertEqual(r["verdict"], "VAGUE")
        self.assertIn("高级感", r["fog"])
        self.assertNotIn("高级", r["fog"])

    def test_name_without_knobs_is_named(self):
        r = lexicon.lint("Use a dolly in on the product.", self.entries)
        self.assertEqual(r["verdict"], "NAMED")
        self.assertIn("dolly in", r["named"])

    def test_name_with_knobs_is_measured(self):
        r = lexicon.lint("Mask reveal the title from below, 0.6 s, ease-out.", self.entries)
        self.assertEqual(r["verdict"], "MEASURED")

    def test_chinese_measured(self):
        r = lexicon.lint("推镜到手部特写，4秒，缓入缓出", self.entries)
        self.assertEqual(r["verdict"], "MEASURED")

    def test_numbers_drowned_in_fog_stay_named(self):
        r = lexicon.lint("2 s of something punchy and premium")
        self.assertEqual(r["verdict"], "NAMED")

    def test_measured_without_lexicon(self):
        r = lexicon.lint("Slide the card in from the left over 300 ms.")
        self.assertEqual(r["verdict"], "MEASURED")

    def test_word_boundary(self):
        r = lexicon.lint("popcorn on a cooler shelf")
        self.assertEqual(r["fog"], [])


class CliTests(unittest.TestCase):
    def run_cli(self, *args, stdin=None):
        return subprocess.run([sys.executable, SCRIPT, *args], input=stdin, capture_output=True, text=True)

    def test_check_exit_zero(self):
        self.assertEqual(self.run_cli("check", EXAMPLE).returncode, 0)

    def test_lint_exit_codes(self):
        self.assertEqual(self.run_cli("lint", "-", stdin="make it pop").returncode, 2)
        self.assertEqual(self.run_cli("lint", "-", "--lexicon", EXAMPLE, stdin="orbit the cup").returncode, 1)
        self.assertEqual(self.run_cli("lint", "-", "--lexicon", EXAMPLE, stdin="orbit 90° right, 5 s").returncode, 0)

    def test_lint_json(self):
        out = self.run_cli("lint", "-", "--json", stdin="smooth").stdout
        self.assertEqual(json.loads(out)["verdict"], "VAGUE")

    def test_usage(self):
        self.assertEqual(self.run_cli().returncode, 3)


if __name__ == "__main__":
    unittest.main()
