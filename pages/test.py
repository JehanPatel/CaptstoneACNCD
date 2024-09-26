import cv2
import streamlit as st
import av
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
from login import *

st.set_page_config(page_title="Code1", layout="wide")

hide_default_format = """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """
st.markdown(hide_default_format, unsafe_allow_html=True)

if authentication_status:
    authenticator.logout('Logout', 'sidebar')
    st.sidebar.write(f'Welcome to the app!')


if st.session_state.authentication_status:
    class VideoTransformer(VideoTransformerBase):
        def transform(self, frame):
            img = frame.to_ndarray(format="bgr24")

            # Convert frame to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Apply thresholding to segment out objects
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            # Find contours of objects
            contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # Iterate through contours and draw bounding rectangles
            for contour in contours:
                area = cv2.contourArea(contour)
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Return the annotated frame
            return av.VideoFrame.from_ndarray(img, format="bgr24")

    webrtc_ctx = webrtc_streamer(key="example", video_transformer_factory=VideoTransformer)

    st.write("Live Video Feed:")
    st.write(webrtc_ctx.video_transformer)

    if webrtc_ctx.state.playing:
        st.write("Contours are being scanned in real-time...")
else:
    st.error("Please login to view this page.")
    st.write(f'<meta http-equiv="refresh" content="0; url=/?login">', unsafe_allow_html=True)    
    st.stop()