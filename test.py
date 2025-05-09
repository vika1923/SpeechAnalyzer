import unittest
from typing import Dict, List, Tuple
from pdf import create_pdf
class TestCreatePDF(unittest.TestCase):
    def test_create_pdf_output(self):
        word_count = 150
        parts_of_speech: Dict[str, int] = {"noun": 50, "verb": 40, "adjective": 20, "other": 40}
        rate_of_speech_points: List[Tuple[float, float]] = [(0.0, 2.0), (1.0, 2.5), (2.0, 2.2)]
        volume_points: List[Tuple[float, float]] = [(0.0, 60.0), (1.0, 58.0), (2.0, 62.0)]

        create_pdf( word_count, parts_of_speech, rate_of_speech_points, volume_points, )

if __name__ == "__main__":
    unittest.main()
