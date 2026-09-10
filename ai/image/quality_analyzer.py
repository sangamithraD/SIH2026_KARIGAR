import cv2
import numpy as np
from PIL import Image
import logging
from typing import Tuple, List, Dict, Any
from ai.config import BLUR_THRESHOLD, UNDEREXPOSED_THRESHOLD, OVEREXPOSED_THRESHOLD
from ai.schemas.image import ImageAnalysisResponse

logger = logging.getLogger("kai.image_analyzer")

class PhotoQualityAnalyzer:
    """
    Evaluates photographic quality using OpenCV and Pillow.
    Evaluates photo technical parameters (lighting, focus, resolution), NOT the physical product quality.
    """

    def analyze(self, image_path_or_bytes: Any) -> ImageAnalysisResponse:
        score = 100
        issues: List[str] = []
        suggestions: List[str] = []
        meta: Dict[str, Any] = {}

        try:
            # Read image using OpenCV and PIL
            pil_img = None
            if isinstance(image_path_or_bytes, str):
                img_cv = cv2.imread(image_path_or_bytes)
                with Image.open(image_path_or_bytes) as img_open:
                    pil_img = img_open.copy()
            elif isinstance(image_path_or_bytes, bytes):
                nparr = np.frombuffer(image_path_or_bytes, np.uint8)
                img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                import io
                with Image.open(io.BytesIO(image_path_or_bytes)) as img_open:
                    pil_img = img_open.copy()
            else:
                if isinstance(image_path_or_bytes, Image.Image):
                    pil_img = image_path_or_bytes
                    img_cv = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                else:
                    img_cv = image_path_or_bytes
                    pil_img = Image.fromarray(cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB))

            if img_cv is None:
                raise ValueError("Could not decode image file")

            height, width = img_cv.shape[:2]
            meta["resolution"] = f"{width}x{height}"
            meta["pixels"] = width * height

            # 1. Resolution Check
            if width < 800 or height < 600:
                score -= 15
                issues.append("Image resolution is low.")
                suggestions.append("Take the photo at a higher resolution (at least 800x600 px) for crisp detail.")

            # 2. Brightness Check (Grayscale mean)
            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            mean_brightness = float(np.mean(gray))
            meta["brightness"] = round(mean_brightness, 1)

            if mean_brightness < UNDEREXPOSED_THRESHOLD:
                score -= 20
                issues.append("Image appears underexposed (dark lighting).")
                suggestions.append("Move to a well-lit area or use natural daylight when photographing your product.")
            elif mean_brightness > OVEREXPOSED_THRESHOLD:
                score -= 20
                issues.append("Image appears overexposed (bright glare).")
                suggestions.append("Avoid harsh direct glare or flash reflections on the product surface.")

            # 3. Blur Check (Laplacian variance)
            laplacian_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
            meta["blur_score"] = round(laplacian_var, 1)

            if laplacian_var < BLUR_THRESHOLD:
                score -= 25
                issues.append("Image appears blurry or out of focus.")
                suggestions.append("Hold your camera steady or rest it on a surface to ensure sharp focus.")

            # 4. Background Clutter Check (Peripheral standard deviation)
            h_margin = int(height * 0.1)
            w_margin = int(width * 0.1)
            border_top = gray[:h_margin, :]
            border_bottom = gray[-h_margin:, :]
            border_left = gray[:, :w_margin]
            border_right = gray[:, -w_margin:]

            border_pixels = np.concatenate([
                border_top.flatten(), border_bottom.flatten(),
                border_left.flatten(), border_right.flatten()
            ])
            border_std = float(np.std(border_pixels))
            meta["background_clutter_std"] = round(border_std, 1)

            if border_std > 55.0:
                score -= 15
                issues.append("Background contains clutter or multiple objects.")
                suggestions.append("Place your product against a simple, plain background (such as a plain sheet).")

            # Final Score clamp
            score = max(10, min(100, score))
            if score >= 80 and not suggestions:
                suggestions.append("Great photograph! The image is crisp, well-lit, and ready for marketplace enhancement.")

            return ImageAnalysisResponse(
                score=score,
                issues=issues,
                suggestions=suggestions,
                metadata=meta
            )

        except Exception as e:
            logger.warning(f"Error during photo quality analysis: {e}")
            return ImageAnalysisResponse(
                score=75,
                issues=["Could not fully evaluate photograph metrics."],
                suggestions=["Ensure the image file is valid and clear."],
                metadata={"error": str(e)}
            )

photo_quality_analyzer = PhotoQualityAnalyzer()
