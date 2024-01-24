#pip install opencv
import cv2

# Load the pre-trained face detection model
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# Start video capture from the default camera
video_capture = cv2.VideoCapture(0)

while True:
    # Capture a frame from the video
    ret, frame = video_capture.read()

    # Convert the frame to grayscale for face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale frame
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # Iterate over each detected face and blur it
    for (x, y, w, h) in faces:
        # Define a Gaussian blur kernel with a larger size for effective blurring
        kernel_size = (51, 51)  # Adjust as needed
        blurred_face = cv2.GaussianBlur(frame[y:y+h, x:x+w], kernel_size, 0)

        # Replace the original face region with the blurred face
        frame[y:y+h, x:x+w] = blurred_face

    # Display the blurred frame
    cv2.imshow('Blurred Video', frame)

    # Exit if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close all windows
video_capture.release()
cv2.destroyAllWindows()
