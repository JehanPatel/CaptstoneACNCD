import cv2
import numpy as np
import streamlit as st
from login import *

st.set_page_config(page_title="Code2", layout="wide")

hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

authenticator.logout('Logout', 'sidebar')
st.sidebar.write(f'Welcome to the app!')

if st.session_state.authentication_status:
    # Create a Streamlit app
    st.title("Live Video Feed with Image Processing")

    # Create a checkbox for toggling image segmentation
    segmentation_enabled = st.checkbox("Enable Image Segmentation", value=True)

    # Create a video capture object
    cap = cv2.VideoCapture(0)

    # Create a window for displaying the video
    stframe = st.image([])

    while True:
        # Read a frame from the video capture object
        ret, frame = cap.read()

        if segmentation_enabled:
            # Convert the frame to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Apply thresholding to the grayscale image
            ret, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)

            # Create a kernel for morphological operations
            kernel = np.ones((5, 5), np.uint8)

            # Apply erosion to the thresholded image
            eroded = cv2.erode(thresh, kernel, iterations=3)

            # Find contours in the eroded image
            contours, _ = cv2.findContours(eroded, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Create markers for the watershed algorithm
            markers = np.zeros(gray.shape, dtype=np.int32)
            for i, contour in enumerate(contours):
                cv2.drawContours(markers, [contour], -1, i+1, -1)

            # Convert the frame to 3-channel 8-bit unsigned integer image
            frame_8uc3 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Apply the watershed algorithm
            cv2.watershed(frame_8uc3, markers)

            # Visualize the result using a colormap
            result = markers.astype(np.uint8)
            result = cv2.applyColorMap(result, cv2.COLORMAP_RAINBOW)
        else:
            # Display the original frame if segmentation is disabled
            result = frame

        # Display the result
        stframe.image(result)

        # Exit on key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object
    cap.release()
    cv2.destroyAllWindows()
else:
    st.error("Please login to view this page.")
    st.write(f'<meta http-equiv="refresh" content="0; url=/?login">', unsafe_allow_html=True)    
    st.stop()