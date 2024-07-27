from PIL import Image, ImageDraw, ImageFont

X_DIMENSION = 600
Y_DIMENSION = 400
FONT_PATH = 'Caveat-VariableFONT_wght.ttf'
FONT_SIZE = 20

FONT = ImageFont.truetype(FONT_PATH, FONT_SIZE)

def create_image(width=X_DIMENSION, height=Y_DIMENSION):
    image = Image.new('RGB', (width, height), 'white')
    return image

def wrap_text(draw, text, max_width):
    lines = []
    words = text.split()
    while words:
        line = ''
        while words and draw.textbbox((0, 0), line + words[0], font=FONT)[2] <= max_width:
            line += words.pop(0) + ' '
        lines.append(line.strip())
    return lines

def add_text_to_image(image, text, max_width, y_start=None):
    draw = ImageDraw.Draw(image)
    
    lines = wrap_text(draw, text, max_width)

    text_height = len(lines) * FONT_SIZE

    if y_start is None:
        y_start = (Y_DIMENSION - text_height) / 2

    for line in lines:
        text_bbox = draw.textbbox((0, 0), line, font=FONT)
        text_width = text_bbox[2] - text_bbox[0]
        x_start = (X_DIMENSION - text_width) / 2
        draw.text((x_start, y_start), line, font=FONT, fill='black')
        y_start += FONT_SIZE

    return int(y_start)

def add_image_to_image(image, image_to_add_path, text_end_y):
    image_to_add = Image.open(image_to_add_path)
    position = (int((X_DIMENSION - image_to_add.width) // 2), text_end_y)
    image.paste(image_to_add, position, image_to_add.convert('RGBA'))
    return image

# image = create_image(X_DIMENSION, Y_DIMENSION)
# image_2 = create_image(X_DIMENSION, Y_DIMENSION)


text = "Write 'E(Y) = 1/p' on the board. Jon is cool!"
text_2 = "E(Y) = 1/0.02"
text_end_y = add_text_to_image(image, text, X_DIMENSION, y_start=50)
text_end_y2 = add_text_to_image(image_2, text_2, X_DIMENSION, text_end_y + 10)

# # image_with_local_image = add_image_to_image(image, 'gray_image.png', text_end_y)
# image.save('final_image.png')
# image_2.save('final_image2.png')
