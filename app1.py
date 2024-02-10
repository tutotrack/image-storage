import requests
import base64
import os
from flask import Flask, request, render_template
from frame_extractor import extract_every_nth_frame_with_timestamp

app = Flask(__name__)

# Function to encode image to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    video = request.files['video']
    if video:
        upload_folder = os.path.join(os.getcwd(), 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        video_path = os.path.join(upload_folder, video.filename)
        video.save(video_path)

        # Extract frames
        extracted_frames_dir = extract_every_nth_frame_with_timestamp(video_path, 40)
        extracted_frames = [os.path.join(extracted_frames_dir, f) for f in os.listdir(extracted_frames_dir) if f.endswith('.jpg')]

        # Prepare API request
        prompt = "act as a tutorial and how-to video expert. [I will include a bunch of image frames from a video. I want you to create a text that fits a tutorial video for the functions that appear on the frames from the video. There is a timestamp on each of the frames so you see which comes first. I want you to explain what is happening in each step, a step is everytime the screen changes, not each frame. I want you to divide it into steps. It needs to include an intro. the context you get for the intro is that the company is called mynewsdesk, you do not need to mention what Mynewsdesk does but should mention Mynewsdesk and what this video will show. So there will be one intro and numerous other steps. The idea is that I am going to create a TTS on the text you provide to me later so I want you to include a time stamp each time you create a step. So put the time step first before starting next step together with what is going to happen in that step. (00:00:00 Minutes, seconds and milli seconds).]"
        encoded_frames = [encode_image_to_base64(frame) for frame in extracted_frames]
        data = {
            "model": "gpt-4-vision-preview",  # Replace with the correct model
            "prompt": prompt,
            "max_tokens": 2000,
            "temperature": 0.5,
            # Include encoded frames in the prompt or as additional parameters
        }

        headers = {
            'Authorization': 'Bearer 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',
            'Content-Type': 'application/json'
        }

        response = requests.post("https://api.openai.com/v1/engines/text-davinci-002/completions", json=data, headers=headers)
        tutorial_text = response.json()

        # Handle the tutorial text
        # ...

        return "Video processed and tutorial text generated."
    return "Failed to upload video."

if __name__ == '__main__':
    app.run(debug=True)
