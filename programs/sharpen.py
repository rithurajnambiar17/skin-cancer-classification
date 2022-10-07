import cv2
import numpy as np

def sharpen(img):
    kernel_sharpening = np.array([
                            [-1,-1,-1], 
                            [-1,9,-1], 
                            [-1,-1,-1]])
    new_img = cv2.filter2D(img, -1, kernel_sharpening)
    return new_img