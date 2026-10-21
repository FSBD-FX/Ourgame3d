"""Regression: a moving weapon must not resize an otherwise rigid character."""
from pathlib import Path
import importlib.util
import unittest
from PIL import Image, ImageDraw

spec = importlib.util.spec_from_file_location("shared_fit", Path(__file__).parents[1] / "scripts/extract-sprite-shared-row-scale.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class SharedFit(unittest.TestCase):
    def test_rigid_body_keeps_height_when_weapon_changes_full_bbox(self):
        parts = []
        for weapon_width in (200, 160, 120, 180):
            image = Image.new("RGBA", (weapon_width, 100))
            draw = ImageDraw.Draw(image)
            draw.rectangle((0, 0, 39, 99), fill=(180, 150, 120, 255))
            draw.rectangle((39, 45, weapon_width - 1, 54), fill=(100, 100, 100, 255))
            parts.append(image)
        frames, record = module.fit_components_shared(parts, 128, 128, 14, 14)
        self.assertEqual(record["scale"], .5)
        self.assertEqual([r["shared_scale"] for r in record["frame_records"]], [.5] * 4)
        self.assertEqual([im.getbbox()[3] - im.getbbox()[1] for im in frames], [50] * 4)
        self.assertFalse(record["per_frame_scale_normalization"])
        # The former per-pose fit made heights50/62/83/56 for this same rigid body.
        legacy_heights = [round(100 * min(100 / p.width, 1)) for p in parts]
        self.assertNotEqual(legacy_heights, [50] * 4)

    def test_native_body_height_changes_are_preserved_not_hidden(self):
        parts = [Image.new("RGBA", (200, h), (180, 150, 120, 255)) for h in (100, 120)]
        frames, record = module.fit_components_shared(parts, 128, 128, 14, 14)
        self.assertEqual([im.getbbox()[3] - im.getbbox()[1] for im in frames], [50, 60])
        self.assertEqual(record["scale"], .5)

    def test_rejects_empty_component_instead_of_fallback(self):
        with self.assertRaisesRegex(ValueError, "Empty"):
            module.fit_components_shared([Image.new("RGBA", (128, 128))], 128, 128, 14, 14)


if __name__ == "__main__":
    unittest.main()
