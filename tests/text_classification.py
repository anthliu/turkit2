import asyncio
import uuid

from context import turkit2
from turkit2.common import TextClassification
from turkit2.qualifications import Unique, Locale, AcceptRate
from utils import get_client

client = get_client()

id_ = str(uuid.uuid4())
quals = [Locale(), AcceptRate()]
task = TextClassification(client, 'Test3', '0.01', 'test test', 600, 6000, ['positive', 'negative'], qualifications=quals)

documents = [f'test{i}' for i in range(5)]

async def proc(text):
    async for answer, assignment in task.ask_async(verbosity=100, text=text, question="Which class does this text match, 'positive' or 'negative'?"):
        print(answer)
        print(assignment)

async def main():
    tasks = []
    for text in documents:
        tasks.append(asyncio.create_task(proc(text)))
    await asyncio.gather(*tasks)

asyncio.run(main())
