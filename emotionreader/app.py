"""Run the application with any command line arguments.

You can run multiple parts of the program in one go,
and they will be executed in the proper sequence.

For example, if you run both the dataset sorted, as well as
the dataset preparation, the sorting process will go first before
preparing the dataset.
"""
import argparse

import emotionreader
from emotionreader.misc import parse_actions
from emotionreader.webcam import predict_from_webcam
from emotionreader.sorter import sort_ck


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
    # parser_dataset = subparsers.add_parser('prepare-dataset', help='prepare',
            # 'the dataset by detecting faces and cutting them to size')
    
    # Subcommand for starting emotion detection from the webcam
    parser_webcam = subparsers.add_parser('webcam', help='start real time'
            'detection from the command line')
    parser_webcam.add_argument('-d', '--dimensions', dest='dimensions',
            action=parse_actions.DimensionAction, default=(640, 480),
            help='the width and height to start the webcam with')
    parser_webcam.add_argument('-l', '--landmarks', dest='landmarks',
            action='store_true', help='draw the facial landmarks on the frame')
    parser_webcam.set_defaults(func=predict_from_webcam)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()
    args.func(args)

