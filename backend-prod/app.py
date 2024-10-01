from fastapi import FastAPI, Request, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import base64
import numpy as np
import slideshow_gen_json
import google_slides_gen
import sound
import generate_image
import image_processing
import socketio

app = FastAPI()

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='https://knowlify-frontend-production.up.railway.app')
socket_app = socketio.ASGIApp(sio, app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://knowlify-frontend-production.up.railway.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@sio.event
async def connect(sid, environ):
    print(f'Connected: {sid}')

@sio.event
async def join(sid, data):
    if isinstance(data, str):
        data2 = json.loads(data)

    else:
        data2 = data
        
    room = data2['room']
    sio.enter_room(sid, room)

@sio.event
async def disconnect(sid):
    print(f'Disconnected: {sid}')

@app.middleware("http")
async def add_cors_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.post("/generate_slides")
async def generate_slides(pdf: UploadFile = File(...), uuid: str = Form(...)):
    try:
        pdf_content = await pdf.read()
        slideshow_gen_json.generate_json(pdf_content, uuid)
        return JSONResponse(content={"successful": "success"}, status_code=200)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/title")
async def title(data: Request):
    print('in title')
    data = await data.json()
    uuid = data['uuid']
    print('got uuid')

    try:
        print('Data:', data)
        await sio.emit('title_data', data, room=uuid)
        print('finished socket emit')
        
    except Exception as e:
        print(e)
    return "Title received", 200

@app.post("/bullet_points")
async def bullet_points(data: Request):
    data = await data.json()
    uuid = data['uuid']
    await sio.emit('bullet_points_data', data, room=uuid)
    return "Bullet Points Received", 200

@app.post("/start")
async def start(data: Request):
    data = await data.json()
    uuid = data['uuid']
    await sio.emit('start_data', data, room=uuid)
    return "Start Audio Received", 200

@app.post("/write")
async def write(data: Request):
    data = await data.json()
    uuid = data['uuid']
    await sio.emit('write_data', data, room=uuid)
    return "Write Coords Received", 200

@app.post("/during_writing")
async def during_writing(data: Request):
    data = await data.json()
    uuid = data['uuid']
    await sio.emit('during_writing_data', data, room=uuid)
    return "During Writing Audio Received", 200

@app.post("/pause")
async def pause(data: Request):
    data = await data.json()
    uuid = data['uuid']
    await sio.emit('pause_data', data, room=uuid)
    return "Pause Audio Received", 200

@app.post("/stop")
async def stop(data: Request):
    data = await data.json()
    uuid = data['uuid']
    await sio.emit('stop_data', data, room=uuid)
    return "Stop Audio Received", 200

@app.post("/answer_question")
async def answer_question(request: Request):
    data = await request.json()
    slide = data.get('slide', '')
    transcript = data.get('transcript', '')

    question = f"Question:\n{transcript}\n\nJSON For A Slide:\n{slide}"

    try:
        json_response = slideshow_gen_json.answer_question(question)
        json_object = json.loads(json_response)
        slides = google_slides_gen.create_completed_slideshow(json_object)
        actions = []

        for obj in json_object:
            last_y = 10
            steps = []

            if 'transcript' in obj:
                audio_bytes = sound.get_audio(obj['transcript'])
                encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
                actions.append(encoded_audio)

            elif 'steps' in obj:
                for idx, step in enumerate(obj['steps']):
                    if 'START' in step:
                        audio_bytes = sound.get_audio(step['START'])
                        encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
                        steps.append(encoded_audio)

                    elif 'WRITE' in step:
                        image = generate_image.create_image()
                        last_y = generate_image.add_text_to_image(image, step['WRITE'], generate_image.X_DIMENSION, last_y + 5)
                        coords = image_processing.get_coordinates_from_processed_img(image, 0, 0)
                        if idx + 1 < len(obj['steps']) and 'DURING WRITING' in obj['steps'][idx + 1]:
                            during_writing_audio = sound.get_audio(obj['steps'][idx + 1]['DURING WRITING'])
                            encoded_audio = base64.b64encode(during_writing_audio).decode('utf-8')
                            steps.append([coords, encoded_audio])
                        else:
                            steps.append(coords)

                    elif 'PAUSE' in step:
                        audio_bytes = sound.get_audio(step['PAUSE'])
                        encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
                        steps.append(encoded_audio)

                    elif 'STOP' in step:
                        audio_bytes = sound.get_audio(step['STOP'])
                        encoded_audio = base64.b64encode(audio_bytes).decode('utf-8')
                        steps.append(encoded_audio)

            actions.append(steps)

        response = {
            'slides': slides,
            'actions': actions
        }

        serializable_response = json.loads(json.dumps(response, default=convert_to_serializable))

        return JSONResponse(content=serializable_response)
    
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

app.mount("/", socket_app)