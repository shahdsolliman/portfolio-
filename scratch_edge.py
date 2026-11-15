import cv2
import numpy as np
from PIL import Image

# Read image with alpha
img = cv2.imread(r'e:\PORTFOLIO\current_portrait.png', cv2.IMREAD_UNCHANGED)
print("Channels:", img.shape)

b, g, r, a = cv2.split(img)

# Let's inspect the alpha channel
# The user's screenshot shows the cutout boundary has jagged pixels, staircasing, and small dark holes/bumps.
# Standard professional technique for matte cleaning:
# 1. Morphological opening/closing on alpha to remove single-pixel holes and protruding jagged specks
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
a_clean = cv2.morphologyEx(a, cv2.MORPH_CLOSE, kernel)
# 2. Slight erosion (1 pixel) to eliminate dirty border fringe
a_eroded = cv2.erode(a_clean, kernel, iterations=1)
# 3. Guided filter or bilateral blur on alpha to keep sharp edges while removing pixel-staircasing
a_blur = cv2.GaussianBlur(a_eroded, (3, 3), 0.8)

# Merge back
cleaned_img = cv2.merge([b, g, r, a_blur])
cv2.imwrite(r'e:\PORTFOLIO\portrait_cleaned_cv.png', cleaned_img)
print("Cleaned with OpenCV successfully!")
