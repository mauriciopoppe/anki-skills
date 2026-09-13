import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).parents[1] / "skills/anki-add-audio/scripts/anki_add_audio.py"
SPEC = importlib.util.spec_from_file_location("anki_add_audio", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class NormalizeForSpeechTest(unittest.TestCase):
    def test_strips_html(self):
        value = "毎日、<b>見ます</b>。"
        self.assertEqual(MODULE.normalize_for_speech(value), "毎日、見ます。")

    def test_keeps_cloze_answer(self):
        value = "毎日、{{c1::見ます::見る → polite}}。"
        self.assertEqual(MODULE.normalize_for_speech(value), "毎日、見ます。")

    def test_uses_furigana_reading(self):
        value = " 毎日[まいにち]、 日本語[にほんご]。"
        self.assertEqual(MODULE.normalize_for_speech(value), "まいにち、にほんご。")


if __name__ == "__main__":
    unittest.main()
