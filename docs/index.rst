pytest-leak-finder
==================

pytest-leak-finder helps you identify which earlier test leaks state and causes
an unrelated failure later in the suite. It uses a binary-search strategy over
collected tests to narrow down the culprit quickly.

Quick start
-----------

Install the plugin:

.. code-block:: bash

   uv add --dev pytest-leak-finder

Run the leak finder on a failing test file:

.. code-block:: bash

   pytest --leak-finder path/to/test_file.py

After the first run sets the target, re-run the command until the leaking test
is identified.
