#############
HumanIO Tasks
#############

A **HumanIO** task is a task that is made of many smaller pieces, **primitives**.
Primitives are contained in the :ref:`primitive` module.

There are *input* primitives and *output* primitives.

An *input* primitive is something a programmer shows to the worker in the task, i.e., the programmer *inputs* data into the task. These primitives are prefixed with :code:`I`. 
Example: for text classification, an input primitive is the text being classified, a :code:`IText` type.

An *output* primitive is something a worker outputs (or produces) in the task, i.e., the programmer receives *output* data from the task. These primitives are prefixed with :code:`O`.
Example: for text classification, an output primitive is the class the worker outputs, a :code:`OChoice` type.

Usage
=====

HumanIO tasks are used in two steps like all task objects:

#. Initialization. The programmer passes a list of ID-primitive pairs into the constructor. The list of primitives determines the order where the primitives appear in the task.
   The ID is used to help the programmer add data to the input primitives when :code:`ask` is called.
#. Ask. The programmer passes data to the input primitive using the previously defined IDs.
   The parameters must be specified correctly in this format:
   :code:`parameters={primitive_ID: arg, ...}`

Example
=======

In this example we reimplement the text classification task in a HumanIO task object.

We start as before, initializing our client.

.. code-block:: python

    # import boto3 to use aws python
    import boto3

    # Import HumanIO and primitives IText and OChoice
    from turkit2.common import HumanIO
    from turkit2.primitive import IText, OChoice

    # Create an MTurk sandbox instance
    # (aws credentials should be stored in ~/.aws, which is taken care of by awscli)
    endpoint = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
    client = boto3.client(
        'mturk',
        region_name='us-east-1',
        endpoint_url = endpoint
    )

We stack a :code:`IText` (the text being classified)
and a :code:`OChoice` (the class being chosen). This is indicated
in the initialization of the HumanIO object.
The IDs specified (prompt and answer) are important.

.. code-block:: python

    task = HumanIO(
        client,
        elements=[
            ('prompt', IText()),# text being classified
            ('class', OChoice('answer_id'))# classes. 'answer_id' is used for the text box id
        ],
        title='Classify tweet sentiment',
        reward='0.05',
        description='Classify the mood of a single Twitter tweet.',
        duration=600,
        lifetime=6000
    )

The IDs specified before are used as ask parameters.

.. code-block:: python

    # Post to mturk from the task object. We need to supply parameters matching the id's supplied earlier.
    for worker_answer, assignment_details in task.ask(
        assignments=5,
        parameters={
            'prompt': 'This movie is sad!',
            'class': ['positive', 'negative']
        }
    ):
        # worker_answer is a dictionary with the privious O primitive id's as keys
        print(worker_answer['answer_id'])

This is all the code in one block.

.. code-block:: python

    # import boto3 to use aws python
    import boto3

    # Import HumanIO and primitives IText and OChoice
    from turkit2.common import HumanIO
    from turkit2.primitive import IText, OChoice

    # Create an MTurk sandbox instance
    # (aws credentials should be stored in ~/.aws, which is taken care of by awscli)
    endpoint = 'https://mturk-requester-sandbox.us-east-1.amazonaws.com'
    client = boto3.client(
        'mturk',
        region_name='us-east-1',
        endpoint_url = endpoint
    )

    task = HumanIO(
        client,
        elements=[
            ('prompt', IText()),# text being classified
            ('class', OChoice('answer_id'))# classes. 'answer_id' is used for the text box id
        ],
        title='Classify tweet sentiment',
        reward='0.05',
        description='Classify the mood of a single Twitter tweet.',
        duration=600,
        lifetime=6000
    )


    # Post to mturk from the task object. We need to supply parameters matching the id's supplied earlier.
    for worker_answer, assignment_details in task.ask(
        assignments=5,
        parameters={
            'prompt': 'This movie is sad!',
            'class': ['positive', 'negative']
        }
    ):
        # worker_answer is a dictionary with the privious O primitive id's as keys
        print(worker_answer['answer_id'])
