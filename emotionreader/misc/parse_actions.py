"""Custom argparse actions are defined here"""
from argparse import Action
import re


class DimensionAction(Action):
    """Handles splitting video frame dimensions in the form of WIDTHxHEIGHT
    into a tuple of the width and height
    """
    def __init__(self, option_strings, dest, nargs=1, **kwargs):
        if nargs != 1:
            raise ValueError('only nargs value of \'1\' is allowed')
        super(DimensionAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        match = re.search(r'(\d{3,4})[xX](\d{3,4})', values)
        if not match:
            raise ValueError('invalid dimensions. expected format WIDTHxHEIGHT'
                    'but got {}'.format(values))
        width, height = int(match.group(1)), int(match.group(2))
        setattr(namespace, self.dest, (width, height))
