"""Adafruit 1602 liquid crystal character display controller."""  # noqa: N999

from __future__ import annotations

from time import sleep
from typing import Any


class Adafruit_CharLCD:  # noqa: N801
    """Adafruit 1602 liquid crystal character display controller."""

    # commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    # flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

    # flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    def __init__(
        self,
        pin_rs: int = 25,
        pin_e: int = 24,
        pins_db: list[int] | None = None,
        GPIO: Any | None = None,  # noqa: N803
    ) -> None:
        """Initialize driver."""
        if pins_db is None:
            pins_db = [23, 17, 21, 22]

        # Emulate the old behavior of using RPi.GPIO if we haven't been given
        # an explicit GPIO interface to use
        if GPIO is None:
            import RPi.GPIO as GPIO

            GPIO.setwarnings(False)
        self.GPIO = GPIO
        self.pin_rs = pin_rs
        self.pin_e = pin_e
        self.pins_db = pins_db

        self.GPIO.setmode(GPIO.BCM)  # GPIO=None use Raspi PIN in BCM mode
        self.GPIO.setup(self.pin_e, GPIO.OUT)
        self.GPIO.setup(self.pin_rs, GPIO.OUT)

        for pin in self.pins_db:
            self.GPIO.setup(pin, GPIO.OUT)

        self.write_bits(0x33)  # initialization
        self.write_bits(0x32)  # initialization
        self.write_bits(0x28)  # 2 line 5x7 matrix
        self.write_bits(0x0C)  # turn cursor off 0x0E to enable cursor
        self.write_bits(0x06)  # shift cursor right

        self.displaycontrol = (
            self.LCD_DISPLAYON | self.LCD_CURSOROFF | self.LCD_BLINKOFF
        )

        self.displayfunction = (
            self.LCD_4BITMODE | self.LCD_1LINE | self.LCD_5x8DOTS
        )
        self.displayfunction |= self.LCD_2LINE

        # Initialize to default text direction (for romance languages)
        self.displaymode = self.LCD_ENTRYLEFT | self.LCD_ENTRYSHIFTDECREMENT
        self.write_bits(
            self.LCD_ENTRYMODESET | self.displaymode,
        )  # set the entry mode

        self.clear()

    def delay_micros(self, microseconds: int) -> None:
        """Wait for given number of microseconds."""
        seconds = microseconds / float(
            1000000,
        )  # divide microseconds by 1 million for seconds
        sleep(seconds)

    def pulse_enable(self) -> None:
        """Pulse the enable pin."""
        self.GPIO.output(self.pin_e, False)
        # 1 microsecond pause - enable pulse must be > 450ns
        self.delay_micros(1)
        self.GPIO.output(self.pin_e, True)
        # 1 microsecond pause - enable pulse must be > 450ns
        self.delay_micros(1)
        self.GPIO.output(self.pin_e, False)
        self.delay_micros(1)  # commands need > 37us to settle

    def write_bits(self, bits: int, char_mode: bool = False) -> None:
        """Send command to LCD."""
        self.delay_micros(1000)  # 1000 microsecond sleep
        bit_data = bin(bits)[2:].zfill(8)
        self.GPIO.output(self.pin_rs, char_mode)
        for pin in self.pins_db:
            self.GPIO.output(pin, False)
        for i in range(4):
            if bit_data[i] == "1":
                self.GPIO.output(self.pins_db[::-1][i], True)
        self.pulse_enable()
        for pin in self.pins_db:
            self.GPIO.output(pin, False)
        for i in range(4, 8):
            if bit_data[i] == "1":
                self.GPIO.output(self.pins_db[::-1][i - 4], True)
        self.pulse_enable()

    def begin(self, cols: int, lines: int) -> None:
        """Begin."""
        if lines > 1:
            self.numlines = lines
            self.displayfunction |= self.LCD_2LINE

    def home(self) -> None:
        """Set cursor position to zero."""
        self.write_bits(self.LCD_RETURNHOME)  # set cursor position to zero
        self.delay_micros(3000)  # this command takes a long time!

    def clear(self) -> None:
        """Clear display."""
        self.write_bits(self.LCD_CLEARDISPLAY)  # command to clear display
        self.delay_micros(
            3000,
        )  # 3000 microsecond sleep, clearing the display takes a long time

    def set_cursor(self, col: int, row: int) -> None:
        """Set cursor position (rows start at zero)."""
        self.row_offsets = [0x00, 0x40, 0x14, 0x54]
        if row > self.numlines:
            row = self.numlines - 1  # we count rows starting w/0
        self.write_bits(self.LCD_SETDDRAMADDR | (col + self.row_offsets[row]))

    def no_display(self) -> None:
        """Disable the display (quickly)."""
        self.displaycontrol &= ~self.LCD_DISPLAYON
        self.write_bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def display(self) -> None:
        """Enable the display (quickly)."""
        self.displaycontrol |= self.LCD_DISPLAYON
        self.write_bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def no_cursor(self) -> None:
        """Disable cursor underline."""
        self.displaycontrol &= ~self.LCD_CURSORON
        self.write_bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def cursor(self) -> None:
        """Enable cursor underline."""
        self.displaycontrol |= self.LCD_CURSORON
        self.write_bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def no_blink(self) -> None:
        """Turn cursor blinking off."""
        self.displaycontrol &= ~self.LCD_BLINKON
        self.write_bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def blink(self) -> None:
        """Turn cursor blinking on."""
        self.displaycontrol |= self.LCD_BLINKON
        self.write_bits(self.LCD_DISPLAYCONTROL | self.displaycontrol)

    def scroll_display_left(self) -> None:
        """Scroll the display left without changing the RAM."""
        self.write_bits(
            self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVELEFT,
        )

    def scroll_display_right(self) -> None:
        """Scroll the display right without changing the RAM."""
        self.write_bits(
            self.LCD_CURSORSHIFT | self.LCD_DISPLAYMOVE | self.LCD_MOVERIGHT,
        )

    def left_to_right(self) -> None:
        """Set display mode to flow from Left to Right."""
        self.displaymode |= self.LCD_ENTRYLEFT
        self.write_bits(self.LCD_ENTRYMODESET | self.displaymode)

    def right_to_left(self) -> None:
        """Set display mode to flow from Right to Left."""
        self.displaymode &= ~self.LCD_ENTRYLEFT
        self.write_bits(self.LCD_ENTRYMODESET | self.displaymode)

    def autoscroll(self) -> None:
        """Right justify text from the cursor."""
        self.displaymode |= self.LCD_ENTRYSHIFTINCREMENT
        self.write_bits(self.LCD_ENTRYMODESET | self.displaymode)

    def no_autoscroll(self) -> None:
        """Left justify text from the cursor."""
        self.displaymode &= ~self.LCD_ENTRYSHIFTINCREMENT
        self.write_bits(self.LCD_ENTRYMODESET | self.displaymode)

    def message(self, text: str) -> None:
        """Send string to LCD. Newline wraps to second line."""
        for char in text:
            if char == "\n":
                self.write_bits(0xC0)  # next line
            else:
                self.write_bits(ord(char), True)


if __name__ == "__main__":
    lcd = Adafruit_CharLCD()
    lcd.clear()
    lcd.message("  Adafruit 16x2\n  Standard LCD")
