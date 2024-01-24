#run in jupyter

#pip install opencv 
import cv2

# Load the image
img = cv2.imread('THAR.jpg')

# Convert to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply Gaussian blur to reduce noise
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# Apply Canny edge detection
edges = cv2.Canny(blurred, 100, 200)  # Adjust thresholds for desired results

# Display the original image and the edge detected image
cv2.imshow('Original Image', img)
cv2.imshow('Edge Detected Image', edges)

# Wait for key press to close windows
cv2.waitKey(0)
cv2.destroyAllWindows()