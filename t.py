
import matplotlib.pyplot as plt
import numpy as np
import io
from PIL import Image

# Data
issues = ['Students feeling disengaged', 'College students dropping out']
percentages = [53, 33]

# Create bar chart
fig, ax = plt.subplots(figsize=(8, 6))
bars = ax.bar(issues, percentages, color=['blue', 'orange'])

# Add title and labels
ax.set_title('Impact of Traditional Lectures on Students', fontsize=16)
ax.set_xlabel('Issues', fontsize=12)
ax.set_ylabel('Percentage of Students', fontsize=12)

# Annotate bars with percentages
for bar in bars:
    yval = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{yval}%', ha='center', va='bottom')

# Adjust the size of the figure
plt.xlim(-0.5, len(issues)-0.5)
plt.ylim(0, 60)

# Convert to PIL image
buf = io.BytesIO()
plt.savefig(buf, format='png')
buf.seek(0)
image = Image.open(buf)

import cv2
import numpy as np

def read_image(img):
    np_img = np.array(img)

    if np_img.ndim == 3:
        return cv2.cvtColor(np_img, cv2.COLOR_RGB2BGR)

    else:
        return np_img

def convert_to_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def increase_contrast(image):
    return cv2.equalizeHist(image)

def apply_threshold(image):
    gray_image = convert_to_grayscale(image)
    contrast_image = increase_contrast(gray_image)
    
    thresh = cv2.adaptiveThreshold(
        contrast_image, 
        255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 
        11,
        2   
    )
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    return thresh

def find_contours(thresh_image):
    contours, hierarchy = cv2.findContours(thresh_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    return contours, hierarchy

def get_contour_start_y(contour):
    return contour[0][0][1]

def get_contour_start_x(contour):
    return contour[0][0][0]

def sort_contours(contours):
    contours = sorted(contours, key=lambda c: get_contour_start_x(c))
    sorted_contours = []
    current_line = []
    current_y = None

    for contour in contours:
        contour_y = get_contour_start_y(contour)
        if current_y is None:
            current_y = contour_y
        if abs(contour_y - current_y) > 10:
            current_line = sorted(current_line, key=lambda c: get_contour_start_x(c))
            sorted_contours.extend(current_line)
            current_line = [contour]
            current_y = contour_y
        else:
            current_line.append(contour)

    if current_line:
        current_line = sorted(current_line, key=lambda c: get_contour_start_x(c))
        sorted_contours.extend(current_line)

    return sorted_contours

def get_contour_coordinates(contours, x_offset, y_offset):
    coords = []
    for contour in contours:
        for point in contour:
            coords.append((point[0][0] + x_offset, point[0][1] + y_offset))
    return coords

def draw_contours(image, contours):
    image = cv2.drawContours(image, contours, -1, (0, 255, 0), 1)
    cv2.imshow('Contours', image)
    cv2.waitKey(0)
    return image

def get_coordinates_from_processed_img(img, x_offset=0, y_offset=0):
    image = read_image(img)
    thresh_image = apply_threshold(image)
    contours, hierarchy = find_contours(thresh_image)
    sorted_contours = sort_contours(contours)
    coords = get_contour_coordinates(sorted_contours, x_offset, y_offset)
    
    # draw_contours(image, contours)
    print(coords)
    return coords

get_coordinates_from_processed_img(image)