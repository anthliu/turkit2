import asyncio

from turkit2.common import HIOTask
from turkit2.primitive import Image, Text, Choice

suggest_captions = HIOTask(
    input=Image,# worker sees an image
    output=Text,# worker suggests text
    prompt='Suggest a sentence that describes the image displayed.'
)

vote_captions = HIOTask(
    input=(Image, [Text]),# worker sees an image and a list of text
    output=Choice,# worker chooses one of the options inputed
    prompt='Select the sentence that *best* describes the image displayed.' 
)

image_paths = [...]

async def caption_image(path):
    captions, worker_info = await suggest_captions.ask(input=path)
    votes, worker_info = await vote_captions.ask(input=(path, captions))
    print(path, captions[argmax[votes]])

async def main():
    tasks = []
    for path in image_paths:
        tasks.append(asyncio.create_task(caption_image(path)))

    await asyncio.gather(*tasks)

asyncio.run(main())
