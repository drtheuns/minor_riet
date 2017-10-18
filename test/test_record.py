import json
import unittest
import tempfile
import os
import subprocess

from emotionreader.webcam import record


class TestRecordVideo(unittest.TestCase):

    def setUp(self):
        self.file = tempfile.NamedTemporaryFile(delete=False, suffix='.avi')
        frames = record(self.file.name, 5)
        self.file.close()
        self._get_video_metadata()

    def tearDown(self):
        os.unlink(self.file.name)

    def _get_video_metadata(self):
        command = [
            'ffprobe', '-show_format', '-print_format', 'json', '-loglevel',
            'quiet', self.file.name
        ]
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res, err = p.communicate()
        self._metadata = json.loads(res)

    def test_video_duration(self):
        duration = self._metadata.get('format', {}).get('duration', None)
 
        self.assertIsNotNone(duration)
        self.assertEqual(duration, '5.000000', 'video is not of expected length')

