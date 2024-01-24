#pip install opencv
import cv2

def cartoonify(image_path):
    """Cartoonifies an image using OpenCV techniques."""

    # 1. Load the image
    img = cv2.imread(image_path)

    # 2. Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 3. Apply median blur to reduce noise and smoothen details
    gray = cv2.medianBlur(gray, 5)

    # 4. Apply adaptive thresholding to highlight edges
    edges = cv2.adaptiveThreshold(gray, 255,cv2.ADAPTIVE_THRESH_MEAN_C,cv2.THRESH_BINARY, 9, 2)

    # 5. Reduce color palette using bilateral filter
    color = cv2.bilateralFilter(img, 9, 250, 250)

    # 6. Combine edges with color to create cartoon effect
    cartoon = cv2.bitwise_and(color, color, mask=edges)

    return cartoon

# Example usage:
cartoon_image = cartoonify("Downloads/THAR.jpg")

# Display the cartoon image
cv2.imshow("Cartoonified Image", cartoon_image)
cv2.waitKey(0)
cv2.destroyAllWindows()