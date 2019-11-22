import asyncio
from context import turkit2
from turkit2.base import Task

from jinja2 import Template
from utils import get_client

doc1 = '''
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Maecenas in luctus augue. Sed a sem at nulla congue condimentum. Aenean dapibus cursus odio ac semper. Curabitur id tincidunt nisl, euismod vestibulum ligula. Aenean auctor ullamcorper euismod. Praesent diam metus, lacinia sit amet neque non, fringilla aliquet nulla. Cras hendrerit quam in elementum tristique. Donec sit amet tortor tincidunt risus egestas faucibus. Sed aliquam erat sed metus aliquam, nec egestas quam maximus. Nam lobortis ligula id orci consequat, nec venenatis magna eleifend.
'''
doc2 = '''
Aliquam erat volutpat. Curabitur ultrices venenatis odio sed mollis. Sed tincidunt, felis sagittis fermentum dignissim, lorem nunc ultricies velit, et tincidunt elit nisi blandit leo. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Pellentesque a dignissim urna, sed feugiat elit. Curabitur rutrum metus venenatis venenatis cursus. In hac habitasse platea dictumst. Praesent a finibus turpis. Nulla blandit quam felis, et aliquet elit fermentum ac. Pellentesque porttitor diam eu odio faucibus, ac placerat justo tincidunt. Aliquam faucibus eget est in eleifend. Morbi vel fermentum metus, pharetra ornare lacus. Sed laoreet iaculis augue at maximus. Suspendisse potenti.
'''
doc3 = '''
Maecenas viverra euismod neque, pellentesque egestas dui sodales a. Nulla rhoncus consequat leo, vitae convallis libero gravida at. Ut ornare porttitor elementum. Duis hendrerit dignissim sem ac tristique. Praesent tristique, tortor non placerat interdum, sapien velit imperdiet erat, pellentesque aliquet nisl enim quis nulla. Aenean viverra ut purus sit amet laoreet. Phasellus tortor neque, auctor ac pellentesque vel, pulvinar eu risus. Aenean sit amet augue id justo vehicula convallis. Cras posuere, metus nec faucibus iaculis, odio elit rutrum risus, a aliquam tortor risus vel ex. Quisque nec metus neque. Duis molestie rutrum libero. Sed dignissim tincidunt ipsum, sit amet tincidunt nulla volutpat efficitur. Aliquam suscipit lacus risus, nec vestibulum ex vehicula sit amet.
'''

with open('textanno_schema.html') as f:
    schema = Template(f.read())

client = get_client()

task = Task(client, schema, 'Test', '0.01', 'test test', 600, 6000)


args = {
    'interface': 'suggestions', 
    'docs': {1: doc1, 2: doc2, 3: doc3},
    'categories': ['positive', 'negative'],
    'categories_agree': ['agree', 'disagree'],
    'suggestions': {1: "positive", 2: "negative", 3: "positive"}
}

async def proc():
    async for answer, assignment in task.ask_async(verbosity=100, **args):
        print(answer)
        print(assignment)

asyncio.run(proc())
