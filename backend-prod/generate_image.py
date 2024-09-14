from PIL import Image, ImageDraw, ImageFont

X_DIMENSION = 3400
Y_DIMENSION = 4400
PRIMARY_FONT_PATH = 'Caveat-VariableFont_wght.ttf'
FALLBACK_FONT_PATH = 'DejaVuSans.ttf'
FONT_SIZE = 20

PRIMARY_FONT = ImageFont.truetype(PRIMARY_FONT_PATH, FONT_SIZE)
FALLBACK_FONT = ImageFont.truetype(FALLBACK_FONT_PATH, FONT_SIZE)

def create_image(width=X_DIMENSION, height=Y_DIMENSION):
    image = Image.new('RGB', (width, height), 'white')
    return image

def wrap_text(draw, text, max_width, font):
    lines = []
    words = text.split()
    line = ''
    for word in words:
        test_line = f'{line}{word} '
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] > max_width:
            if line:
                lines.append(line.strip())
            line = f'{word} '
        else:
            line = test_line
    if line:
        lines.append(line.strip())
    return lines

def supports_character(font, character):
    test_image = Image.new('RGB', (10, 10), 'white')
    draw = ImageDraw.Draw(test_image)
    
    try:
        draw.text((0, 0), character, font=font, fill='black')
        return True
    
    except UnicodeEncodeError:
        return False

def add_text_to_image(image, text, max_width, y_start=None):
    draw = ImageDraw.Draw(image)
    
    lines = wrap_text(draw, text, max_width, PRIMARY_FONT)

    text_height = len(lines) * FONT_SIZE

    if y_start is None:
        y_start = (Y_DIMENSION - text_height) / 2

    for line in lines:
        x_start = (X_DIMENSION - draw.textbbox((0, 0), line, font=PRIMARY_FONT)[2]) / 2
        y_position = y_start
        
        for char in line:
            font = PRIMARY_FONT if supports_character(PRIMARY_FONT, char) else FALLBACK_FONT
            
            draw.text((x_start, y_position), char, font=font, fill='black')
            x_start += draw.textbbox((0, 0), char, font=font)[2]

        y_start += FONT_SIZE

    return y_start

def add_image_to_image(background_image, image_to_add, y_start=None):
    background_width, background_height = background_image.size
    add_width, add_height = image_to_add.size

    if y_start is None:
        y_start = (background_height - add_height) / 2

    x_start = (background_width - add_width) / 2

    background_image.paste(image_to_add, (int(x_start), int(y_start)))

    y_start += add_height

    return y_start
