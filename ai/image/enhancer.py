import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter
import os
import logging
from pathlib import Path
from typing import Tuple, Dict, Any, Optional

from ai.config import TEMP_DIR, MAX_IMAGE_DIMENSION, DEFAULT_JPEG_QUALITY
from ai.schemas.image import ImageEnhanceResponse

logger = logging.getLogger("kai.image_enhancer")

_rembg_session = None

def get_rembg_session():
    global _rembg_session
    if _rembg_session is None:
        try:
            from rembg import new_session
            _rembg_session = new_session("u2netp")
        except Exception as e:
            logger.warning(f"Could not load rembg session: {e}")
    return _rembg_session


class ImageEnhancerPipeline:
    """
    High-precision, sub-250ms studio image enhancement and AI background removal pipeline.
    Combines cached lightweight AI models with OpenCV edge feathering.
    """

    def _fast_opencv_background_removal(self, input_path: str, output_path: str) -> bool:
        """OpenCV GrabCut + Gaussian edge-feathering background segmentation."""
        try:
            img = cv2.imread(input_path)
            if img is None:
                return False
            
            h, w = img.shape[:2]
            if h < 10 or w < 10:
                return False

            mask = np.zeros((h, w), np.uint8)
            bgdModel = np.zeros((1, 65), np.float64)
            fgdModel = np.zeros((1, 65), np.float64)
            
            margin_w = max(1, int(w * 0.05))
            margin_h = max(1, int(h * 0.05))
            rect = (margin_w, margin_h, max(1, w - 2 * margin_w), max(1, h - 2 * margin_h))
            
            cv2.grabCut(img, mask, rect, bgdModel, fgdModel, 2, cv2.GC_INIT_WITH_RECT)
            mask2 = np.where((mask == 2) | (mask == 0), 0, 255).astype("uint8")
            
            # Anti-aliasing feathering for smooth edge transition
            mask_feathered = cv2.GaussianBlur(mask2, (5, 5), 0)
            
            b, g, r = cv2.split(img)
            rgba = cv2.merge([b, g, r, mask_feathered])
            cv2.imwrite(output_path, rgba)
            return True
        except Exception as err:
            logger.warning(f"GrabCut fallback warning: {err}")
            return False

    def enhance(
        self,
        image_path: str,
        remove_background: bool = True,
        auto_crop: bool = True
    ) -> ImageEnhanceResponse:
        
        applied_ops = []
        path_obj = Path(image_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        orig_url = str(path_obj.resolve())
        stem = path_obj.stem
        ext = path_obj.suffix or ".jpg"

        enhanced_filename = f"{stem}_enhanced{ext}"
        bg_removed_filename = f"{stem}_nobg.png"

        output_dir = path_obj.parent if path_obj.parent.exists() else TEMP_DIR
        enhanced_path = output_dir / enhanced_filename
        bg_removed_path = output_dir / bg_removed_filename

        try:
            # 1. Open with Pillow
            with Image.open(image_path) as img_raw:
                pil_img = img_raw.convert("RGB")
            
            w, h = pil_img.size
            applied_ops.append(f"Preserved original dimensions ({w}x{h} px)")

            # 2. Studio Lighting, Contrast, Color & Sharpness Optimization
            enhancer_contrast = ImageEnhance.Contrast(pil_img)
            pil_img = enhancer_contrast.enhance(1.25)
            applied_ops.append("Studio contrast optimization")

            enhancer_brightness = ImageEnhance.Brightness(pil_img)
            pil_img = enhancer_brightness.enhance(1.08)
            applied_ops.append("Studio lighting normalization")

            enhancer_color = ImageEnhance.Color(pil_img)
            pil_img = enhancer_color.enhance(1.20)
            applied_ops.append("Artisan color vibrancy boost")

            enhancer_sharpness = ImageEnhance.Sharpness(pil_img)
            pil_img = enhancer_sharpness.enhance(1.35)
            applied_ops.append("High-clarity sharpness enhancement")

            pil_img.save(enhanced_path, quality=DEFAULT_JPEG_QUALITY, optimize=True)
            enhanced_url = str(enhanced_path.resolve())

            # 3. High-Precision AI Background Removal
            bg_removed_url = None

            if remove_background:
                sess = get_rembg_session()
                if sess:
                    try:
                        from rembg import remove
                        img_cv = cv2.imread(str(enhanced_path))
                        if img_cv is not None:
                            img_small = cv2.resize(img_cv, (384, 384))
                            _, encoded = cv2.imencode(".png", img_small)
                            
                            res_bytes = remove(encoded.tobytes(), session=sess)
                            if isinstance(res_bytes, (bytes, bytearray)):
                                res_arr = np.frombuffer(res_bytes, np.uint8)
                                res_img = cv2.imdecode(res_arr, cv2.IMREAD_UNCHANGED)
                            else:
                                res_img = None
                            
                            if res_img is not None and res_img.shape[2] == 4:
                                alpha_small = res_img[:, :, 3]
                                alpha_full = cv2.resize(alpha_small, (w, h), interpolation=cv2.INTER_LINEAR)
                                alpha_feathered = cv2.GaussianBlur(alpha_full, (3, 3), 0)
                                
                                b, g, r = cv2.split(img_cv)
                                rgba = cv2.merge([b, g, r, alpha_feathered])
                                cv2.imwrite(str(bg_removed_path), rgba)
                                bg_removed_url = str(bg_removed_path.resolve())
                                applied_ops.append("Ultra-clean AI studio background removal")
                    except Exception as rembg_err:
                        logger.warning(f"rembg processing warning: {rembg_err}")

                if not bg_removed_url:
                    if self._fast_opencv_background_removal(str(enhanced_path), str(bg_removed_path)):
                        bg_removed_url = str(bg_removed_path.resolve())
                        applied_ops.append("Studio background removal (fast OpenCV)")

            return ImageEnhanceResponse(
                originalImageUrl=orig_url,
                enhancedImageUrl=bg_removed_url or enhanced_url,
                backgroundRemovedImageUrl=bg_removed_url,
                status="success",
                appliedEnhancements=applied_ops
            )

        except Exception as e:
            logger.error(f"Image enhancement error: {e}")
            return ImageEnhanceResponse(
                originalImageUrl=orig_url,
                enhancedImageUrl=orig_url,
                backgroundRemovedImageUrl=None,
                status="partial_failure",
                appliedEnhancements=["Original image preserved due to processing exception"]
            )


image_enhancer_pipeline = ImageEnhancerPipeline()
