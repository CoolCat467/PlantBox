"""Plantbox Script - Automate plants."""

# Programmed by CoolCat467

from __future__ import annotations

# Plantbox Script - Automate plants
# Copyright (C) 2024  CoolCat467
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__title__ = "Plantbox Script"
__author__ = "CoolCat467"
__version__ = "0.0.0"
__license__ = "GNU General Public License Version 3"

import contextlib
import math
import time
from typing import TYPE_CHECKING

import RPi.GPIO as GPIO
from smbus2 import SMBus

if TYPE_CHECKING:
    from collections.abc import Generator

ADDRESS = 0x48
CMD = 0x40
MOTOR_PIN = 11  # physical 17
BUTTON_PIN = 12  # physical 18

MOTOR_HOLD_TIME_SEC = 5
RESISTANCE_THRESHOLD = 55


def analog_read(bus: SMBus, chn: int) -> int:
    """Read analog data."""
    return bus.read_byte_data(ADDRESS, CMD + chn)


def analog_write(bus: SMBus, value: int) -> None:
    """Write analog data."""
    bus.write_byte_data(ADDRESS, CMD, value)


@contextlib.contextmanager
def setup() -> Generator[None, None, None]:
    """Handle GPIO setup."""
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(MOTOR_PIN, GPIO.OUT, initial=GPIO.LOW)  # motor off
    GPIO.setup(
        BUTTON_PIN,
        GPIO.IN,
        pull_up_down=GPIO.PUD_UP,
    )  # Set buttonPin's mode is input, and pull up to high level(3.3V)
    try:
        yield
    finally:
        GPIO.output(MOTOR_PIN, GPIO.LOW)  # motor off
        GPIO.cleanup()


def loop() -> None:
    """Handle main loop."""
    max_resistance = 3.3
    ##    max_resistance = 2.821176470588235
    last_value = 1024
    last_pressed = False
    tick_delay = 0.01
    motor_ticks = 0

    with SMBus(1) as analog_bus:
        while True:
            value = analog_read(analog_bus, 0)  # read A0 pin
            button_state = GPIO.input(BUTTON_PIN)  # read button state
            button_pressed = button_state == GPIO.LOW

            time.sleep(tick_delay)
            motor_ticks = max(0, motor_ticks - 1)

            state = {True: GPIO.HIGH, False: GPIO.LOW}[motor_ticks > 0]
            GPIO.output(MOTOR_PIN, state)  # Motor value

            if (button_pressed == last_pressed) and (value == last_value):
                continue

            last_value = value
            voltage = value / 255 * 3.3  # calculate voltage

            if button_pressed and not last_pressed:
                break
            ##if button_pressed and not last_pressed:
            ##    print(f"Changing max_resistance to {voltage}")
            ##    max_resistance = float(voltage)
            ##if button_pressed != last_pressed:
            ##    print(f"Changing monitor state to {button_pressed}")
            ##    state = {True: GPIO.HIGH, False: GPIO.LOW}[button_pressed]
            ##    GPIO.output(MOTOR_PIN, state)     # Motor value

            last_pressed = button_pressed

            if voltage == max_resistance:
                resistance = math.inf
            else:
                resistance = (
                    10 * voltage / (max_resistance - voltage)
                )  # calculate resistance value
            print(
                f"ADC Value : {value}, Voltage : {voltage:.2f}, Resistance : {resistance:.2f}",
            )

            if resistance > RESISTANCE_THRESHOLD:
                motor_ticks = math.ceil(MOTOR_HOLD_TIME_SEC / tick_delay)


def run() -> None:
    """Run program."""
    print("Program is starting ... ")
    with setup():
        loop()


if __name__ == "__main__":
    print(f"{__title__} v{__version__}\nProgrammed by {__author__}.\n")
    run()
