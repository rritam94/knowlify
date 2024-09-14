import json
import numpy as np
import base64
import sound
import generate_image
import image_processing
import requests
import ast
import openai
import gpt_imggen_combined
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPEN_AI_KEY")

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

def send_request(url, data):
    response = requests.post(url, json=data)
    return response.text

def complete_api_request(prompt, pdf, uuid, current_slide=0, max_tokens=3000):
    found_title = False
    title = ''

    found_bullet_points = False
    bullet_points = ''

    found_start = False
    start = ''

    found_drawing = False
    drawing = ''

    found_during_drawing = False
    during_drawing = ''

    found_write = False
    write = ''

    found_during_writing = False
    during_writing = ''

    found_pause = False
    pause = ''

    found_stop = False
    stop = ''

    last_y = 10
    image = generate_image.create_image()

    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": entire_prompt},
            {"role": "user", "content": pdf}
        ],
        max_tokens = 16000,
        stream=True,
        temperature=1,
        top_p=1,
        frequency_penalty = 0,
        presence_penalty = 0,
        max_retries=3,
    )

    content = ''
    total_content = ''

    for chunk in completion:
        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
            content = chunk.choices[0].delta.content

            total_content += content
    
            if '题' in content.lower():
                found_title = True

            elif not (',' in content.lower()) and found_title:
                title += content
            
            elif ',' in content.lower() and found_title:
                if title[4:] != '':
                    title = title[4:]
                    response = {
                        "slide_number": current_slide,
                        "title": title,
                        "uuid": uuid,
                    }

                    serializable_response = json.loads(json.dumps(response, default=convert_to_serializable))
                    send_request('http://knowlify.us-east-2.elasticbeanstalk.com/title', serializable_response)
                    title = ''
                    found_title = False

            if '数' in content.lower():
                found_bullet_points = True

            elif not (']' in content.lower()) and found_bullet_points:
                bullet_points += content
            
            elif ']' in content.lower() and found_bullet_points:
                if bullet_points != '':
                    bullet_points = bullet_points[3:]
                    bullet_points += ']'
                    single_line_string = " ".join(bullet_points.split())
                    bullet_points_list = ast.literal_eval(single_line_string)

                    response = {
                        "slide_number": current_slide,
                        "bullet_points": bullet_points_list,
                        "uuid": uuid
                    }

                    serializable_response = json.loads(json.dumps(response, default=convert_to_serializable))
                    send_request('http://knowlify.us-east-2.elasticbeanstalk.com/bullet_points', serializable_response)

                    bullet_points = ''
                    found_bullet_points = False

            if '始' in content.lower():
                found_start = True

            elif not ('}' in content.lower()) and found_start:
                start += content
            
            elif '}' in content.lower():
                if start[4:] != '':
                    for char in content.lower():
                        if char != '}':
                            start += char
                        else: break

                    start = start[4:-1]
                    start_sound = sound.get_audio(start)

                    response = {
                        "slide_number": current_slide,
                        "start": start_sound,
                        "uuid": uuid,
                        "content": total_content
                    }

                    serializable_response = json.loads(json.dumps(response, default=convert_to_serializable))
                    send_request('http://knowlify.us-east-2.elasticbeanstalk.com/start', serializable_response)
                    
                    start = ''
                    found_start = False

            if '拉' in content.lower():
                found_drawing = True
                image = generate_image.create_image()
                coords = []

            elif not ('}' in content.lower()) and found_drawing:
                drawing += content
            
            elif '}' in content.lower():
                if drawing[4:] != '':
                    for char in content.lower():
                        if char != '}':
                            drawing += char
                        else: break

                    drawing = drawing[4:-1]

                    image_gen = gpt_imggen_combined.generate_python_code(drawing, total_content)
                    last_y = generate_image.add_image_to_image(image, image_gen, last_y + 5)
                    coords = image_processing.get_coordinates_from_processed_img(image)

                    drawing = ''
                    found_drawing = False

            if '图' in content.lower():
                found_during_drawing = True

            elif not ('}' in content.lower()) and found_during_drawing:
                during_drawing += content
            
            elif '}' in content.lower() and found_during_drawing:
                if during_drawing[4:] != '':
                    for char in content.lower():
                        if char != '}':
                            during_drawing += char
                        else: break

                    during_drawing = during_drawing[4:-1]
                    during_drawing_sound = sound.get_audio(during_drawing)

                    response = {
                        "slide_number": current_slide,
                        "coords": coords,
                        "during_writing": during_drawing_sound,
                        "uuid": uuid,
                        "content": total_content
                    }

                    serializable_response = json.loads(json.dumps(response, default=convert_to_serializable))
                    send_request('http://knowlify.us-east-2.elasticbeanstalk.com/during_writing', serializable_response)
                    
                    during_drawing = ''
                    found_during_drawing = False

            if '写' in content.lower():
                found_write = True
                image = generate_image.create_image()
                coords = []

            elif not ('}' in content.lower()) and found_write:
                write += content
            
            elif '}' in content.lower():
                if write[4:] != '':
                    for char in content.lower():
                        if char != '}':
                            write += char
                        else: break

                    write = write[4:-1]

                    last_y = generate_image.add_text_to_image(image, write, generate_image.X_DIMENSION, last_y + 5)
                    coords = image_processing.get_coordinates_from_processed_img(image, 0, 0)

                    write = ''
                    found_write = False

            if '时' in content.lower():
                found_during_writing = True

            elif not ('}' in content.lower()) and found_during_writing:
                during_writing += content
            
            elif '}' in content.lower() and found_during_writing:
                if during_writing[4:] != '':
                    for char in content.lower():
                        if char != '}':
                            during_writing += char
                        else: break

                    during_writing = during_writing[4:-1]
                    during_writing_sound = sound.get_audio(during_writing)

                    response = {
                        "slide_number": current_slide,
                        "coords": coords,
                        "during_writing": during_writing_sound,
                        "uuid": uuid,
                        "content": total_content
                    }

                    serializable_response = json.loads(json.dumps(response, default=convert_to_serializable))
                    send_request('http://knowlify.us-east-2.elasticbeanstalk.com/during_writing', serializable_response)
                    
                    during_writing = ''
                    found_during_writing = False
            
            if '暂' in content.lower():
                found_pause = True

            elif not ('}' in content.lower()) and found_pause:
                pause += content
            
            elif '}' in content.lower() and found_pause:
                if pause[4:] != '':
                    for char in content.lower():
                        if char != '}':
                            pause += char
                        else: break

                    pause = pause[4:-1]
                    pause_sound = sound.get_audio(pause)

                    response = {
                        "slide_number": current_slide,
                        "pause": pause_sound,
                        "uuid": uuid,
                        "content": total_content
                    }

                    serializable_response = json.loads(json.dumps(response, default=convert_to_serializable))
                    send_request('http://knowlify.us-east-2.elasticbeanstalk.com/pause', serializable_response)

                    pause = ''
                    found_pause = False
            
            if '停' in content.lower():
                found_stop = True

            elif not ('}' in content.lower()) and found_stop:
                stop += content
            
            elif '}' in content.lower() and found_stop:
                if stop[4:] != '':
                    for char in content.lower():
                        if char != '}':
                            stop += char
                        else: break

                    stop = stop[4:-1]
                    stop_sound = sound.get_audio(stop)

                    response = {
                        "slide_number": current_slide,
                        "stop": stop_sound,
                        "uuid": uuid,
                        "content": total_content
                    }

                    serializable_response = json.loads(json.dumps(response, default=convert_to_serializable))
                    send_request('http://knowlify.us-east-2.elasticbeanstalk.com/stop', serializable_response)

                    stop = ''
                    found_stop = False

                    last_y = 10
                    current_slide += 1
                    total_content = ''

    return current_slide

