import os
import subprocess
from flask import Flask, request, jsonify, render_template 
from frame_extractor import extract_frames_on_scene_change
import openai

app = Flask(__name__)

# Directly setting the API key
openai.api_key = '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'

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
        video_filename = video.filename
        video_path = os.path.join(upload_folder, video_filename)
        video.save(video_path)

        # Your video processing logic here...
        repo_path = '/Users/kekerahnasto/Desktop/Tuttass/uploads/extracted_frames/imagerepo'
        extract_frames_on_scene_change(video_path, repo_path, change_threshold=0.5, font_size=1, font_color=(0, 255, 255))

        # Assuming frames are pushed to GitHub and accessible via URLs
        github_base_url = 'https://raw.githubusercontent.com/tuttass/imagerepo/main/'
        extracted_frames = [f for f in os.listdir(repo_path) if f.endswith('.jpg')]
        image_urls = [github_base_url + frame for frame in extracted_frames]

        # Constructing messages for the API call, including image URLs
        messages = [
            {"role": "system", "content": "Generate a description for the video based on the provided frames."},
            *[
                {"role": "user", "content": {"type": "image_url", "image_url": url}}
                for url in image_urls
            ]
        ]

try:
    response = openai.ChatCompletion.create(
    model="gpt-4-vision-preview",
    messages=messages,
    temperature=0.7,
    max_tokens=2000,
    top_p=1,
    frequency_penalty=0
    )
            
    # Assuming the response structure has the desired text in the first choice's content
    tutorial_text = response.choices[0].message['content']
    with open('tutorial_text.txt', 'w') as file:
        file.write(tutorial_text)
                
    return jsonify({"message": "Video processed and tutorial text generated.", "tutorial_text": tutorial_text})   
except Exception as e:
    print(f"Error processing video: {e}")
    # Optionally, log the traceback to get more detail on the error
    import traceback
    traceback.print_exc()
    return jsonify({"error": str(e)}), 500
else:
    return jsonify({"error": "No video file received."}), 400

if __name__ == '__main__':
    app.run(debug=True)