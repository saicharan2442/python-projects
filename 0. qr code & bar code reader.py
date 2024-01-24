# run in jupyter lab

#pip install pyzbar
#pip install opencv
#pip install numpy

import cv2
import numpy as np
from pyzbar.pyzbar import decode

# Initialize video capture
cap = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Decode barcodes and QR codes
    barcodes = decode(frame)

    # Iterate through each detected barcode
    for barcode in barcodes:
        # Extract barcode data and type
        data = barcode.data.decode('utf-8')
        type = barcode.type

        # Print barcode information
        print(f"Data: {data}, Type: {type}")

        # Draw a rectangle around the barcode and display text
        x, y, w, h = barcode.rect
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(frame, data, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow("Barcode Scanner", frame)

    # Exit on 'q' key press
    if cv2.waitKey(1) == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
