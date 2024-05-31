# coding: utf8

import cv2
import numpy as np
import pyautogui
import time
import keyboard

# Function to check if ESC key is pressed
def check_esc_key():
    if keyboard.is_pressed('esc'):
        print("ESC pressed, stopping the script.")
        exit()

time.sleep(3)

image = cv2.imread('testing.png')

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

_, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Function to get the y-coordinate of the contour
def get_contour_start_y(contour):
    return contour[0][0][1]

# Sort contours from top to bottom based on the y-coordinate of their starting point
contours = sorted(contours, key=get_contour_start_y)

# Now sort each line of contours from left to right
def sort_contours_line_by_line(contours):
    sorted_contours = []
    current_line = []
    current_y = None

    for contour in contours:
        contour_y = get_contour_start_y(contour)
        if current_y is None:
            current_y = contour_y
        if abs(contour_y - current_y) > 10:  # Adjust this threshold as needed
            # Sort the current line by x-coordinate
            current_line = sorted(current_line, key=lambda c: c[0][0][0])
            sorted_contours.extend(current_line)
            current_line = [contour]
            current_y = contour_y
        else:
            current_line.append(contour)

    # Sort and add the last line
    if current_line:
        current_line = sorted(current_line, key=lambda c: c[0][0][0])
        sorted_contours.extend(current_line)
    
    return sorted_contours

contours = sort_contours_line_by_line(contours)

x_offset = 300
y_offset = 500

for contour in contours:
    check_esc_key()  # Check if ESC is pressed before starting each contour
    epsilon = 0.01 * cv2.arcLength(contour, True)
    approx = cv2.approxPolyDP(contour, epsilon, True)
    
    # Start drawing from the first point in the contour
    first_point = approx[0][0]
    pyautogui.moveTo(first_point[0] + x_offset, first_point[1] + y_offset)
    
    # Draw the contour by dragging the mouse to each point
    for point in approx:
        check_esc_key()  # Check if ESC is pressed during drawing
        pyautogui.dragTo(point[0][0] + x_offset, point[0][1] + y_offset, button='left', duration=0.01)

pyautogui.sleep(5)
