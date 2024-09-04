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

def apply_threshold(image):
    non_white_mask = cv2.inRange(image, (0, 0, 0), (254, 254, 254))
    
    gray_image = convert_to_grayscale(image)
    
    _, thresh = cv2.threshold(gray_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    thresh = cv2.bitwise_and(thresh, thresh, mask=non_white_mask)
    
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
    image = cv2.drawContours(image, contours, -1, (0, 255, 0), 2)
    cv2.imshow('Hello', image)
    cv2.waitKey(0)
    return image

def get_coordinates_from_processed_img(img, x_offset=0, y_offset=0):
    image = read_image(img)
    thresh_image = apply_threshold(image)
    contours, hierarchy = find_contours(thresh_image)
    sorted_contours = sort_contours(contours)
    coords = get_contour_coordinates(sorted_contours, x_offset, y_offset)
    return coords

