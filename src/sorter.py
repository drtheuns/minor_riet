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

emotions = ["neutral", "anger", "contempt", "disgust", "fear", "happy", "sadness", "surprise"] #Define emotion order
participants = glob.glob("../data/source_emotions/*") #Returns a list of all folders with participant numbers
participants.sort()

for x in participants:
    part = "%s" %x[-4:]
    ls_sessions = glob.glob('%s/*' % x)
    ls_sessions.sort()
    for sessions in ls_sessions:
        ls_files = glob.glob('%s/*' % sessions)
        ls_files.sort()
        for files in ls_files:
            current_session = files[20:-30]
            file = open(files, 'r')
            
            emotion = int(float(file.readline())) #emotions are encoded as a float, readline as float, then convert to integer.
            
            session_files = glob.glob("../data/source_images/%s/*" % current_session) #get path for last image in sequence, which contains the emotion
            session_files.sort()
            sourcefile_emotion = session_files[-1]
            sourcefile_neutral = session_files[0]
            
            dest_neut = "../data/sorted_set/neutral/%s" %sourcefile_neutral[29:] #Generate path to put neutral image
            dest_emot = "../data/sorted_set/%s/%s" %(emotions[emotion], sourcefile_emotion[29:]) #Do same for emotion containing image
            
            copyfile(sourcefile_neutral, dest_neut) #Copy file
            copyfile(sourcefile_emotion, dest_emot) #Copy file
