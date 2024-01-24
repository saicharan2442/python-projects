import cv2

def sketch(image_path):
  """Converts a photo to a pencil sketch-like image."""

  # Load the image in grayscale
  image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

  # Apply Gaussian blur to reduce noise
  blurred = cv2.GaussianBlur(image, (5, 5), 0)

  # Create a pencil sketch effect using adaptive thresholding
  sketch = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 2)

  # Invert the image for a more natural-looking sketch
  inverted_sketch = 255 - sketch

  # Show the sketch
  cv2.imshow("Sketch", inverted_sketch)
  cv2.waitKey(0)
  cv2.destroyAllWindows()

# Example usage:
image_path = "Downloads/THAR.jpg"  # Replace with your image path
sketch(image_path)