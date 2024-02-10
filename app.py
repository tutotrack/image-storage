import os
import subprocess
import traceback
from flask import Flask, request, jsonify, render_template
from frame_extractor import extract_frames_on_scene_change
import openai

app = Flask(__name__)

# Directly setting the API key for simplicity; consider using environment variables for production
client = openai.OpenAI(api_key='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')

def clean_directory(directory_path):
    """
    Deletes all files in the specified directory.
    """
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(f'Failed to delete {file_path}. Reason: {e}')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_video():
    # Extract the prompt text from the form data
    user_prompt = request.form['prompt']
    video = request.files['video']
    if video:
        upload_folder = os.path.join(os.getcwd(), 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)
        video_filename = video.filename
        video_path = os.path.join(upload_folder, video_filename)
        video.save(video_path)

        repo_path = '/Users/kekerahnasto/Desktop/Tuttass/uploads/extracted_frames/imagerepo'
        extract_frames_on_scene_change(video_path, repo_path, change_threshold=0.5, font_size=1, font_color=(0, 255, 255))

        github_base_url = 'https://raw.githubusercontent.com/tuttass/imagerepo/main/'
        extracted_frames = [f for f in os.listdir(repo_path) if f.endswith('.jpg')]
        image_urls = [github_base_url + frame for frame in extracted_frames]

        messages = [
    {"role": "system", "content": "act as a tutorial and how-to video expert. I will include a bunch of image frames from a video. I want you to create a text that fits a tutorial video for the functions that appear on the frames from the video. Where they click. what does it say on the button they click. There is a timestamp on each of the frames so you see which comes first. I want you to explain what is happening in each step, a step is everytime the screen changes, not each frame. I want you to divide it into steps. The idea is that I am going to create a TTS on the text you provide to me later so I want you to include a time stamp each time you create a step. So put the time step first before starting next step together with what is going to happen in that step. (00:00:00 Minutes, seconds and milli seconds)."},
    {"role": "user", "content": user_prompt},
    # Assuming image_urls is a list of image URL strings
    *[
        {"role": "user", "content": url}
        for url in image_urls
    ]
]

        try:
            # Using the ChatCompletion API correctly for gpt-4-vision-preview
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=messages,
                temperature=0.7,
                max_tokens=2000,
                top_p=1,
                frequency_penalty=0
            )
            tutorial_text = response.choices[0].message.content
            with open('tutorial_text.txt', 'w') as file:
                file.write(tutorial_text)
            return jsonify({"message": "Video processed and tutorial text generated.", "tutorial_text": tutorial_text})
        except Exception as e:
            print(f"Error processing video: {e}")
            traceback.print_exc()
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "No video file received."}), 400

if __name__ == '__main__':
    app.run(debug=True)