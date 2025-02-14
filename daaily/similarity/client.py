import io
from typing import TYPE_CHECKING

import urllib3

if TYPE_CHECKING:
    import imagehash
    from PIL import Image
else:
    try:
        from PIL import Image
    except ImportError:
        Image = None
    try:
        import imagehash
    except ImportError:
        imagehash = None


http = urllib3.PoolManager()


class Client:
    def __init__(self, threshold: int = 10):
        """ """
        self.threshold = threshold
        self.http = http
        if Image is None or imagehash is None:
            raise ImportError(
                "Some extra dependency is not installed.\n"
                "Please add extra dependency like so:\n\n"
                "#egg=daaily[similarity]\n"
            )

    def _calculate_distance(self, image1: Image.Image, image2: Image.Image) -> int:
        """
        Compute the perceptual hash for two images and compare their similarity.
        """
        hash1 = imagehash.phash(image1)
        hash2 = imagehash.phash(image2)
        distance = hash1 - hash2
        return distance

    def compare_lucy_images(self, image_blob_id: str, image_urls: list[str]):
        blob_name = "/".join(image_blob_id.split("/")[:-1])
        source_image_url = f"https://storage.googleapis.com/{blob_name}"
        resp_source_image = self.http.request("GET", source_image_url)
        if resp_source_image.status != 200:
            raise ValueError("Source image not found.")
        source_image = Image.open(io.BytesIO(resp_source_image.data))
        similarities = {}
        for image_url in image_urls:
            resp = self.http.request("GET", image_url)
            if resp_source_image.status != 200:
                similarities[image_url] = "Image not found."
                continue
            image = Image.open(io.BytesIO(resp.data))
            similarities[image_url] = self._calculate_distance(source_image, image)
        return similarities
