Contributing
============

We welcome contributions to the SignalRGB Python Client! This document outlines the process for contributing to the project.

Setting Up the Development Environment
--------------------------------------

1. Fork the repository on GitHub.
2. Clone your fork locally:

   .. code-block:: bash

       git clone https://github.com/your-username/signalrgb-python.git
       cd signalrgb-python

3. Install Poetry if you haven't already:

   .. code-block:: bash

       pip install poetry

4. Install dependencies:

   .. code-block:: bash

       poetry install

5. Activate the virtual environment:

   .. code-block:: bash

       poetry shell

Making Changes
--------------

1. Create a new branch for your feature or bugfix:

   .. code-block:: bash

       git checkout -b feature-branch-name

2. Make your changes and commit them:

   .. code-block:: bash

       git commit -m 'Add some feature'

3. Push to the branch:

   .. code-block:: bash

       git push origin feature-branch-name

4. Submit a pull request through the GitHub website.

Running Tests
-------------

Before submitting a pull request, make sure all tests pass:

.. code-block:: bash

    pytest

Running Linting
---------------

We use flake8 for linting. Run it with:

.. code-block:: bash

    flake8

Updating Documentation
----------------------

If your changes require updates to the documentation:

1. Update the relevant .rst files in the `docs/source/` directory.
2. Build the documentation locally to check your changes:

   .. code-block:: bash

       cd docs
       make html

3. Include the documentation changes in your pull request.

Code of Conduct
---------------

Please note that this project is released with a Contributor Code of Conduct. By participating in this project you agree to abide by its terms. See CODE_OF_CONDUCT.md for details.

Questions?
----------

If you have any questions about contributing, please open an issue on GitHub.

Thank you for your contribution!
