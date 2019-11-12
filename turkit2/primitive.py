import os
from pathlib import Path
import yaml

class IImage(object):
    def __init__(self, s3client, bucket: str):
        '''
        '''
        self.client = s3client
        self.bucket = bucket
        self.urls = {}

    def _upload(self, path):
        assert path not in self.urls
        key = 'turkit2/' + path
        response = self.client.upload_file(
            path, self.bucket, key,
            ExtraArgs={'ACL':'public-read'}
        )
        # TODO handle errors
        bucket_location = self.client.get_bucket_location(Bucket=self.bucket)['LocationConstraint']
        self.urls[path] = f"https://s3-{bucket_location}.amazonaws.com/{self.bucket}/{key}"
        return response

    def render(self, path):
        if path not in self.urls:
            self._upload(path)

        return f'<img src={self.urls[path]}>'

class IText(object):
    def render(self, text):
        return f'<p>{text}</p>'

class OText(object):
    def __init__(self, id_):
        self.id_ = id_
    def render(self):
        return f"<p><textarea name='{self.id_}' cols='80' rows='3'></textarea></p>"
