from typing import Optional
from pathlib import Path
import asyncio
#from xml.sax.saxutils import escape
from jinja2 import Template

class Task(object):
    def __init__(self, mturk_client,
        schema_template : Template,
        title: str,
        reward: str,
        description: str,
        duration: int,
        lifetime: int,
        #
        keywords: str='',
        auto_approval_delay: int=7200,# 24 hours
        max_heartbeat: int=600,# 10 minutes
    ):
        '''
        TODO add qualifications
        TODO add documentation
        '''
        self.mturk_client = mturk_client
        self.schema_template = schema_template
        with (Path(__file__).parent / 'schemas' / 'html_question.xml').open() as f:
            self.question_schema = Template(f.read())

        self.title = title
        self.reward = reward
        self.description = description
        self.keywords = keywords
        self.duration = duration
        self.auto_approval_delay = auto_approval_delay
        self.lifetime = lifetime

    def execute(self, assignments=1, verbosity=0, **schema_args):
        yield from asyncio.run(self.execute_async(assignments, verbosity, **schema_args))

    async def execute_async(self, assignments=1, verbosity=0, **schema_args):
        html_content = self.schema_template.render(**schema_args)
        #xml_question = self.question_schema.render(html_content=escape(html_content))
        xml_question = self.question_schema.render(html_content=html_content.replace('&', '&amp;'))

        response = self.mturk_client.create_hit(
            MaxAssignments=assignments,
            Title=self.title,
            Description=self.title,
            Keywords=self.keywords,
            Reward=self.reward,
            LifetimeInSeconds=self.lifetime,
            AssignmentDurationInSeconds=self.duration,
            AutoApprovalDelayInSeconds=self.auto_approval_delay,
            Question=xml_question
        )
        if verbosity >= 1:
            print("https://worker.mturk.com/mturk/preview?groupId=" + response['HIT']['HITGroupId'])
            print("https://workersandbox.mturk.com/mturk/preview?groupId=" + response['HIT']['HITGroupId'])
