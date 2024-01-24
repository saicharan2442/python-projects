import cv2

# Access the default camera
camera = cv2.VideoCapture(0)

while True:
    # Capture a frame from the camera
    ret, frame = camera.read()

    # Display the frame
    cv2.imshow('Camera', frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) == ord('q'):
        break

# Release the camera and close the windows
camera.release()
cv2.destroyAllWindows()
