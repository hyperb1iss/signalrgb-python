import time
from signalrgb.client import SignalRGBClient


def cycle_effects(client, duration=10):
    """
    Cycle through all available effects, applying each for a specified duration.

    Args:
        client (SignalRGBClient): An initialized SignalRGBClient object.
        duration (int): The duration in seconds to apply each effect. Defaults to 10 seconds.
    """
    print("Fetching available effects...")
    effects = client.get_effects()

    print(f"Found {len(effects)} effects. Starting cycle...")
    for effect in effects:
        effect_name = effect.attributes.name
        print(f"Applying effect: {effect_name}")

        try:
            client.apply_effect_by_name(effect_name)
            print(
                f"Effect '{effect_name}' applied successfully. Waiting for {duration} seconds..."
            )
            time.sleep(duration)
        except Exception as e:
            print(f"Error applying effect '{effect_name}': {str(e)}")


def main():
    # Initialize the SignalRGB client
    client = SignalRGBClient(host="hyperia.home", port=16038)

    try:
        # Get the initial effect
        initial_effect = client.get_current_effect()
        print(f"Initial effect: {initial_effect.attributes.name}")

        # Cycle through effects
        cycle_effects(client, duration=5)  # Change duration as needed

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        # Restore the initial effect
        try:
            client.apply_effect_by_name(initial_effect.attributes.name)
            print(f"Restored initial effect: {initial_effect.attributes.name}")
        except Exception as e:
            print(f"Error restoring initial effect: {str(e)}")


if __name__ == "__main__":
    main()
