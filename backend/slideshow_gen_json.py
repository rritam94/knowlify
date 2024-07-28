import urllib.request
import json
import os
import ssl
from pdf2image import convert_from_path
import pytesseract
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
        "max_tokens": 4096,
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
        for i in range(len(images)):
            print(f"Processing page {i}")
            text = pytesseract.image_to_string(images[i])
            print(f"Extracted text: {text[:500]}")  # Print first 500 characters of extracted text for debugging
            
            # Remove special characters and convert Greek letters to English
            clean_text = re.sub(r'[^a-zA-Z0-9\s.,;:!?\'"-]', '', text)
            clean_text = clean_text.replace('α', 'alpha').replace('β', 'beta').replace('γ', 'gamma').replace('δ', 'delta')  # Add more replacements as needed

            futures.append(executor.submit(complete_api_request, entire_prompt, clean_text))
        
        for i, future in enumerate(as_completed(futures)):
            content = future.result()
            pattern = re.compile(r'\[(.*?)\]', re.DOTALL)
            match = pattern.search(content)

            if content:
                json_str = match.group(0)
                total_json.append(json_str)

    total_json_str = "[" + ",".join(total_json) + "]"
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
- Describe the problem-solving process in a step-by-step manner.
- Provide detailed explanations for each step, breaking down new concepts or calculations thoroughly.
- Be specific and detailed in calculations.
- Describe what should be drawn or written on a whiteboard, keeping it concise.
- Use a clear, engaging, and conversational style suitable for educational content.
- Instead of using Greek letters, use the English translation when needed
- Example of the desired level of detail:
{
  "steps": [
    {"START": "Let's define the problem: finding the mean and standard deviation of Y."},
    {"WRITE": "E(Y) = 1/p' on the board."},
    {"DURING WRITING": "For a geometric distribution with p = 0.02, we calculate the mean."},
    {"WRITE": "E(Y) = 1/0.02' on the board."},
    {"DURING WRITING": "This simplifies to E(Y) = 50."},
    {"WRITE": "Standard Deviation = √(1-p)/p^2' on the board."},
    {"DURING WRITING": "Plugging in values gives Standard Deviation = √(1-0.02)/(0.02)^2."},
    {"WRITE": "Standard Deviation = 49.497'."}
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

For problem-solving slides, the steps should be a list of objects following this format (NOT JUST DIALOGUE!):
[
  {
    "title": "TITLE_OF_SLIDE",
    "bullet_points": ["POINT_1", "POINT_2", "POINT_3", ...],
    "steps": {
      [
        {"START": optional string},
        {"WRITE": required string},
        {"DRAW": optional string},
        {"DURING WRITING": optional string},
        {"PAUSE": optional string},
        {"STOP": optional string}
      ]
    }
  }
]

Ensure that all brackets, parentheses, and curly braces are properly opened and closed. The entire output should be presented as a comprehensive JSON structure, with each slide represented as an object containing a title, bullet points, and a transcript (either standard or problem-solving format). Please make sure that the steps key is only included within the JSON objects representing example problems. Do not restart generating the JSON randomly.
'''

# pdf_path = 'Statistics.pdf'

# with open('output2.txt', 'w', encoding='utf-8') as file:
#     file.write(generate_json(pdf_path))
