import urllib.request
import json
import os
import ssl
from pdf2image import convert_from_path
import pytesseract
import time
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def allowSelfSignedHttps(allowed):
    if allowed and not os.environ.get('PYTHONHTTPSVERIFY', '') and getattr(ssl, '_create_unverified_context', None):
        ssl._create_default_https_context = ssl._create_unverified_context

allowSelfSignedHttps(True)

def complete_api_request(prompt, pdf):
    data = {
        "messages": [
            {"role": "system", "content": prompt},
            {"role": "user", "content": pdf}
        ],
        "max_tokens": 5500,
        "temperature": 0.8,
        "top_p": 0.1,
        "best_of": 1,
        "presence_penalty": 0,
        "use_beam_search": "false",
        "ignore_eos": "false",
        "skip_special_tokens": "false",
        "logprobs": "false"
    }

    body = str.encode(json.dumps(data))
    url = 'https://knowlify-serverless.eastus2.inference.ai.azure.com/v1/chat/completions'
    api_key = 'r969yiozSSSCFTZDwuBRU2gje26A0Dac'

    if not api_key:
        raise Exception("A key should be provided to invoke the endpoint")

    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + api_key}
    req = urllib.request.Request(url, body, headers)

    try:
        response = urllib.request.urlopen(req)
        result = response.read()
        if not result:
            raise Exception("Empty response received from the API")
        
        json_string = result.decode('utf-8')
        if not json_string.strip():
            raise Exception("Empty JSON string received from the API")
        
        data = json.loads(json_string)
        message_content = data['choices'][0]['message']['content']
        return message_content

    except urllib.error.HTTPError as error:
        print("The request failed with status code: " + str(error.code))
        print(error.info())
        print(error.read().decode("utf8", 'ignore'))
        return None
    except json.JSONDecodeError as e:
        print("Error decoding JSON response: " + str(e))
        print("Raw response: " + result.decode('utf-8'))
        return None

def generate_json(pdf_path):
    images = convert_from_path(pdf_path)
    text = ''
    total_json = []

    with ThreadPoolExecutor() as executor:
        futures = []
        for i in range(0, len(images), 2):
            if i == len(images) - 1:
                text = pytesseract.image_to_string(images[i])
                clean_text = re.sub(r'[^a-zA-Z0-9\s.,;:!?\'"-]', '', text)
                clean_text = clean_text.replace('α', 'alpha').replace('β', 'beta').replace('γ', 'gamma').replace('δ', 'delta')

            else:
                text = pytesseract.image_to_string(images[i])
                text += pytesseract.image_to_string(images[i + 1])
                clean_text = re.sub(r'[^a-zA-Z0-9\s.,;:!?\'"-]', '', text)
                clean_text = clean_text.replace('α', 'alpha').replace('β', 'beta').replace('γ', 'gamma').replace('δ', 'delta')

            futures.append(executor.submit(complete_api_request, entire_prompt, clean_text))
        
        for i, future in enumerate(as_completed(futures)):
            content = future.result()
            content_clipped = ''
            start = False

            if content:
                for char in content:
                    if char == '[' and not start:
                        start = True

                    elif start:
                        content_clipped += char

                total_json.append(content_clipped[0:-1])

    total_json_str = '[' + ",".join(total_json) + ']'
    return total_json_str


