import time

import RPi.GPIO as GPIO

from ampel import energy_mix

IS_TEST = False
LOOP_TIME = 10

GREEN_PIN = 17
YELLOW_PIN = 27
RED_PIN = 22

LOWER_BORDER = 0.3
UPPER_BORDER = 0.4

TEST_COUNTER = 0

URL = "https://thingspeak.umwelt-campus.de/channels/688"
RANGE = 8


def setup() -> None:
    """Sets up the GPIO pins"""

    global RED_PIN
    global YELLOW_PIN
    global GREEN_PIN

    # set GPIO mode
    GPIO.setmode(GPIO.BCM)

    # set output pins
    GPIO.setup(RED_PIN, GPIO.OUT)
    GPIO.setup(YELLOW_PIN, GPIO.OUT)
    GPIO.setup(GREEN_PIN, GPIO.OUT)


def cleanup() -> None:
    """Cleans up the GPIO pins"""
    GPIO.cleanup()


def determine_light(val_now, val_future) -> None:
    """Determines the output light for the current and future values

    @param val_now The value of the current sustainable energy
    @param val_future The value of the sustainable energy in the future

    """

    global RED_PIN
    global YELLOW_PIN
    global GREEN_PIN

    if val_now > UPPER_BORDER and val_future > UPPER_BORDER:
        # current and future energy are both fully sustainable
        GPIO.output(GREEN_PIN, 1)
        GPIO.output(YELLOW_PIN, 0)
        GPIO.output(RED_PIN, 0)
    elif (
        val_now > UPPER_BORDER
        and val_future < UPPER_BORDER
        and val_future > LOWER_BORDER
    ):
        # current energy is fully sustainable but future energy is sustainable
        GPIO.output(GREEN_PIN, 1)
        GPIO.output(YELLOW_PIN, 0)
        GPIO.output(RED_PIN, 0)
    elif val_now > UPPER_BORDER and val_future < LOWER_BORDER:
        # current energy is fully sustainable but future energy is not
        GPIO.output(GREEN_PIN, 0)
        GPIO.output(YELLOW_PIN, 1)
        GPIO.output(RED_PIN, 0)
    elif (
        val_now < UPPER_BORDER and val_now > LOWER_BORDER and val_future > UPPER_BORDER
    ):
        # current energy is sustainable but future energy is fully sustainable
        GPIO.output(GREEN_PIN, 1)
        GPIO.output(YELLOW_PIN, 0)
        GPIO.output(RED_PIN, 0)
    elif (
        val_now < UPPER_BORDER
        and val_now > LOWER_BORDER
        and val_future < UPPER_BORDER
        and val_future > LOWER_BORDER
    ):
        # current energy is sustainable but future energy is also sustainable
        GPIO.output(GREEN_PIN, 1)
        GPIO.output(YELLOW_PIN, 1)
        GPIO.output(RED_PIN, 0)
    elif (
        val_now < UPPER_BORDER and val_now > LOWER_BORDER and val_future < LOWER_BORDER
    ):
        # current energy is sustainable but future energy is not
        GPIO.output(GREEN_PIN, 0)
        GPIO.output(YELLOW_PIN, 1)
        GPIO.output(RED_PIN, 1)
    elif val_now < LOWER_BORDER and val_future > UPPER_BORDER:
        # current energy is not sustainable but future energy is fully sustainable
        GPIO.output(GREEN_PIN, 0)
        GPIO.output(YELLOW_PIN, 1)
        GPIO.output(RED_PIN, 1)
    elif (
        val_now < LOWER_BORDER
        and val_future < UPPER_BORDER
        and val_future > LOWER_BORDER
    ):
        # current energy is not sustainable but future energy is sustainable
        GPIO.output(GREEN_PIN, 0)
        GPIO.output(YELLOW_PIN, 1)
        GPIO.output(RED_PIN, 1)
    elif val_now < LOWER_BORDER and val_future < LOWER_BORDER:
        # current energy is not sustainable and future energy is not
        GPIO.output(GREEN_PIN, 0)
        GPIO.output(YELLOW_PIN, 0)
        GPIO.output(RED_PIN, 1)
    else:
        # something wrong
        GPIO.output(GREEN_PIN, 1)
        GPIO.output(YELLOW_PIN, 1)
        GPIO.output(RED_PIN, 1)


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
            time.sleep(LOOP_TIME)  # set to 30 mins
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    setup()

    GPIO.output(GREEN_PIN, True)
    GPIO.output(YELLOW_PIN, True)
    GPIO.output(RED_PIN, True)

    time.sleep(1)

    GPIO.output(GREEN_PIN, False)
    GPIO.output(YELLOW_PIN, False)
    GPIO.output(RED_PIN, False)

    time.sleep(1)

    GPIO.output(GREEN_PIN, True)
    GPIO.output(YELLOW_PIN, True)
    GPIO.output(RED_PIN, True)

    main()
    cleanup()
