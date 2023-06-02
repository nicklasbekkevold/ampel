import time

import RPi.GPIO as GPIO

from ampel import energy_mix, parameters

TEST_COUNTER = 0


def setup() -> None:
    """Sets up the GPIO pins"""

    # set GPIO mode
    GPIO.setmode(GPIO.BCM)

    # set output pins
    GPIO.setup(parameters.RED_PIN, GPIO.OUT)
    GPIO.setup(parameters.YELLOW_PIN, GPIO.OUT)
    GPIO.setup(parameters.GREEN_PIN, GPIO.OUT)


def cleanup() -> None:
    """Cleans up the GPIO pins"""
    GPIO.cleanup()


def determine_light(val_now, val_future) -> None:
    """Determines the output light for the current and future values

    @param val_now The value of the current sustainable energy
    @param val_future The value of the sustainable energy in the future

    """

    if val_now > parameters.UPPER_THRESHOLD and val_future > parameters.UPPER_THRESHOLD:
        # current and future energy are both fully sustainable
        GPIO.output(parameters.GREEN_PIN, 1)
        GPIO.output(parameters.YELLOW_PIN, 0)
        GPIO.output(parameters.RED_PIN, 0)
    elif (
        val_now > parameters.UPPER_THRESHOLD
        and val_future < parameters.UPPER_THRESHOLD
        and val_future > parameters.LOWER_THRESHOLD
    ):
        # current energy is fully sustainable but future energy is sustainable
        GPIO.output(parameters.GREEN_PIN, 1)
        GPIO.output(parameters.YELLOW_PIN, 0)
        GPIO.output(parameters.RED_PIN, 0)
    elif (
        val_now > parameters.UPPER_THRESHOLD and val_future < parameters.LOWER_THRESHOLD
    ):
        # current energy is fully sustainable but future energy is not
        GPIO.output(parameters.GREEN_PIN, 0)
        GPIO.output(parameters.YELLOW_PIN, 1)
        GPIO.output(parameters.RED_PIN, 0)
    elif (
        val_now < parameters.UPPER_THRESHOLD
        and val_now > parameters.LOWER_THRESHOLD
        and val_future > parameters.UPPER_THRESHOLD
    ):
        # current energy is sustainable but future energy is fully sustainable
        GPIO.output(parameters.GREEN_PIN, 1)
        GPIO.output(parameters.YELLOW_PIN, 0)
        GPIO.output(parameters.RED_PIN, 0)
    elif (
        val_now < parameters.UPPER_THRESHOLD
        and val_now > parameters.LOWER_THRESHOLD
        and val_future < parameters.UPPER_THRESHOLD
        and val_future > parameters.LOWER_THRESHOLD
    ):
        # current energy is sustainable but future energy is also sustainable
        GPIO.output(parameters.GREEN_PIN, 1)
        GPIO.output(parameters.YELLOW_PIN, 1)
        GPIO.output(parameters.RED_PIN, 0)
    elif (
        val_now < parameters.UPPER_THRESHOLD
        and val_now > parameters.LOWER_THRESHOLD
        and val_future < parameters.LOWER_THRESHOLD
    ):
        # current energy is sustainable but future energy is not
        GPIO.output(parameters.GREEN_PIN, 0)
        GPIO.output(parameters.YELLOW_PIN, 1)
        GPIO.output(parameters.RED_PIN, 1)
    elif (
        val_now < parameters.LOWER_THRESHOLD and val_future > parameters.UPPER_THRESHOLD
    ):
        # current energy is not sustainable but future energy is fully sustainable
        GPIO.output(parameters.GREEN_PIN, 0)
        GPIO.output(parameters.YELLOW_PIN, 1)
        GPIO.output(parameters.RED_PIN, 1)
    elif (
        val_now < parameters.LOWER_THRESHOLD
        and val_future < parameters.UPPER_THRESHOLD
        and val_future > parameters.LOWER_THRESHOLD
    ):
        # current energy is not sustainable but future energy is sustainable
        GPIO.output(parameters.GREEN_PIN, 0)
        GPIO.output(parameters.YELLOW_PIN, 1)
        GPIO.output(parameters.RED_PIN, 1)
    elif (
        val_now < parameters.LOWER_THRESHOLD and val_future < parameters.LOWER_THRESHOLD
    ):
        # current energy is not sustainable and future energy is not
        GPIO.output(parameters.GREEN_PIN, 0)
        GPIO.output(parameters.YELLOW_PIN, 0)
        GPIO.output(parameters.RED_PIN, 1)
    else:
        # something wrong
        GPIO.output(parameters.GREEN_PIN, 1)
        GPIO.output(parameters.YELLOW_PIN, 1)
        GPIO.output(parameters.RED_PIN, 1)


def get_test_sustainability_values():
    global TEST_COUNTER

    out = (0, 0)

    if TEST_COUNTER == 0:
        out = (0.5, 0.5)
    elif TEST_COUNTER == 1:
        out = (0.5, 0.35)
    elif TEST_COUNTER == 2:
        out = (0.5, 0.1)
    elif TEST_COUNTER == 3:
        out = (0.35, 0.5)
    elif TEST_COUNTER == 4:
        out = (0.35, 0.35)
    elif TEST_COUNTER == 5:
        out = (0.35, 0.1)
    elif TEST_COUNTER == 6:
        out = (0.1, 0.5)
    elif TEST_COUNTER == 7:
        out = (0.1, 0.35)
    elif TEST_COUNTER == 8:
        out = (0.1, 0, 1)

    if TEST_COUNTER >= 11:
        TEST_COUNTER = 0
    TEST_COUNTER += 1

    return out


def get_sustainable_energy_distribution(hour: int, test: bool, pos: int):
    if test:
        return get_test_sustainability_values()[pos]
    return energy_mix.get_sustainable_energy_distribution(hour)


def main():
    global IS_TEST
    global LOOP_TIME

    try:
        while True:
            current_val = get_sustainable_energy_distribution(0, IS_TEST, 0)
            print("current: " + str(current_val))
            future_val = get_sustainable_energy_distribution(2, IS_TEST, 1)
            print("in 2h: " + str(future_val))
            determine_light(current_val, future_val)
            time.sleep(LOOP_TIME)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    setup()

    GPIO.output(parameters.GREEN_PIN, True)
    GPIO.output(parameters.YELLOW_PIN, True)
    GPIO.output(parameters.RED_PIN, True)

    time.sleep(1)

    GPIO.output(parameters.GREEN_PIN, False)
    GPIO.output(parameters.YELLOW_PIN, False)
    GPIO.output(parameters.RED_PIN, False)

    time.sleep(1)

    GPIO.output(parameters.GREEN_PIN, True)
    GPIO.output(parameters.YELLOW_PIN, True)
    GPIO.output(parameters.RED_PIN, True)

    main()
    cleanup()
