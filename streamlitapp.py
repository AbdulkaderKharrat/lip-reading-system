import os
import tensorflow as tf
import imageio
import streamlit as st
from utils import load_data, num_to_char
from modelutils import load_model
import numpy as np

# Set the page layout to wide mode
st.set_page_config(layout="wide")

# Main Title
st.markdown("<h1 style='text-align: center;'>👄 LipBuddy: Your Lip Reading Companion</h1>", unsafe_allow_html=True)

# Setup the sidebar
with st.sidebar:
    st.image('images/lipnet.png')
    st.markdown("## Welcome to LipBuddy!")
    st.markdown("""
**👋 Hello there!** 

1. **Upload or select a pre-loaded video**: Pick a sample video from the dropdown.
2. **Preview the video**: See the video on the left side.
3. **Model Visualization**: On the right, see what the ML model "sees" and the predicted tokens.
4. **Final Transcription**: Get a decoded transcript of the video.
    """)

# Fetch video options
options = os.listdir(os.path.join('data', 's1'))

# Video Selection
st.markdown("### 🎥 Select a Video")
selected_video = st.selectbox(
    'Pick a video from the dataset below:',
    options
)

if selected_video:
    col1, col2 = st.columns(2)

    # Render the original video in MP4 format
    with col1:
        st.markdown("### 📺 Original Video Preview")
        file_path = os.path.join('data', 's1', selected_video)

        # Convert video to MP4 using ffmpeg
        os.system(f'ffmpeg -i {file_path} -vcodec libx264 test_video.mp4 -y')

        # Render MP4 video in Streamlit
        video = open('test_video.mp4', 'rb')
        video_bytes = video.read()
        st.video(video_bytes)

    # Model Visualization on the other side
    with col2:
        st.markdown("### 🔬 Model Input Visualization")

        # Load video data and annotations
        video, annotations = load_data(tf.convert_to_tensor(file_path))
        frames = [np.squeeze(frame.numpy(), axis=-1) for frame in video]  # Remove last dimension
        frames = [np.uint8(frame*100) for frame in frames]
        imageio.mimsave('output.gif', frames, fps=10)
        
        # Display GIF of preprocessed frames
        st.image('output.gif', width=400, caption="Model's View (Preprocessed Frames)")

        # Load the model
        model = load_model()
        if model is None:
            st.error("🚨 Failed to load the model. Please check your configuration.")
        else:
            st.success("✅ Model loaded successfully!")
            st.info('**Next Step**: Let’s run a prediction on the selected video.')

            # Run prediction
            st.markdown("### 🔡 Raw Model Predictions")
            yhat = model.predict(tf.expand_dims(video, axis=0))
            st.write("**Raw argmax tokens:**", tf.argmax(yhat, axis=1).numpy())

            # Decode the tokens using CTC decode
            decoder = tf.keras.backend.ctc_decode(yhat, [75], greedy=True)[0][0].numpy()
            st.write("**CTC Decoded Tokens:**", decoder)

            # Convert decoded tokens to text
            st.markdown("### 🗣️ Decoded Speech")
            converted_prediction = tf.strings.reduce_join(num_to_char(decoder)).numpy().decode("utf-8")
            st.markdown(f"**Predicted Transcript:** `{converted_prediction}`")

else:
    st.warning("⚠️ No videos found. Please check your 'data/s1' directory or refresh the page.")

