import tempfile
import unittest
from pathlib import Path

from PIL import Image
from advertisement_generator import analyze_inputs, build_design_plan, render_ad


class AdvertisementGeneratorTests(unittest.TestCase):
    def test_fitness_detection(self):
        self.assertEqual(analyze_inputs("PulseFit Protein", "Gym Goers", "bold")["category"], "fitness")

    def test_beauty_detection(self):
        plan = build_design_plan("GlowLeaf Vitamin C Serum", "Young Adults", "premium, clean")
        self.assertEqual(plan.category, "beauty")
        self.assertEqual(plan.visual, "serum")

    def test_education_audience_weighting(self):
        self.assertEqual(build_design_plan("SkillSprint AI Course", "College Students", "sale, bold").category, "education")

    def test_general_fallback(self):
        self.assertEqual(analyze_inputs("Miscellaneous Item", "General Buyers", "fresh concept")["category"], "tech")

    def test_png_output_dimensions(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "sample.png"
            render_ad("PulseFit Protein", "Gym Goers", "bold, modern", path)
            with Image.open(path) as image:
                self.assertEqual(image.size, (1080, 1080))
                self.assertEqual(image.format, "PNG")

    def test_empty_product_raises(self):
        with self.assertRaises(ValueError):
            build_design_plan(" ", "General Buyers", "clean")


if __name__ == "__main__":
    unittest.main()
