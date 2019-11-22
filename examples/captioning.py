from glob import glob
import asyncio
from random import randint

from turkit2.common import HumanIO
from turkit2.primitive import IImage, OText, OChoice
from utils import get_client, get_s3

s3 = get_s3(profile='anthony')
image_placeholder = IImage(s3, 'turkit-testing')

client = get_client()

session = randint(0, 100)

caption_reps = 1
vote_reps = 1
verbosity = 100

suggest_captions = HumanIO(
    client,
    [
        ('prompt', image_placeholder),
        ('answer', OText('answer'))
    ],
    f'Caption an image - {session}', '0.10',
    'Suggest a sentence that describes the image displayed.', 600, 6000
)

vote_captions = HumanIO(
    client,
    [
        ('prompt', image_placeholder),
        ('answer', OChoice('answer'))
    ],
    f'Vote on image captions - {session}', '0.05',
    'Pick the caption that describes the image the best', 600, 6000
)

image_paths = glob('imgs/*')

async def caption_image(path):
    captions = []
    async for caption, assignment in suggest_captions.ask_async(
        verbosity=verbosity, assignments=caption_reps, parameters={'prompt': {'path': path}}
    ):
        captions.append(caption['answer'])

    votes = []
    async for vote, assignment in vote_captions.ask_async(
        verbosity=verbosity, assignments=vote_reps, parameters={'prompt': {'path': path}, 'answer': {'choices': captions}}
    ):
        votes.append(vote['answer'])

    best_caption = max(set(votes), key=votes.count)
    print(path, best_caption)

async def main():
    tasks = []
    for path in image_paths:
        tasks.append(asyncio.create_task(caption_image(path)))

    await asyncio.gather(*tasks)

asyncio.run(main())
