"""Use the LCD to display data."""

from __future__ import annotations

########################################################################
# Filename    : I2CLCD1602.py
# Description : Use the LCD to display data
# Author      : freenove
# modification: 2018/08/03
########################################################################
from datetime import datetime
from time import sleep

from Adafruit_LCD1602 import Adafruit_CharLCD
from PCF8574 import PCF8574_GPIO, destroy as pcf_destroy


def get_cpu_temp() -> str:
    """Return CPU temperature and store it into file "/sys/class/thermal/thermal_zone0/temp"."""
    with open("/sys/class/thermal/thermal_zone0/temp") as fp:
        cpu = fp.read()
        return f"{float(cpu) / 1000:.2f}" + " C"


def get_time_now() -> str:
    """Return current time as "    %H:%M:%S"."""
    return datetime.now().strftime("    %H:%M:%S")


def loop() -> None:
    """Display the CPU temperature and current time."""
    mcp.output(3, 1)  # turn on LCD backlight
    lcd.begin(16, 2)  # set number of LCD lines and columns
    while True:
        # lcd.clear()
        lcd.setCursor(0, 0)  # set cursor position
        lcd.message("CPU: " + get_cpu_temp() + "\n")  # display CPU temperature
        lcd.message(get_time_now())  # display the time
        sleep(1)


def destroy() -> None:
    """Deallocate memory."""
    pcf_destroy()
    lcd.clear()


PCF8574_address = 0x27  # I2C address of the PCF8574 chip.
PCF8574A_address = 0x3F  # I2C address of the PCF8574A chip.
# Create PCF8574 GPIO adapter.
try:
    mcp = PCF8574_GPIO(PCF8574_address)
except Exception as exc:
    try:
        mcp = PCF8574_GPIO(PCF8574A_address)
    except Exception as exc_two:
        print("I2C Address Error !")
        raise exc_two from exc

# Create LCD, passing in MCP GPIO adapter.
lcd = Adafruit_CharLCD(pin_rs=0, pin_e=2, pins_db=[4, 5, 6, 7], GPIO=mcp)

if __name__ == "__main__":
    print("Program is starting ... ")
    try:
        loop()
    except KeyboardInterrupt:
        destroy()
