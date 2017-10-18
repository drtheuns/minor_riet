"""
Sort the CK+ dataset into the corresponding emotions.

Before running the file, make sure you have done the following:
    - In data/ make two folders `source_emotions` and `source_images`.
      source_images contains the CK+ images, and source_emotions has the labels
    - Make a third folder `sorted_set` with subfolders for each emotions
      (sorted_set/anger, sorted_set/happy, etc)
    - Add the folders of the CK+ images/labels to the right folders (S005, S010, etc)

Once the above is done, the program can be run.

The images from CK+ will be sorted into the right folders based on the emotions
described in the label. Once this is done, you can run the `prepare_dataset.py` file
to crop the faces and prepare the files so they can be used to train a model.
"""
import glob
from shutil import copyfile


emotions = ["neutral", "anger", "contempt", "disgust", "fear",
            "happy", "sadness", "surprise"]


def sorted_glob(pattern):
    return sorted(glob.glob(pattern))


def handle_file(filepath, session):
    with open(filepath, 'r') as f:
        emotion = int(float(f.readline()))
        session_files = sorted_glob('data/source_images/%s/*' % session)
        src_emotion = session_files[-1]
        src_neutral = session_files[0]
        dest_emotion = 'data/sorted_set/%s/%s' % (emotions[emotion], src_emotion[29:])
        dest_neutral = 'data/sorted_set/neutral/%s' % src_neutral[29:]
        copyfile(src_neutral, dest_neutral)
        copyfile(src_emotion, dest_emotion)

def sort_ck(args):
    #Returns a list of all folders with participant numbers
    participants = sorted_glob('data/source_emotions/*')

    for x in participants:
        part = "%s" % x[-4:]
        ls_sessions = sorted_glob('%s/*' % x)
        for sessions in ls_sessions:
            ls_files = sorted_glob('%s/*' % sessions)
            for files in ls_files:
                current_session = files[21:-30]
                handle_file(files, current_session) 

