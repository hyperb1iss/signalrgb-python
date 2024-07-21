Usage
=====

Command-line Interface
----------------------

The SignalRGB Python Client comes with an intuitive command-line interface for easy interaction with your SignalRGB setup.

Listing Available Effects
~~~~~~~~~~~~~~~~~~~~~~~~~

To list all available effects:

.. code-block:: bash

    signalrgb list-effects

Getting Effect Details
~~~~~~~~~~~~~~~~~~~~~~

To get details of a specific effect:

.. code-block:: bash

    signalrgb get-effect "Psychedelic Dream"

Applying an Effect
~~~~~~~~~~~~~~~~~~

To apply an effect:

.. code-block:: bash

    signalrgb apply-effect "Rave Visualizer"

Getting the Current Effect
~~~~~~~~~~~~~~~~~~~~~~~~~~

To get the current effect:

.. code-block:: bash

    signalrgb current-effect

Using a Custom Host and Port
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can specify a custom host and port:

.. code-block:: bash

    signalrgb --host hyperia.home --port 16038 list-effects

For a full list of available commands and options, use:

.. code-block:: bash

    signalrgb --help

Python Library
--------------

You can also use the SignalRGB Python Client as a library in your Python projects.

Initializing the Client
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from signalrgb import SignalRGBClient

    client = SignalRGBClient(host="hyperia.home", port=16038)

Listing Effects
~~~~~~~~~~~~~~~

.. code-block:: python

    effects = client.get_effects()
    for effect in effects:
        print(f"Effect: {effect.attributes.name}")

Applying an Effect
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    client.apply_effect_by_name("Rain")

Getting the Current Effect
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    current_effect = client.get_current_effect()
    print(f"Current effect: {current_effect.attributes.name}")

Error Handling
~~~~~~~~~~~~~~

The client provides custom exceptions for different types of errors:

.. code-block:: python

    from signalrgb import SignalRGBClient, ConnectionError, APIError, EffectNotFoundError

    client = SignalRGBClient()

    try:
        client.apply_effect_by_name("Non-existent Effect")
    except ConnectionError as e:
        print(f"Connection failed: {e}")
    except EffectNotFoundError as e:
        print(f"Effect not found: {e}")
    except APIError as e:
        print(f"API error occurred: {e}")
