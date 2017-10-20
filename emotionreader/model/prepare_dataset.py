import cv2
import glob


def detect_faces(emotion, face_detectors):
    """Process all images of one emotion

    Args:
        emotion: The emotion to process
        face_detectors: The opencv haarcascade classifiers to be used
    """
    print('working on %s' % emotion)
    files = glob.glob("data/sorted_set/%s/*" % emotion)
    print('%s has %d files' % (emotion, len(files)))

    for num, f in enumerate(files):
        frame = cv2.imread(f)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Try to detect a face, using 4 different face detectors.
        faces = [det.detectMultiScale(
                 gray, scaleFactor=1.1, minNeighbors=10, minSize=(5, 5),
                 flags=cv2.CASCADE_SCALE_IMAGE)
                 for det in face_detectors]

        # Go over detected faces, stop at the first one.
        facefeatures = next((f for f in faces if len(f) == 1), None)
        if facefeatures is None:
            continue

        # Cut and save face
        for (x, y, w, h) in facefeatures:
            print("face found in file: %s" % f)
            gray = gray[y:y+h, x:x+w]  # Cut the frame to size

            try:
                out = cv2.resize(gray, (350, 350))
                cv2.imwrite("data/dataset/%s/%s.jpg" % (emotion, num), out)
            except Exception as e:
                print('error occured: ', e)


def prepare_dataset(args):
    emotions = ["neutral", "anger", "contempt", "disgust",
                "fear", "happy", "sadness", "surprise"]
    face_detectors = [
        cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml'),
        cv2.CascadeClassifier('models/haarcascade_frontalface_alt.xml'),
        cv2.CascadeClassifier('models/haarcascade_frontalface_alt2.xml'),
        cv2.CascadeClassifier('models/haarcascade_frontalface_alt_tree.xml')
    ]

    for emotion in emotions:
        detect_faces(emotion, face_detectors)
