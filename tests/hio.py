import asyncio

from context import turkit2
from turkit2.common import HumanIO
from turkit2.primitive import IText, OText
from utils import get_client

client = get_client()

elements = [
    ('Prompt', IText()),
    ('Answer', OText()),
    ('Prompt2', IText()),
    ('Answer2', OText()),
]

task = HumanIO(client, elements, 'Test2', '0.01', 'test test', 600, 6000)

async def proc():
    parameters = {
        'Prompt': {'text': 'How are you?'},
        'Answer': {'id_': 'Answer'},
        'Prompt2': {'text': 'Flip a coin.'},
        'Answer2': {'id_': 'Answer'}
    } 
    async for answer, assignment in task.ask_async(verbosity=100, parameters=parameters):
        print(answer)
        print(assignment)

asyncio.run(proc())
