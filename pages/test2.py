import streamlit as st
import cv2
import numpy as np
import av
from streamlit_webrtc import VideoProcessorBase, webrtc_streamer
import threading
from login import *

st.set_page_config(page_title="Code3", layout="wide")

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
    class VideoTransformer(VideoProcessorBase):
        def __init__(self):
            self.frame_lock = threading.Lock()
            self.in_image = None

        def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
            in_image = frame.to_ndarray(format="bgr24")
            
            # Apply the watershed method to the image
            gray = cv2.cvtColor(in_image, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            kernel = np.ones((3, 3), np.uint8)
            opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
            sure_bg = cv2.dilate(opening, kernel, iterations=3)
            dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
            _, sure_fg = cv2.threshold(dist_transform, 0.7 * dist_transform.max(), 255, 0)
            sure_fg = np.uint8(sure_fg)
            unknown = cv2.subtract(sure_bg, sure_fg)
            _, markers = cv2.connectedComponents(sure_fg)
            markers = markers + 1
            markers[unknown == 255] = 0
            markers = cv2.watershed(in_image, markers)
            in_image[markers == -1] = [255, 0, 0]
            
            with self.frame_lock:
                self.in_image = in_image
            
            return av.VideoFrame.from_ndarray(in_image)

    webrtc_ctx = webrtc_streamer(key="example", video_processor_factory=VideoTransformer)

    if st.button("Capture Image"):
        # Get the last processed frame from the VideoTransformer instance
        video_transformer = webrtc_ctx.video_processor
        with video_transformer.frame_lock:
            frame = video_transformer.in_image
        st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
else:
    st.error("Please login to view this page.")
    st.write(f'<meta http-equiv="refresh" content="0; url=/?login">', unsafe_allow_html=True)    
    st.stop()