import boto3

from turkit2.common import HumanIO
from turkit2.primitive import IText, OText, IImage

endpoint = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
client = boto3.client('mturk',
   region_name='us-east-1',
   endpoint_url = endpoint
)

elements = [
    ('Prompt', IText()),
    ('Answer', OText('answer1')),
]

task = HumanIO(client, elements, 'Test', '0.01', 'test test', 600, 6000)

parameters = {
    'Prompt': {'text': 'How are you?'},
} 
print(task.preview(parameters=parameters))
