from keras.models import load_model

emotion_classifier = None
# https://github.com/oarriaga/face_classification
def get_model(path='/nomad/nomad/fer2013_mini_XCEPTION.102-0.66.hdf5'):
    global emotion_classifier
    if emotion_classifier is None:
        emotion_classifier = load_model(path, compile=False)
    return emotion_classifier


def preprocess_input(x, v2=True):
    x = x.astype('float32')
    x = x / 255.0
    if v2:
        x = x - 0.5
        x = x * 2.0
    return x
