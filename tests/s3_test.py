import boto3
from utils import get_s3
from turkit2.primitive import IImage
from context import turkit2

# Retrieve a bucket's ACL
s3 = get_s3(profile='anthony')

im = IImage(s3, 'turkit-testing')
print(im.render('imgs/dog2.jpg'))
