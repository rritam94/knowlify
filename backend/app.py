from flask import Flask, request, jsonify
from flask_cors import CORS
import slideshow_gen_json
import google_slides_gen
import test_ai_sound
import generate_image
import image_processing
import json
import base64
import numpy as np  # Import numpy
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)
CORS(app, origins='http://localhost:3000')

def convert_to_serializable(obj):
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, bytes):
        return base64.b64encode(obj).decode('utf-8')
    else:
        raise TypeError(f"Type {type(obj)} not serializable")

@app.route('/generate_slides', methods=['POST'])
def generate_slides():
    if 'pdf' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    pdf = request.files['pdf']
    print(pdf)

    if pdf.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        json_response = slideshow_gen_json.generate_json(pdf.read())

        json_object = json.loads(json_response)
        slides = google_slides_gen.create_completed_slideshow(json_object)
        actions = []

        for obj in json_object:
            last_y = 10

            if 'transcript' in obj:
                audio_bytes = test_ai_sound.get_audio(obj['transcript'])
                encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
                actions.append(encoded_audio)

            elif 'steps' in obj:
                steps = []
                
                for idx, step in enumerate(obj['steps']):
                    if 'START' in step:
                        audio_bytes = test_ai_sound.get_audio(step['START'])
                        encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
                        steps.append(encoded_audio)

                    elif 'WRITE' in step:
                        image = generate_image.create_image()
                        last_y = generate_image.add_text_to_image(image, step['WRITE'], generate_image.X_DIMENSION, last_y + 5)
                        coords = image_processing.get_coordinates_from_processed_img(image, 0, 0)
                        
                        if idx + 1 < len(obj['steps']) and 'DURING WRITING' in obj['steps'][idx + 1]:
                            during_writing_audio = test_ai_sound.get_audio(obj['steps'][idx + 1]['DURING WRITING'])
                            encoded_audio = base64.b64encode(during_writing_audio).decode('utf-8')
                            steps.append([coords, encoded_audio])
                        else:
                            steps.append(coords)

                    elif 'DURING WRITING' in step:
                        continue  

                    elif 'PAUSE' in step:
                        audio_bytes = test_ai_sound.get_audio(step['PAUSE'])
                        encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
                        steps.append(encoded_audio)

                    elif 'STOP' in step:
                        audio_bytes = test_ai_sound.get_audio(step['STOP'])
                        encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
                        steps.append(encoded_audio)

                actions.append(steps)

        response = {
            'slides': slides,
            'actions': actions,
            'json': json_object
        }

        serializable_response = json.loads(json.dumps(response, default=convert_to_serializable))

        return jsonify(serializable_response)
    
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500
    
@app.route('/answer_question', methods=['POST'])
def answer_question():
    data = request.get_json()
    slide = data.get('slide', '')
    transcript = data.get('transcript', '')

    question = 'Question:\n' + transcript + '\n\n' + 'JSON For A Slide:\n' + slide
    print(question)

    json_response = slideshow_gen_json.answer_question(question)

    with open('output2.txt', 'w', encoding='utf-8') as file:
        file.write(json_response)

    try:
        json_object = json.loads(json_response)
        slides = google_slides_gen.create_completed_slideshow(json_object)
        actions = []

        for obj in json_object:
            last_y = 10

            if 'transcript' in obj:
                audio_bytes = test_ai_sound.get_audio(obj['transcript'])
                encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
                actions.append(encoded_audio)

            elif 'steps' in obj:
                steps = []
                
                for idx, step in enumerate(obj['steps']):
                    if 'START' in step:
                        audio_bytes = test_ai_sound.get_audio(step['START'])
                        encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
                        steps.append(encoded_audio)

                    elif 'WRITE' in step:
                        image = generate_image.create_image()
                        last_y = generate_image.add_text_to_image(image, step['WRITE'], generate_image.X_DIMENSION, last_y + 5)
                        coords = image_processing.get_coordinates_from_processed_img(image, 0, 0)
                        
                        if idx + 1 < len(obj['steps']) and 'DURING WRITING' in obj['steps'][idx + 1]:
                            during_writing_audio = test_ai_sound.get_audio(obj['steps'][idx + 1]['DURING WRITING'])
                            encoded_audio = base64.b64encode(during_writing_audio).decode('utf-8')
                            steps.append([coords, encoded_audio])
                        else:
                            steps.append(coords)

                    elif 'DURING WRITING' in step:
                        continue  

                    elif 'PAUSE' in step:
                        audio_bytes = test_ai_sound.get_audio(step['PAUSE'])
                        encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
                        steps.append(encoded_audio)

                    elif 'STOP' in step:
                        audio_bytes = test_ai_sound.get_audio(step['STOP'])
                        encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
                        steps.append(encoded_audio)

                actions.append(steps)

        response = {
            'slides': slides,
            'actions': actions
        }

        serializable_response = json.loads(json.dumps(response, default=convert_to_serializable))

        return jsonify(serializable_response)
    
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)