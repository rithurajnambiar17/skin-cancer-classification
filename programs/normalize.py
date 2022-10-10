import cv2

def normalize(img):
    new_img = cv2.normalize(img, None,
                            alpha=0, beta=200, 
                            norm_type=cv2.NORM_MINMAX)
    return new_img