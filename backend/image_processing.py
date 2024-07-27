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

def apply_threshold(gray_image):
    _, thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return thresh

def find_contours(thresh_image):
    contours, hierarchy = cv2.findContours(thresh_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    return contours, hierarchy

def filter_outer_contours(contours, hierarchy):
    outer_contours = []
    for i, contour in enumerate(contours):
        if hierarchy[0][i][3] == -1:
            outer_contours.append(contour)
    return outer_contours

def get_contour_start_y(contour):
    return contour[0][0][1]

def get_contour_start_x(contour):
    return contour[0][0][0]

def sort_contours(contours):
    # First sort by the x-coordinate
    contours = sorted(contours, key=lambda c: get_contour_start_x(c))
    # Then sort by the y-coordinate within each line
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
    cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
    return image

def get_coordinates_from_processed_img(img, x_offset=0, y_offset=0):
    image = read_image(img)
    gray_image = convert_to_grayscale(image)
    thresh_image = apply_threshold(gray_image)
    contours, hierarchy = find_contours(thresh_image)
    outer_contours = filter_outer_contours(contours, hierarchy)
    sorted_contours = sort_contours(outer_contours)
    coords = get_contour_coordinates(sorted_contours, x_offset, y_offset)

    image_with_contours = draw_contours(image, sorted_contours)
    cv2.imwrite('image_with_contours.png', image_with_contours)  

    return coords