entire_prompt = '''
You are responsible for creating at max 2 informational presentation slides based on the provided text

Generate:
1. Informative slide titles that accurately reflect the main idea of each section.
2. Bullet points summarizing the key points for each slide.
3. If we have a general informational slide, a detailed transcript that explains the content in-depth should be generated. If it is an example problem slide, then a json object called "steps" should be generated.

As mentioned, slides will be split up into general informational content and example problems.

For general informational content:
- Ensure all symbols and special characters are correctly represented.
- Thoroughly cover all the material from the text within the slides.
- The transcript should expand on the bullet points, offering detailed explanations, examples, and insights to enhance understanding.
- Make sure the transcript continues smoothly from previous slides without repeating introductory phrases.
- Do not reference non-existent images or tables

For example problems:
- Instead of a transcript key, you should use "steps"
- The steps key should be a list of steps required to solve the problem (Use the following indicators where appropriate: START, WRITE, DRAW, DURING WRITING, PAUSE, STOP). It should not just be dialogue.
- Describe the problem-solving process in a step-by-step manner to the point where a child could understand how to solve it.
- Provide detailed explanations for each step, breaking down new concepts or calculations thoroughly.
- Be specific and detailed in calculations.
- Describe what should be drawn or written on a whiteboard, keeping it concise.
- Use a clear, engaging, and conversational style suitable for educational content.
- Do not reference non-existent images or tables
- Reflect the entire problem statement within the bullet points
- Example of the desired level of detail:
{
    "title": "Example 6.29: Finding the Center of Mass of Objects along a Line",
    "bullet_points": ["Four point masses are placed on a number line", "m1 = 30 kg, placed at x1 = −2 m", "m2 = 5 kg, placed at x2 = 3 m", "m3 = 10 kg, placed at x3 = 6 m", "m4 = 15 kg, placed at x4 = −3 m", "Find the moment of the system with respect to the origin and the center of mass of the system"],
    "steps": [
      {"START": "Let's begin by understanding the problem. We are given four point masses placed at different positions along a number line."},
      {"WRITE": "m1 = 30 kg, x1 = −2 m"},
      {"DURING WRITING": "This means we have a mass of 30 kilograms placed 2 meters to the left of the origin."},
      {"WRITE": "m2 = 5 kg, x2 = 3 m"},
      {"DURING WRITING": "Here, a smaller mass of 5 kilograms is positioned 3 meters to the right of the origin."},
      {"WRITE": "m3 = 10 kg, x3 = 6 m"},
      {"DURING WRITING": "Next, we have a 10 kilogram mass placed 6 meters to the right."},
      {"WRITE": "m4 = 15 kg, x4 = −3 m"},
      {"DURING WRITING": "Finally, a 15 kilogram mass is 3 meters to the left of the origin."},
      {"PAUSE": "Now, let's think about what we need to do next. We want to find the moment of the system with respect to the origin. Remember, the moment is like the 'turning force' caused by these masses about the origin. It's calculated by multiplying each mass by its distance from the origin."},
      {"WRITE": "M = ∑(m_i x_i) = −60 + 15 + 60 − 45 = −30"},
      {"DURING WRITING": "Let's break it down: for each mass, we multiply it by its position and then add all these values together. We get a total moment of -30."},
      {"PAUSE": "A negative moment means that if we imagine a seesaw, the left side is heavier. Now, let's calculate the total mass of the system."},
      {"WRITE": "m = ∑ m_i = 30 + 5 + 10 + 15 = 60 kg"},
      {"DURING WRITING": "This is simply adding up all the individual masses. So, the total mass is 60 kilograms."},
      {"PAUSE": "With both the moment and the total mass known, we can now find the center of mass. This tells us where to place a fulcrum to balance all the masses."},
      {"WRITE": "x̄ = M / m = −30 / 60 = −1/2"},
      {"DURING WRITING": "We divide the moment by the total mass. The result, -1/2, means the center of mass is half a meter to the left of the origin."},
      {"STOP": "So, if you placed a fulcrum at this point, the entire system would be perfectly balanced!"}
    ]
  }

YOUR OUTPUT MUST BE A JSON FILE IN THE FOLLOWING FORMAT. EACH JSON OBJECT IS ITS OWN SLIDE:
[
  {
    "title": "TITLE_OF_SLIDE",
    "bullet_points": ["POINT_1", "POINT_2", "POINT_3", ...],
    "transcript" or "steps": "TRANSCRIPT_FOR_SLIDE" or "STEPS_FOR_SLIDE"
  }
]

Ensure that all brackets, parentheses, and curly braces are properly opened and closed. The entire output should be presented as a comprehensive JSON structure, with each slide represented as an object containing a title, bullet points, and a transcript (either standard or problem-solving format). Please make sure that the steps key is only included within the JSON objects representing example problems. Do not restart generating the JSON randomly.
'''

# pdf_path = 'Statistics.pdf'

# current_time = time.time()

# with open('output2.txt', 'w', encoding='utf-8') as file:
#     file.write(generate_json(pdf_path))

# print(time.time() - current_time)
