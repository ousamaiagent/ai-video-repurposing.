import streamlit as st
import requests
from pytube import YouTube
from moviepy.editor import VideoFileClip
import os

# Set your Groq API key
groq_api_key = st.secrets.get("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", None)
if not groq_api_key:
    st.error("GROQ_API_KEY is missing in Streamlit secrets.")
    st.stop()

# Function to download YouTube video
def download_youtube_video(yt_link):
    try:
        yt = YouTube(yt_link)
        stream = yt.streams.filter(file_extension="mp4").get_lowest_resolution()
        video_path = "downloaded_video.mp4"
        stream.download(filename=video_path)
        return video_path
    except Exception as e:
        st.error(f"Failed to download video: {str(e)}")
        return None

# Function to clip a video
def clip_video(video_path, start_time, end_time):
    try:
        clip = VideoFileClip(video_path).subclip(start_time, end_time)
        clipped_path = "short_clip.mp4"
        clip.write_videofile(clipped_path, codec="libx264")
        return clipped_path
    except Exception as e:
        st.error(f"Failed to clip video: {str(e)}")
        return None

# Function to call Groq API for caption generation
def generate_caption(transcript):
    try:
        headers = {
            "Authorization": f"Bearer {groq_api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "model": "gpt-4",
            "prompt": f"Summarize this: {transcript}",
            "max_tokens": 200,
            "temperature": 0.7,
        }
        response = requests.post("https://api.groq.com/v1/generate", headers=headers, json=data)
        if response.status_code == 200:
            return response.json().get("text", "No caption generated.")
        else:
            st.error(f"Groq API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Failed to generate caption: {str(e)}")
        return None

# Streamlit app title
st.title("🎬 AI Video Repurposing Assistant")

# Step 1: User inputs YouTube link
st.subheader("Step 1: Download YouTube Video")
yt_link = st.text_input("Paste your YouTube video link")

if yt_link:
    video_path = download_youtube_video(yt_link)
    if video_path:
        st.video(video_path)
        st.success("Downloaded video successfully!")

        # Step 2: Clip the video
        st.subheader("Step 2: Clip the Video")
        start_time = st.number_input("Start Time (in seconds)", min_value=0, value=0)
        end_time = st.number_input("End Time (in seconds)", min_value=start_time + 1, value=60)

        if st.button("Clip Video"):
            clipped_path = clip_video(video_path, start_time, end_time)
            if clipped_path:
                st.video(clipped_path)
                st.success("Clipped video successfully!")

                # Step 3: Generate Caption
                st.subheader("Step 3: Generate Caption")
                st.write("Using YouTube description as a placeholder transcript.")
                transcript = YouTube(yt_link).description[:1000]  # Placeholder for actual transcript extraction
                generated_caption = generate_caption(transcript)

                if generated_caption:
                    st.write("📢 Suggested Caption:")
                    st.code(generated_caption)

                # Step 4: Google Drive Upload (Placeholder)
                st.subheader("Step 4: Upload to Google Drive (Coming Soon)")
                st.write("Feature to upload videos to Google Drive will be available in future updates.")

        # Clean up downloaded files
        if os.path.exists(video_path):
            os.remove(video_path)
