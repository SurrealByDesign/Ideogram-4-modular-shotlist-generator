import unittest

from shotplanner.bbox import validate_bbox


class BBoxTests(unittest.TestCase):
    def test_validate_bbox_accepts_normalized_coordinates(self):
        validate_bbox([0, 10, 1000, 990])

    def test_validate_bbox_rejects_invalid_coordinates(self):
        invalid_boxes = [
            [-1, 0, 100, 100],
            [0, 0, 1001, 100],
            [100, 0, 100, 100],
            [0, 200, 100, 200],
            [0, 0, 100],
        ]
        for bbox in invalid_boxes:
            with self.subTest(bbox=bbox):
                with self.assertRaises(ValueError):
                    validate_bbox(bbox)


if __name__ == "__main__":
    unittest.main()
