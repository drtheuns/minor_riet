"""Run the application with any command line arguments.
self.statusBar().showMessage('Hello from statusbar')

You can run multiple parts of the program in one go,
and they will be executed in the proper sequence.

For example, if you run both the dataset sorted, as well as
the dataset preparation, the sorting process will go first before
preparing the dataset.
"""
import argparse

import emotionreader
from emotionreader.misc import parse_actions
from emotionreader.video import predict_from_webcam, predict_from_video
from emotionreader.model import sort_ck, prepare_dataset, train_model
from emotionreader.flask.app import run_webserver, initdb


def get_parser():
    parser = argparse.ArgumentParser(prog='emotionreader',
                                     description=emotionreader.__description__)
    parser.add_argument('-V', '--version', action='version',
                        version=emotionreader.__version__)

    subparsers = parser.add_subparsers(help='the action to perform')

    # Subcommand for sorting the dataset
    parser_sort = subparsers.add_parser('sort', help='sort the CK+ dataset')
    parser_sort.set_defaults(func=sort_ck)

    # Subcommand for preparing the dataset.
    parser_dataset = subparsers.add_parser('prepare-dataset', help='prepare '
                                           'the dataset by detecting faces and'
                                           ' cutting them to size')
    parser_dataset.set_defaults(func=prepare_dataset)

    # Subcommand for training the model
    parser_train = subparsers.add_parser('train', help='train the model')
    parser_train.add_argument('-m', '--measure', dest='measure',
                              action='store_true',
                              help='test accuracy of the model')
    parser_train.set_defaults(func=train_model)

    # Subcommand for starting emotion detection from the webcam
    parser_webcam = subparsers.add_parser('webcam', help='start real time'
                                          'detection from the command line')
    parser_webcam.add_argument('-d', '--dimensions', dest='dimensions',
                               action=parse_actions.DimensionAction,
                               default=(640, 480), help='the width and height '
                               'to start the webcam with')
    parser_webcam.add_argument('-l', '--landmarks', dest='landmarks',
                               action='store_true',
                               help='draw the facial landmarks on the frame')
    parser_webcam.set_defaults(func=predict_from_webcam)

    # Subcommand for predicting video from file
    parser_file = subparsers.add_parser('file', help='predict from file')
    parser_file.add_argument('path', help='the video file to predict from')
    parser_file.add_argument('-w', '--workers', dest='workers', default=4,
                             type=int, help='the amount of workers processes'
                             ' to start')
    parser_file.set_defaults(func=predict_from_video)

    # Subcommand for starting the GUI
    parser_gui = subparsers.add_parser('webserver',
                                       help='Start the webserver')
    parser_gui.add_argument('-d', '--debug', dest='debug',
                            action='store_true',
                            help='start in debug mode')
    parser_gui.set_defaults(func=run_webserver)

    # Subcommand for database operations
    parser_db = subparsers.add_parser('initdb', help='database operations')
    parser_db.set_defaults(func=initdb)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    args.func(args)
