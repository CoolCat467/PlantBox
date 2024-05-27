"""PCF8574 as Raspberry GPIO."""  # noqa: N999

from __future__ import annotations

########################################################################
# Filename    : PCF8574.py
# Description : PCF8574 as Raspberry GPIO
# Author      : freenove
# modification: 2018/08/03
########################################################################
import time

from smbus2 import SMBus

# Note you need to change the bus number to 0 if running on a revision 1 Raspberry Pi.
bus = SMBus(1)


class PCF8574_I2C:  # noqa: N801
    """PCF8574 I2C interface."""

    OUTPUT = 0
    INPUT = 1
    __slots__ = ("address", "current_value")

    def __init__(self, address: int) -> None:
        """Initialize and test I2C."""
        self.address = address
        self.current_value = 0
        self.write_byte(0)  # I2C test.

    def read_byte(self) -> int:
        """Read PCF8574 all port of the data."""
        # value = self.bus.read_byte(self.address)
        return self.current_value

    def write_byte(self, value: int) -> None:
        """Write data to PCF8574 port."""
        self.current_value = value
        bus.write_byte(self.address, value)

    def digital_read(self, pin: int) -> bool:
        """Read PCF8574 one port of the data."""
        value = self.read_byte()
        return value & (1 << pin) == (1 << pin)

    def digital_write(self, pin: int, newvalue: bool) -> None:
        """Write data to PCF8574 one port."""
        value = self.current_value  # bus.read_byte(address)
        if newvalue:
            value |= 1 << pin
        else:
            value &= ~(1 << pin)
        self.write_byte(value)


def loop() -> None:
    """Test writing bytes."""
    mcp = PCF8574_I2C(0x27)
    while True:
        # mcp.writeByte(0xff)
        mcp.digitalWrite(3, 1)
        print(f"Is 0xff? {mcp.readByte():x}")
        time.sleep(1)
        mcp.writeByte(0x00)
        # mcp.digitalWrite(7,1)
        print(f"Is 0x00? {mcp.readByte():x}")
        time.sleep(1)


class PCF8574_GPIO:  # noqa: N801
    """Standardization function interface."""

    __slots__ = ("chip", "address")

    OUT = 0
    IN = 1
    BCM = 0
    BOARD = 0

    def __init__(self, address: int) -> None:
        """Initialize PCF8574 I2C interface at address."""
        self.chip = PCF8574_I2C(address)
        self.address = address

    def setmode(
        self,
        mode: int,
    ) -> None:
        """PCF8574 port belongs to two-way IO, do not need to set the input and output model."""

    def setup(self, pin: int, mode: int) -> None:
        """Do nothing."""

    def input(self, pin: int) -> int:
        """Read PCF8574 one port of the data."""
        return self.chip.digitalRead(pin)

    def output(self, pin: int, value: int) -> None:
        """Write data to PCF8574 one port."""
        self.chip.digitalWrite(pin, value)


def destroy() -> None:
    """Close SMBus."""
    bus.close()


if __name__ == "__main__":
    print("Program is starting ... ")
    try:
        loop()
    finally:
        destroy()
