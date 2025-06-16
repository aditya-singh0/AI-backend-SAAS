import pytesseract
from PIL import Image
import numpy as np

class CaptchaSolver:
    def __init__(self, tesseract_cmd_path=None):
        if tesseract_cmd_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_path
        else:
            # Default Windows Tesseract installation path
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def preprocess_image(self, image_path):
        image = Image.open(image_path).convert('L') # Convert to grayscale
        # Try multiple preprocessing approaches
        processed_images = []
        
        # Method 1: Simple binarization
        img1 = image.point(lambda x: 0 if x < 140 else 255)
        processed_images.append(img1)
        
        # Method 2: Different threshold
        img2 = image.point(lambda x: 0 if x < 120 else 255)
        processed_images.append(img2)
        
        # Method 3: Invert colors
        img3 = image.point(lambda x: 255 if x < 140 else 0)
        processed_images.append(img3)
        
        return processed_images

    def solve_captcha(self, image_path):
        processed_images = self.preprocess_image(image_path)
        
        # Try different OCR configurations
        configs = [
            r'--oem 3 --psm 7 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
            r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
            r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
            r'--oem 3 --psm 7',
            r'--oem 3 --psm 8'
        ]
        
        best_result = ""
        max_length = 0
        
        for img in processed_images:
            for config in configs:
                try:
                    text = pytesseract.image_to_string(img, config=config).strip()
                    # Clean the text
                    text = ''.join(c for c in text if c.isalnum())
                    
                    if len(text) > max_length and len(text) >= 4:  # CAPTCHA usually 4-6 chars
                        best_result = text
                        max_length = len(text)
                        
                except Exception:
                    continue
        
        return best_result if best_result else None

if __name__ == '__main__':
    # Example usage:
    # solver = CaptchaSolver(tesseract_cmd_path=r'C:\Program Files\Tesseract-OCR\tesseract.exe')
    # solution = solver.solve_captcha('path_to_your_captcha.png')
    # print(f"CAPTCHA Solution: {solution}")
    pass 