def read_file_in_chunks(file_path, chunk_size=1024):
    with open(file_path, 'r') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk

def answer_question(prompt, question):

    completion = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question}
        ],
        max_tokens = 1024,
        stream=True,
        temperature=1,
        top_p=1,
        frequency_penalty = 0,
        presence_penalty = 0,
    )

    content = ''

    for chunk in completion:
        if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content is not None:
            content += chunk.choices[0].delta.content

    return content

entire_prompt = '''
You are an AI teacher who is explaining the material in a clear and easy-to-understand manner. When generating dialogue, focus on teaching the content directly, without mentioning your actions. The dialogue should be informative, seamless, and enhance the understanding of the material being presented. Additionally, make the output make sense. Write steps should include every SINGLE calculation involving numbers. Drawing steps should delineate the 
FINAL image created.
 
- Informative slide titles reflecting each section's main idea. 
- Bullet points summarizing key points. 
- A "steps" object explaining content in-depth with presentation instructions, such as verbal dialogue and writing and drawing decriptions. 
- Separate slides for general information and example problems. 
- Output 2 lengthy slides that go over the material in depth.
 
The steps object is used by another AI that will follow the steps you generate. The goal here is to have the you as the AI teach in a natural manner that emphasizes all concepts. 
 
Follow this output format as JSON: 
{ 
  "标题": "TITLE_OF_SLIDE", 
  "点数": ["POINT_1", "POINT_2", ...], 
  "steps": [ 
    {"开始": "Generate dialogue that you as the AI teacher should say to introduce the material based on the bullet points"}, 
 
    {"暂": "Generate dialogue that you as the AI teacher should say to smoothly flow into the next step where it will start drawing something out. It should add context to enhance the viewer's understanding."}, 
    {"拉": "Generate an extremely detailed prompt of what to draw. Use a bottom-up approach to showcase every single characteristic needed in the **FINAL** image. The goal here is to draw something that helps explain the concepts/problem statement. This step should not be in first person."}, 
    {"图": "Generate conversational dialogue that will be put into a text-to-speech application in which you as the AI teacher will say while they draw the image from the step before. The goal here is to continuously teach the concept with the given image being used for contextual understanding. Do not include any calculations in this dialogue."}, 
    {"暂": "Generate dialogue that you as the AI teacher should say to smoothly flow from the previous step where it will finish drawing something out. It should add context to enhance the viewer's understanding."}, 
     
    {"暂": "Generate dialogue that you as the AI teacher should say to smoothly flow into the next step where it will start writing something out. It should add context to enhance the viewer's understanding."}, 
    {"写": "Generate text that should be written by you as the AI teacher. Don't generate more than 5 words, but if it's a math statement, you can leave it the length that it is. The goal here is to either go through an example problem or write short statements/equations to help teach the content."}, 
    {"作时": "Generate conversational dialogue that will be put into a text-to-speech application in which you asthe AI teacher will say while they write the text from the step before. The goal here is to continuously teach the concept with the given text being used for contextual understanding. Do not include any calculations in this dialogue."}, 
    {"暂": "Generate dialogue that you as the AI teacher should say to smoothly flow from the previous step where it will finish writing something out. It should add context to enhance the viewer's understanding."}, 
 
    {"暂": "Generate dialogue that you as the AI teacher should say to smoothly flow into the next step where it will start drawing something out. It should add context to enhance the viewer's understanding."}, 
    {"拉": "Generate an extremely detailed prompt of what to draw. Use a bottom-up approach to showcase every single characteristic needed in the **FINAL** image. The goal here is to draw something that helps explain the concepts/problem statement. This step should not be in first person."}, 
    {"图": "Generate conversational dialogue that will be put into a text-to-speech application in which you as the AI teacher will say during the drawing of the image from the step before. The goal here is to continuously teach the concept with the given image being used for contextual understanding. Do not include any calculations in this dialogue."}, 
    {"暂": "Generate dialogue that the AI teacher should say to smoothly flow from the previous step where it will finish drawing something out. It should add context to enhance the viewer's understanding."}, 
     
    {"暂": "Generate dialogue that you as the AI teacher should say to smoothly flow into the next step where it will start writing something out. It should add context to enhance the viewer's understanding."}, 
    {"写": "Generate text that should be written by you as the AI teacher. Don't generate more than 5 words, but if it's a math statement, you can leave it the length that it is. The goal here is to either go through an example problem or write short statements/equations to help teach the content."}, 
    {"作时": "Generate conversational dialogue that will be put into a text-to-speech application in which you as the AI teacher will say while they write the text from the step before. The goal here is to continuously teach the concept with the given text being used for contextual understanding. Do not include any calculations in this dialogue."}, 
    {"暂": "Generate dialogue that you as the AI teacher should say to smoothly flow from the previous step where it will finish writing something out. It should add context to enhance the viewer's understanding."}, 
 
    {"停": "Generate dialogue that summarize key takeaways from the current slide."} 
  ] 
} 
 
Feel free to use as many draw/write statements out. Always make sure to follow this format though when drawing/writing (暂, 写/拉, 图/作时, 暂). Make your keys in the JSON in Chinese (as in the example), but everything else should be in English. The 拉 step should be a prompt that will be put into another AI that will generate that image. Always remember, the 作时 and 图 should be in first person and should not say the actions of whatever the AI is doing. It should rather be text that teaches the material in context of the step before it. 

Please don't tell me what to do. Just explain what you're doing and teach the material in relation to the text :). Don't draw tables. Only graphs. Also, don't include equations or calculations in dialogue please! For example problems, the steps array should rather be a list of steps to solve the problem.
'''

