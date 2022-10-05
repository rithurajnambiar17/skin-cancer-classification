import numpy as np
import tensorflow as tf

def reshapeImage(image):

    image = tf.keras.preprocessing.image.smart_resize(
    image, (225, 225), interpolation='nearest'
    )
    image = np.reshape(image, (1, 225,225,3))
    return image
    