from context import turkit2
from turkit2.primitive import Task

from jinja2 import Template
from utils import get_client

with open('basic_form.html') as f:
    schema = Template(f.read())

client = get_client('mykey.key')

task = Task(client, schema, 'Test', '0.01', 'test test', 600, 6000)

print(task.preview())
