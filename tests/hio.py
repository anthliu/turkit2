import asyncio

from context import turkit2
from turkit2.common import HumanIO
from turkit2.primitive import IText, OText
from utils import get_client

client = get_client()

elements = [
    ('Prompt', IText()),
    ('Answer', OText('answer1')),
    ('Prompt2', IText()),
    ('Answer2', OText('answer2')),
]

task = HumanIO(client, elements, 'Test2', '0.01', 'test test', 600, 6000)

async def proc():
    parameters = {
        'Prompt': {'text': 'How are you?'},
        'Prompt2': {'text': 'Flip a coin.'},
    } 
    async for answer, assignment in task.ask_async(verbosity=100, parameters=parameters):
        print(answer)
        print(assignment)

asyncio.run(proc())
