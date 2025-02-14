import unittest
from io import BytesIO
from unittest import mock

import imagehash
from PIL import Image

from daaily.similarity.client import Client


class DummyResponse:
    def __init__(self, data, status=200):
        self.data = data
        self.status = status


class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = Client(threshold=10)
        self.mock_image_data = BytesIO(b"fake_image_data")
        self.mock_image = Image.new("RGB", (100, 100))

    def test_compare_lucy_images(self):
        # Mock the HTTP responses
        mock_http_request = mock.MagicMock()
        mock_http_request.return_value = DummyResponse(
            self.mock_image_data.getvalue(), 200
        )

        # Mock the Image.open method
        mock_image_open = mock.MagicMock()
        mock_image_open.return_value = self.mock_image

        # Mock the imagehash.phash method
        mock_phash = mock.MagicMock()
        mock_phash.side_effect = [
            imagehash.phash(self.mock_image),  # Source image hash
            imagehash.phash(self.mock_image),  # Mocked image 1 hash
            imagehash.phash(self.mock_image),  # Mocked image 2 hash
            imagehash.phash(self.mock_image),  # Mocked image 3 hash
            imagehash.phash(self.mock_image),  # Mocked image 4 hash
            imagehash.phash(self.mock_image),  # Mocked image 5 hash
            imagehash.phash(
                self.mock_image
            ),  # Mocked image 6 hash (extra to avoid StopIteration)
        ]

        # Replace the actual methods with mocks
        self.client.http.request = mock_http_request
        Image.open = mock_image_open
        imagehash.phash = mock_phash

        image_blob_id = "some/blob/id/source_image.jpg"
        image_urls = [
            "http://example.com/image1.jpg",
            "http://example.com/image2.jpg",
            "http://example.com/image3.jpg",
            "http://example.com/image4.jpg",
            "http://example.com/image5.jpg",
        ]

        similarities = self.client.compare_lucy_images(image_blob_id, image_urls)

        # Verify the HTTP requests
        self.assertEqual(mock_http_request.call_count, 6)

        # Verify the Image.open calls
        self.assertEqual(mock_image_open.call_count, 6)

        # Verify the imagehash.phash calls
        self.assertEqual(mock_phash.call_count, 6)

        # Verify the similarities dictionary
        for url in image_urls:
            self.assertIn(url, similarities)
            self.assertEqual(
                similarities[url], 0
            )  # Since all images are the same, distance should be 0


if __name__ == "__main__":
    unittest.main()