prompt_2 = '''
Respond back with the following text no matter what the user prompt is:

{
  "标题": "Expected Value and Probability Distributions",
  "点数": [
    "Understanding the probability distribution of random variables.",
    "Calculating the expected value of a random variable.",
    "Applying these concepts to real-world examples."
  ],
  "steps": [
    {
      "开始": "In this lesson, we'll explore how to determine the probability distribution of a random variable and calculate its expected value. The probability distribution provides a model for predicting outcomes, while the expected value helps us understand the average result of these outcomes."
    },
    {
      "暂": "We'll start by visualizing the probability distribution of a random variable through a graph. This will help us see how probabilities are distributed across different values."
    },
    {
      "拉": "Create a new bar graph to show the probability distribution of the random variable Y. On the x-axis, plot the possible values of Y, which are 0, 1, and 2. On the y-axis, plot the probabilities for each value. The heights of the bars should represent the following probabilities: Y=0 should have a bar height of 0.25, Y=1 should have a bar height of 0.50, and Y=2 should have a bar height of 0.25. Ensure the y-axis ranges from 0 to 1 to accommodate the maximum probability value."
    },
    {
      "图": "As we look at the bar graph, notice how the probability of Y being 1 is the highest, at 0.50. This visual representation helps us see which values are more likely. The height of each bar represents the probability of that particular outcome, providing a clear view of the distribution."
    },
    {
      "暂": "Next, we'll discuss the formula used to calculate the expected value. This involves understanding the default equation and how it applies to our probability distribution."
    },
    {
      "写": "E(Y) = sum [y times p(y)]"
    },
    {
      "作时": "The formula for the expected value is E(Y) = sum [y times p(y)]. This equation calculates the average outcome by multiplying each possible value of Y by its probability and then summing these products. This provides a measure of the central tendency of the distribution."
    },
    {
      "暂": "Now, let's proceed to calculate the expected value using the given probabilities and values."
    },
    {
      "写": "E(Y) = (0 times 0.25) + (1 times 0.50) + (2 times 0.25) = 0 + 0.50 + 0.50 = 1"
    },
    {
      "作时": "To find the expected value, we use the written formula. This calculation results in 1, which means that, on average, the value of Y is 1."
    },
    {
      "暂": "We'll now create a new image to represent the expected value on a separate graph. This will help us visualize where the average outcome falls in relation to the individual probabilities."
    },
    {
      "拉": "Create a new bar graph similar to the first one but include a vertical line to indicate the expected value of Y. Use the same x-axis values (0, 1, 2) and y-axis range (0 to 1). The vertical line should be positioned at Y=1, which represents the calculated expected value."
    },
    {
      "图": "Observe where the vertical line intersects the new bar graph. This line represents the expected value, providing a visual summary of the average outcome based on the probability distribution."
    },
    {
      "暂": "Finally, let's summarize what we've learned about probability distributions and expected values."
    },
    {
      "停": "We've explored how to visualize and calculate the probability distribution and expected value of a random variable. This understanding helps in predicting outcomes and making informed decisions based on probabilities."
    }
  ]
}

'''
