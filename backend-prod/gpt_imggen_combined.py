import os
import openai
import time
from PIL import Image, ImageDraw, ImageFont
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPEN_AI_KEY")

def generate_text(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content'].strip()

def parse_table(text):
    lines = text.split('\n')
    table = []
    for line in lines:
        if '|' in line and '---' not in line:
            table.append([col.strip() for col in line.split('|')[1:-1]])
    return table

def save_table_as_image(table, file_path=None):
    width, height = 1200, 600
    image = Image.new('RGB', (width, height), color=(255, 255, 255))

    draw = ImageDraw.Draw(image)

    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    text_position = (10, 10)
    text_color = (0, 0, 0)

    row_height = font.getbbox("A")[3] + 20

    for row_index, row in enumerate(table):
        y_text = text_position[1] + row_index * row_height
        for col_index, col in enumerate(row):
            x_text = text_position[0] + col_index * 200
            draw.text((x_text, y_text), col, font=font, fill=text_color)
            draw.rectangle(
                [x_text - 5, y_text - 5, x_text + 195, y_text + row_height - 5],
                outline=text_color
            )

    if file_path:
        image.save(file_path)
    
    return image

def write_mermaid_file(mermaid_code, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(mermaid_code)

def generate_png_from_mermaid(input_file, output_file=None):
    command = f"mmdc -i {input_file} -o temp_output.png -w 2400 -H 1200"
    os.system(command)

    # Ensure the output image is resized to the correct dimensions using Pillow
    with Image.open("temp_output.png") as img:
        img = img.resize((1200, 600), Image.Resampling.LANCZOS)  # Resize to 1200x600

        if output_file:
            img.save(output_file)
        img.save("resized_output.png")

    # Clean up temporary files
    os.remove("temp_output.png")

    return img

def generate_mermaid_code(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an assistant that generates Mermaid code for diagrams."},
            {"role": "user", "content": prompt}
        ]
    )
    mermaid_code = response['choices'][0]['message']['content']
    
    start_index = mermaid_code.find("```")
    if (start_index != -1):
        end_index = mermaid_code.find("```", start_index + 3)
        if (end_index != -1):
            mermaid_code = mermaid_code[start_index + 3:end_index].strip()
        else:
            print("End of code block not found")
    else:
            print("Start of code block not found")
    
    if mermaid_code.startswith("mermaid"):
        mermaid_code = mermaid_code[len("mermaid"):].strip()
    
    return mermaid_code

def analyze_prompt(prompt):
    keywords_table = ["table", "columns", "rows"]
    keywords_diagram = ["diagram", "mermaid", "flowchart", "graph"]
    
    if any(keyword in prompt.lower() for keyword in keywords_table):
        return "table"
    elif any(keyword in prompt.lower() for keyword in keywords_diagram):
        return "diagram"
    else:
        return "unknown"

def process_prompt(prompt):
    analysis_result = analyze_prompt(prompt)

    if analysis_result == "table":
        generated_text = generate_text(prompt)
        print(generated_text)
        table = parse_table(generated_text)
        image = save_table_as_image(table)
        print("Table processed.")
        return image
    elif analysis_result == "diagram":
        mermaid_code = generate_mermaid_code(prompt)
        if mermaid_code:
            print(f"Generated Mermaid code:\n{mermaid_code}")
            input_file = "diagram.mmd"
            output_file = "diagram.png"
            write_mermaid_file(mermaid_code, input_file)
            time.sleep(2)
            image = generate_png_from_mermaid(input_file)
            image.save(output_file)
            print("Diagram processed.")
            return image
        else:
            print("Failed to generate Mermaid code")
    else:
        print("Could not determine if the prompt is for a table or a diagram.")
        return None

def generate_python_code(prompt, context=''):
    global image
    image = None
    content = ''
    error = ''
    
    success = False 
    
    while not success:
        image = None
        
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": '''
                    You are given some context and a prompt. Your goal is to generate an image either using Pillow (for scenarios) or MatPlotLib by creating Python code that accurately represents the given prompt. Don't draw extraneous things that are not needed (gridlines on graphs for example). Additionally, make it generate as 640x480. Your raw output (unparsed) will be put into a compiler to run. Write the image to a variable called image that is of PIL type (convert MatPlotLib figure to PIL format by using the following code:
                    buf = io.BytesIO()
                    fig.savefig(buf, format='png')
                    buf.seek(0)
                    image = Image.open(buf)). 
                 
                    Do not run image.show() nor should you save the image to disk. If there are any containers such as boxes that include text, please make sure the text wraps around so that it does not go outside the box.
                 '''},

                {"role": "user", "content": "Context:\n" + context + "\Prompt:\n" + prompt + "\nError:" + error}
            ],
            stream=True
        )
        
        content = ''
        for chunk in response:
            content += chunk['choices'][0]['delta'].get('content', '')
        
        content = content[content.find('python') + 6:-3]
        content.replace('image.show()', '')

        try:
            exec(content, globals())
            if image is not None:
                success = True
                print("Image successfully generated!")

            else:
                print("Failed to generate image, trying again...")
                
        except Exception as e:
            error = str(e)
            print(f"Execution failed: {e}. Trying again...")
    
    return image