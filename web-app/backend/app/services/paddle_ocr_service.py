"""
PaddleOCR Service for real text extraction from images
"""
import os
import logging
from typing import Optional, List, Tuple
import numpy as np
import unicodedata
import re

logger = logging.getLogger(__name__)

try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    logger.warning("PaddleOCR not available")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    logger.warning("OpenCV not available for image preprocessing")

class PaddleOCRService:
    """PaddleOCR service for actual text extraction"""
    
    def __init__(self):
        self.ocr = None
        if PADDLE_AVAILABLE:
            try:
                # Initialize PaddleOCR with optimized settings for Japanese text
                # Use 'japan' for better mixed English/Japanese support
                self.ocr = PaddleOCR(
                    lang='japan',  # Supports both English and Japanese
                    det_db_thresh=0.1,  # Lower threshold for better detection of Japanese text
                    det_db_box_thresh=0.3,  # Lower box threshold for better text region detection
                    det_db_unclip_ratio=1.8,  # Increase unclip ratio for better text boundaries
                    rec_batch_num=1,  # Process one at a time for better accuracy
                    use_angle_cls=True,  # Enable angle classification for rotated text
                    cls_thresh=0.9,  # High threshold for angle classification
                    use_gpu=False,  # Use CPU for compatibility
                    show_log=False,  # Disable verbose logging
                    drop_score=0.3  # Lower drop score to include more text
                )
                logger.info("PaddleOCR initialized successfully with multi-language support")
            except Exception as e:
                logger.error(f"Failed to initialize PaddleOCR: {e}")
                self.ocr = None
    
    def preprocess_image(self, image_path: str) -> Optional[np.ndarray]:
        """
        Preprocess image for better OCR accuracy
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Preprocessed image as numpy array or None if preprocessing fails
        """
        if not CV2_AVAILABLE:
            logger.warning("OpenCV not available, skipping image preprocessing")
            return None
        
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                return None
            
            # Convert to grayscale if colored
            if len(img.shape) == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray = img
            
            # Apply adaptive thresholding for better text contrast
            # This helps with low contrast and uneven lighting
            processed = cv2.adaptiveThreshold(
                gray, 
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,  # Block size
                2    # Constant subtracted from mean
            )
            
            # Denoise
            denoised = cv2.medianBlur(processed, 3)
            
            # Apply morphological operations to connect broken text
            kernel = np.ones((1, 1), np.uint8)
            morphed = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
            
            # Increase image size for better OCR (especially for small Japanese text)
            height, width = morphed.shape
            if width < 1000 or height < 1000:
                scale = max(1000 / width, 1000 / height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                morphed = cv2.resize(morphed, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            
            return morphed
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {e}")
            return None
    
    def normalize_japanese_text(self, text: str) -> str:
        """
        Normalize Japanese text for better consistency
        
        Args:
            text: Raw text from OCR
            
        Returns:
            Normalized text
        """
        if not text:
            return text
        
        # Normalize unicode characters (全角/半角の統一など)
        normalized = unicodedata.normalize('NFKC', text)
        
        # Fix common OCR mistakes in Japanese
        replacements = {
            # Common katakana mistakes
            'ー': 'ー',  # 長音記号の統一
            '―': 'ー',  # ダッシュを長音記号に
            '–': 'ー',  # en dashを長音記号に
            '力': 'カ',  # 漢字の「力」がカタカナの「カ」と誤認識される
            '夕': 'タ',  # 漢字の「夕」がカタカナの「タ」と誤認識される
            '工': 'エ',  # 漢字の「工」がカタカナの「エ」と誤認識される
            '二': 'ニ',  # 漢字の「二」がカタカナの「ニ」と誤認識される
            'ロ': 'ロ',  # 漢字の「口」がカタカナの「ロ」と誤認識される
            
            # Common punctuation fixes
            '、': '、',  # 読点の統一
            '。': '。',  # 句点の統一
            '·': '・',  # 中黒の統一
            '•': '・',  # ビュレットを中黒に
            '．': '.',  # 全角ピリオドを半角に
            '，': ',',  # 全角カンマを半角に
            
            # Quotation marks
            '"': '"',
            '"': '"',
            ''': "'",
            ''': "'",
        }
        
        # コンテキストに基づく修正（カタカナ語の中の誤認識）
        if re.search(r'[ァ-ヴ]', normalized):  # カタカナが含まれている場合
            # カタカナ語の中の漢字をカタカナに修正
            normalized = re.sub(r'(?<=[ァ-ヴ])力(?=[ァ-ヴ])', 'カ', normalized)
            normalized = re.sub(r'(?<=[ァ-ヴ])夕(?=[ァ-ヴ])', 'タ', normalized)
            normalized = re.sub(r'(?<=[ァ-ヴ])工(?=[ァ-ヴ])', 'エ', normalized)
            normalized = re.sub(r'(?<=[ァ-ヴ])二(?=[ァ-ヴ])', 'ニ', normalized)
            normalized = re.sub(r'(?<=[ァ-ヴ])口(?=[ァ-ヴ])', 'ロ', normalized)
        
        # Apply replacements
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)
        
        # Remove extra spaces between Japanese characters
        normalized = re.sub(r'([ぁ-ん]+)\s+([ぁ-ん]+)', r'\1\2', normalized)  # ひらがな
        normalized = re.sub(r'([ァ-ヴ]+)\s+([ァ-ヴ]+)', r'\1\2', normalized)  # カタカナ
        normalized = re.sub(r'([一-龯]+)\s+([一-龯]+)', r'\1\2', normalized)  # 漢字
        
        # Fix spacing around Japanese punctuation
        normalized = re.sub(r'\s*([、。])\s*', r'\1', normalized)
        
        # Trim extra whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized
    
    def extract_text(self, image_path: str) -> str:
        """
        Extract text from image using PaddleOCR
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text as string
        """
        if not PADDLE_AVAILABLE or not self.ocr:
            return "PaddleOCR not available. Please install paddleocr: pip install paddlepaddle paddleocr"
        
        try:
            # Try preprocessing the image first
            preprocessed = self.preprocess_image(image_path)
            
            # Log preprocessing status
            if preprocessed is not None:
                logger.info(f"Using preprocessed image for OCR: {os.path.basename(image_path)}")
                result = self.ocr.ocr(preprocessed)
            else:
                logger.info(f"Using original image for OCR: {os.path.basename(image_path)}")
                result = self.ocr.ocr(image_path)
            
            if not result or not result[0]:
                return "No text detected in the image."
            
            ocr_result = result[0]
            extracted_lines = []
            
            # Check if it's the new OCRResult format
            if hasattr(ocr_result, 'json'):
                # New format - extract from JSON
                result_json = ocr_result.json
                if 'res' in result_json and 'rec_texts' in result_json['res']:
                    texts = result_json['res']['rec_texts']
                    scores = result_json['res'].get('rec_scores', [])
                    
                    for i, text in enumerate(texts):
                        confidence = scores[i] if i < len(scores) else 0.0
                        if text and text.strip():
                            # Normalize Japanese text
                            normalized_text = self.normalize_japanese_text(text)
                            
                            if confidence > 0.7:
                                # High confidence - include as is
                                extracted_lines.append(normalized_text)
                            elif confidence > 0.4:
                                # Medium confidence - include without marker for cleaner output
                                extracted_lines.append(normalized_text)
                            elif confidence > 0.2:
                                # Low confidence - still include for completeness
                                extracted_lines.append(normalized_text)
                            else:
                                # Very low confidence - include with warning
                                extracted_lines.append(f"{normalized_text} [未確認]")
            else:
                # Old format - legacy support
                for line in ocr_result:
                    # Each line contains: [coordinates, (text, confidence)]
                    if len(line) >= 2 and len(line[1]) >= 1:
                        text = line[1][0]
                        confidence = line[1][1] if len(line[1]) > 1 else 0.0
                        
                        # Include detected text with adjusted confidence thresholds
                        if text and text.strip():
                            # Normalize Japanese text
                            normalized_text = self.normalize_japanese_text(text)
                            
                            if confidence > 0.7:
                                # High confidence - include as is
                                extracted_lines.append(normalized_text)
                            elif confidence > 0.4:
                                # Medium confidence - include without marker for cleaner output
                                extracted_lines.append(normalized_text)
                            elif confidence > 0.2:
                                # Low confidence - still include for completeness
                                extracted_lines.append(normalized_text)
                            else:
                                # Very low confidence - include with warning
                                extracted_lines.append(f"{normalized_text} [未確認]")
            
            if extracted_lines:
                # Log extraction statistics
                logger.info(f"OCR extracted {len(extracted_lines)} text lines from {os.path.basename(image_path)}")
                
                # Log sample of extracted text for debugging (first 3 lines)
                sample_lines = extracted_lines[:3]
                if sample_lines:
                    logger.debug(f"Sample extracted text: {sample_lines}")
                
                return "\n".join(extracted_lines)
            else:
                logger.warning(f"Text detected in {os.path.basename(image_path)} but confidence too low to extract reliably")
                return "Text detected but confidence too low to extract reliably."
                
        except Exception as e:
            logger.error(f"OCR extraction error for {os.path.basename(image_path)}: {e}")
            return f"OCR extraction failed: {str(e)}"
    
    def extract_text_with_details(self, image_path: str) -> List[Tuple[str, float]]:
        """
        Extract text with confidence scores
        
        Args:
            image_path: Path to the image file
            
        Returns:
            List of tuples containing (text, confidence)
        """
        if not PADDLE_AVAILABLE or not self.ocr:
            return []
        
        try:
            # Try preprocessing the image first
            preprocessed = self.preprocess_image(image_path)
            
            # Perform OCR on preprocessed image if available, otherwise use original
            if preprocessed is not None:
                result = self.ocr.ocr(preprocessed)
            else:
                result = self.ocr.ocr(image_path)
            
            if not result or not result[0]:
                return []
            
            ocr_result = result[0]
            extracted_items = []
            
            # Check if it's the new OCRResult format
            if hasattr(ocr_result, 'json'):
                # New format - extract from JSON
                result_json = ocr_result.json
                if 'res' in result_json and 'rec_texts' in result_json['res']:
                    texts = result_json['res']['rec_texts']
                    scores = result_json['res'].get('rec_scores', [])
                    
                    for i, text in enumerate(texts):
                        confidence = scores[i] if i < len(scores) else 0.0
                        if text and text.strip():
                            extracted_items.append((text, confidence))
            else:
                # Old format - legacy support
                for line in ocr_result:
                    if len(line) >= 2 and len(line[1]) >= 1:
                        text = line[1][0]
                        confidence = line[1][1] if len(line[1]) > 1 else 0.0
                        extracted_items.append((text, confidence))
            
            return extracted_items
                
        except Exception as e:
            logger.error(f"Detailed OCR extraction error: {e}")
            return []
    
    def is_available(self) -> bool:
        """Check if PaddleOCR is available"""
        return PADDLE_AVAILABLE and self.ocr is not None
    
    def get_status(self) -> dict:
        """Get status of OCR service"""
        return {
            'type': 'PaddleOCR',
            'available': self.is_available(),
            'message': 'PaddleOCR ready for text extraction' if self.is_available() else 'PaddleOCR not initialized',
            'languages': ['en', 'japan', 'ch', 'korean'] if self.is_available() else [],
            'gpu_enabled': False  # Can be detected dynamically
        }