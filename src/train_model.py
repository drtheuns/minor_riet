"""
This files handles the creation of a linear SVM machine learning model
that uses the dataset in ../data/dataset to train it (CK/CK+ dataset)

The facial recognition uses facial landmarks to detect emotions.

See also:
    http://www.paulvangent.com/2016/08/05/emotion-recognition-using-facial-landmarks/
"""
import glob
import itertools
import math
import random
import os.path
import pickle

import cv2
import dlib
import numpy as np
from sklearn.svm import SVC


# TODO: remove global variables
emotions = ['anger', 'contempt', 'disgust', 'fear', 'happiness', 'neutral', 'sadness', 'surprise']
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
clf = SVC(kernel='linear', probability=True, tol=1e-3)
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('../models/shape_predictor_68_face_landmarks.dat')

data = {}


def get_files(emotion):
    files = glob.glob('../data/dataset/%s/*' % emotion)
    random.shuffle(files)
    training = files[:int(len(files) * 0.8)]
    prediction = files[-int(len(files) * 0.2):]
    return training, prediction


def get_landmarks(image):
    detections = detector(image, 1)
    for k, d in enumerate(detections):
        shape = predictor(image, d)
        xlist = []
        ylist = []

        for i in range(1, 68):
            xlist.append(float(shape.part(i).x))
            ylist.append(float(shape.part(i).y))

        xmean = np.mean(xlist)
        ymean = np.mean(ylist)
        xcentral = [(x-xmean) for x in xlist]
        ycentral = [(y-ymean) for y in ylist]

        landmarks_vectorised = []
        for x, y, w, z in zip(xcentral, ycentral, xlist, ylist):
            landmarks_vectorised.append(w)
            landmarks_vectorised.append(z)
            meannp = np.asarray((ymean, xmean))
            coornp = np.asarray((z, w))
            dist = np.linalg.norm(coornp - meannp)
            landmarks_vectorised.append(dist)
            landmarks_vectorised.append(int(math.atan((y-ymean) / (x-xmean)) * 360/math.pi))

        data['landmarks_vectorised'] = landmarks_vectorised
    if len(detections) < 1: 
        data['landmarks_vectorised'] = "error"

    return data['landmarks_vectorised']


def read_image(path):
    if not os.path.isfile(path):
        print('failed to read with image %s' % path)
        return

    image = cv2.imread(path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe_image = clahe.apply(gray)
    get_landmarks(clahe_image)


def make_sets():
    training_data = []
    training_labels = []
    prediction_data = []
    prediction_labels = []
    for emotion in emotions:
        print('working on %s' % emotion)
        training, prediction = get_files(emotion)
        # Append data to training and prediction list and generate labels 0-7
        for item in training:
            read_image(item)
            if data['landmarks_vectorised'] == 'error':
                print('no face detected on this one')
            else:
                training_data.append(data['landmarks_vectorised'])
                training_labels.append(emotions.index(emotion))

        for item in prediction:
            read_image(item)
            if data['landmarks_vectorised'] == 'error':
                print('no face detected on this one')
            else:
                prediction_data.append(data['landmarks_vectorised'])
                prediction_labels.append(emotions.index(emotion))

    return training_data, training_labels, prediction_data, prediction_labels


def make_model():
    model = SVC(kernel='linear', probability=True, tol=1e-3)
    training_data, training_labels, prediction_data, prediction_labels = make_sets()
    npar_train = np.array(training_data)
    model.fit(npar_train, training_labels)
    return model


def measure_accuracy():
    accur_lin = []
    for i in range (0, 10):
        print('Making sets %s' % i)
        training_data, training_labels, prediction_data, prediction_labels = make_sets()

        npar_train = np.array(training_data)
        npar_trainlabs = np.array(training_labels)
        print('training SVM linear %s' % i)
        clf.fit(npar_train, training_labels)

        print('getting accurary')
        npar_pred = np.array(prediction_data)
        pred_lin = clf.score(npar_pred, prediction_labels)
        print('linear: ', pred_lin)
        accur_lin.append(pred_lin)

    print('mean value lin svm: %s' % np.mean(accur_lin))


def save_trained_model():
    model = make_model()
    with open('../models/trained_svm_model', 'wb+') as f:
        pickle.dump(model, f)


if __name__ == '__main__':
    # measure_accuracy()
    save_trained_model()

