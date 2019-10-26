from context import turkit2

import boto3
from utils import get_s3
from turkit2.primitive import Image
from context import turkit2

# Retrieve a bucket's ACL
s3 = get_s3()

im = Image(s3, 'turkit-testing', 'imgs/dog2.jpg')
print(im.render())
