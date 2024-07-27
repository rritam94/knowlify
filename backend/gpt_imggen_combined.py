import os
import openai
import time
from PIL import Image, ImageDraw, ImageFont
from wand.image import Image as WandImage
import os

# Set your OpenAI API key
openai.api_key = os.getenv('OPEN_AI_KEY')

def generate_text(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4",
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
            table.append([col.strip() for col in line.split('|')[1:-1]])  # Split by '|' and strip spaces
    return table

def save_table_as_image(table, file_path=None):
    # Create an image with white background
    width, height = 1200, 600  # Fixed dimensions
    image = Image.new('RGB', (width, height), color=(255, 255, 255))

    draw = ImageDraw.Draw(image)

    # Use a truetype or opentype font
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except IOError:
        font = ImageFont.load_default()

    # Define text position and color
    text_position = (10, 10)
    text_color = (0, 0, 0)

    # Calculate row height
    row_height = font.getbbox("A")[3] + 20

    # Draw the table
    for row_index, row in enumerate(table):
        y_text = text_position[1] + row_index * row_height
        for col_index, col in enumerate(row):
            x_text = text_position[0] + col_index * 200
            draw.text((x_text, y_text), col, font=font, fill=text_color)
            # Draw cell borders
            draw.rectangle(
                [x_text - 5, y_text - 5, x_text + 195, y_text + row_height - 5],
                outline=text_color
            )

    # Save the image
    if file_path:
        image.save(file_path)
    
    return image

def write_mermaid_file(mermaid_code, output_file):
    with open(output_file, 'w') as file:
        file.write(mermaid_code)

def generate_png_from_mermaid(input_file, output_file=None):
    command = f"mmdc -i {input_file} -o temp_output.png -w 2400 -H 1200"
    os.system(command)

    # Ensure the output image is resized to the correct dimensions using Wand
    with WandImage(filename="temp_output.png") as img:
        img.resize(1200, 600)
        if output_file:
            img.save(filename=output_file)
        img.save(filename="resized_output.png")

    with Image.open("resized_output.png") as img:
        img = img.copy()  # To avoid potential file locking issues

    # Clean up temporary files
    os.remove("temp_output.png")
    os.remove("resized_output.png")

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
    
    # Extract the Mermaid code from the response
    start_index = mermaid_code.find("```")
    if start_index != -1:
        end_index = mermaid_code.find("```", start_index + 3)
        if end_index != -1:
            mermaid_code = mermaid_code[start_index + 3:end_index].strip()
        else:
            print("End of code block not found")
    else:
            print("Start of code block not found")
    
    # Remove any leading "mermaid" keyword
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
        # image.save("generated_table.png")  # Uncomment to save the image to file
        print("Table processed.")
        return image
    elif analysis_result == "diagram":
        mermaid_code = generate_mermaid_code(prompt)
        if mermaid_code:
            print(f"Generated Mermaid code:\n{mermaid_code}")
            input_file = "diagram.mmd"
            output_file = "diagram.png"
            write_mermaid_file(mermaid_code, input_file)
            time.sleep(2)  # Slight delay
            image = generate_png_from_mermaid(input_file)
            # image.save(output_file)  # Uncomment to save the image to file
            print("Diagram processed.")
            return image
        else:
            print("Failed to generate Mermaid code")
    else:
        print("Could not determine if the prompt is for a table or a diagram.")
        return None

if __name__ == "__main__":
    prompt = input("Enter your prompt: ")
    process_prompt(prompt)