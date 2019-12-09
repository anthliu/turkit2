import os
from pathlib import Path
import yaml

class IImage(object):
    """
    An input image primitive. The image is uploaded to an s3 bucket, so it can be rendered in the task.

    :param s3client: boto3 s3 client
    :param bucket: name of the s3 bucket to upload images to
    """
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

    def render(self, arg):
        """
        Called during HumanIO.ask. Need to pass in the correct type to the right ID (specified when initializing the HumanIO. Renders an image from the local path specified.

        :param arg: The argument specified to this primitive's ID in HumanIO.ask
        :type arg: str (path)
        """
        if arg not in self.urls:
            self._upload(arg)

        return f'<img src={self.urls[arg]}>'

class IText(object):
    """
    An input text primitive. (Plain <p> text).
    """
    def render(self, arg):
        """
        Called during HumanIO.ask. Need to pass in the correct type to the right ID (specified when initializing the HumanIO. Renders plain <p> text

        :param arg: The argument specified to this primitive's ID in HumanIO.ask
        :type arg: str
        """
        return arg

class OText(object):
    """
    An output text primitive. (Plain text box for worker output).

    :param id_: ID of the text box (used for parsing output)
    :type id_: str
    """
    def __init__(self, id_):
        self.id_ = id_
    def render(self):
        """
        Called during HumanIO.ask. Renders worker output text box
        """
        return f"<p><textarea name='{self.id_}' cols='80' rows='3'></textarea></p>"

class OChoice(object):
    """
    An output radio button primitive.

    :param id_: ID of the radio button (used for parsing output)
    :type id_: str
    """
    def __init__(self, id_):
        self.id_ = id_
    def render(self, arg):
        """
        Called during HumanIO.ask. Renders worker radio buttons
        """
        return '\n'.join(
            f'<input type="radio" name="{self.id_}" value="{choice}" id="radio" onclick="radioclick()" checked>{choice}<br>'
            for choice in arg
        )
