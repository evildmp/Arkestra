
from django.test import TestCase

from video.models import Video


class VideoTests(TestCase):
    def setUp(self):
        pass

class SimpleVideoTests(TestCase):
    def setUp(self):
        self.video = Video()

    def test_matches_file_type(self):
        self.assertTrue(self.video.matches_file_type('videofile.mp4', None, None))
        self.assertTrue(self.video.matches_file_type('~/videofile.mp4', None, None))
        self.assertTrue(self.video.matches_file_type('video file with spaces.mp4', None, None))
        self.assertTrue(self.video.matches_file_type('videofile.dv', None, None))
        self.assertTrue(self.video.matches_file_type('videofile.mov', None, None))
        self.assertTrue(self.video.matches_file_type('videofile.avi', None, None))
        self.assertTrue(self.video.matches_file_type('videofile.wmv', None, None))
        self.assertFalse(self.video.matches_file_type('videofile', None, None))
        self.assertFalse(self.video.matches_file_type('videofile.zzz', None, None))



