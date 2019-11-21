from turkit2.base import Task

from jinja2 import Template
from utils import get_client

with open('basic_form.html') as f:
    schema = Template(f.read())

client = get_client()

task = Task(client, schema, 'Test', '0.01', 'test test', 600, 6000)

print(task.preview())
