import asyncio

from turkit2.common import HumanIO
from turkit2.primitive import IText, OText, IImage
from utils import get_client, get_s3

s3 = get_s3(profile='anthony')
im = IImage(s3, 'turkit-testing')

client = get_client()

elements = [
    ('Prompt', IText()),
    ('Answer', OText('answer1')),
    ('Prompt2', IText()),
    ('Answer2', OText('answer2')),
    ('Prompt3', im),
    ('Answer2', OText('answer3')),
]

task = HumanIO(client, elements, 'Test2', '0.01', 'test test', 600, 6000)

async def proc():
    parameters = {
        'Prompt': {'text': 'How are you?'},
        'Prompt2': {'text': 'Flip a coin.'},
        'Prompt3': {'path': 'imgs/dog2.jpg'},
    } 
    async for answer, assignment in task.ask_async(verbosity=100, parameters=parameters):
        print(answer)
        print(assignment)

asyncio.run(proc())
