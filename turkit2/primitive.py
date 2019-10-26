import os
from pathlib import Path
import yaml

class Image(object):
    def __init__(self, s3client, bucket: str, path: str, url_time: int=24*60*60):
        '''
        '''
        self.client = s3client
        self.bucket = bucket
        self.path = path
        self.url = None
        self.url_time = url_time
        self.key = 'turkit2/' + self.path
        self.uploaded = False

    def _upload(self):
        response = self.client.upload_file(
            self.path, self.bucket, self.key,
            ExtraArgs={'ACL':'public-read'}
        )
        return response

    def render(self):
        if not self.uploaded:
            self._upload()
            self.uploaded = True

            bucket_location = self.client.get_bucket_location(Bucket=self.bucket)['LocationConstraint']
            
            self.url = f"https://s3-{bucket_location}.amazonaws.com/{self.bucket}/{self.key}"

        assert self.url
        return self.url
