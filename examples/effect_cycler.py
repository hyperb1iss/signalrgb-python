import contextlib
import logging
import time

from signalrgb.client import SignalRGBClient, SignalRGBException
from signalrgb.model import Effect


def cycle_effects(client: SignalRGBClient, duration: int = 10) -> None:
    """
    Cycle through all available effects, applying each for a specified duration.

    Args:
        client (SignalRGBClient): An initialized SignalRGBClient object.
        duration (int): The duration in seconds to apply each effect. Defaults to 10 seconds.
    """
    effects = client.get_effects()

    for effect in effects:
        effect_name = effect.attributes.name

        try:
            client.apply_effect_by_name(effect_name)
            time.sleep(duration)
        except SignalRGBException as e:
            logging.warning("Failed to apply effect %s: %s", effect_name, e)


def main() -> None:
    # Initialize the SignalRGB client
    client = SignalRGBClient(host="hyperia.home", port=16038)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

    # Initialize initial_effect to None
    initial_effect: Effect | None = None

    try:
        # Get the initial effect
        initial_effect = client.get_current_effect()

        # Cycle through effects
        cycle_effects(client, duration=5)  # Change duration as needed

    except SignalRGBException as e:
        logging.exception("Error during effect cycling: %s", e)

    finally:
        # Restore the initial effect
        with contextlib.suppress(SignalRGBException):
            if initial_effect:
                client.apply_effect_by_name(initial_effect.attributes.name)


if __name__ == "__main__":
    main()
