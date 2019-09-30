from typing import List

class RemoteImage(object):
    def __init__(self, url):
        self.url = url
    def render(self):
        return self.url

class LocalImage(object):
    def __init__(self, s3bucket, path, persistant=False, persistant_time):
        self.s3bucket = s3bucket
