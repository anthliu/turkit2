######
common
######

.. autoclass:: turkit2.common.External
   :members:

   .. automethod:: preview

   .. automethod:: ask

   .. automethod:: ask_async

.. autoclass:: turkit2.common.HumanIO
   :members:
   :exclude-members: ask_async

   .. automethod:: preview

   .. automethod:: ask
    
        :param assignments: Number of assignments to add to a HIT. *NOTE* HITs with asssignments >= 10 are upcharged about 20% by Amazon.
        :type assignments: int
        :param verbosity: How much to print during execution.
        :type verbosity: int
        :param parameters: Values added to I primitives to generate task.
        :type parameters: dict

.. autoclass:: turkit2.common.BonusTask
   :members:

.. autoclass:: turkit2.common.TextClassification
   :members:

   .. automethod:: preview

   .. automethod:: ask

   .. automethod:: ask_async
