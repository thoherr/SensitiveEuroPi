"""
Sensitive Euro Pi - generating CV from sensor reading
author: Thomas Herrmann (github.com/thoherr)
date: 2023-01-29
labels: sensor

digital_in: not used
analog_in: not used

knob_1: adjust the value of the current configuration parameter
knob_2: not used

button_1: enable/disable sensor readings
button_2: cycle through editable configuration parameters

output_1: VL53L0X CV
output_2: HC-SR04 CV
output_3: GY302 CV
output_4: VL53L0X gate (CV valid)
output_5: HC-SR04 gate (CV valid)
output_6: GY302 gate (CV valid)

"""

from time import sleep
from europi import oled, b1, cv1, cv2, cv3, cv4, cv5, cv6, OLED_WIDTH, OLED_HEIGHT, CHAR_HEIGHT
from europi_script import EuroPiScript
from machine import Pin, I2C
from vl53l0x import VL53L0X

from collections import namedtuple

VERSION = "0.2"

I2C_ID = 1
I2C_SDA_PIN = 2
I2C_SCL_PIN = 3

SensorReading = namedtuple("SensorReading", "valid value")

class Sensor:
    active = False
    reading = SensorReading(False, 0)
    def __init__(self, index, name, description, i2c_address, output, gate):
        self.index = index
        self.name = name
        self.description = description
        self.i2c_address = i2c_address
        self.output = output
        self.output.voltage(0)
        self.gate = gate
        self.gate.off()

    def __str__(self):
        status = f"@ 0x{self.i2c_address:x}" if self.active else "not connected"
        return f"{self.name} ({self.description}) {status}"

    def activate(self, i2c, state):
        self.active = True

    def display_reading(self):
        padding_x = self.index * int((OLED_WIDTH - 8)/3) + 4
        padding_y = 0
        oled.text(f"{self.name:>4}", padding_x, padding_y, 1)
        padding_y = 12
        oled.text(f"{self.reading.value:.2f}", padding_x, padding_y, 1)

    def update(self):
        if self.active:
            self.reading = self.get_reading()
            if self.reading.valid:
                self.output.voltage(self.reading.value)
            self.gate.value(self.reading.valid)

    def get_reading(self):
        return SensorReading(False, 0)


class LaserDistanceSensorVL53L0X(Sensor):
    OFFSET_MM = 30
    MAX_MM = 999
    MAX_VOLTAGE = 9.99
    pre_periods = [12, 14, 16, 18]
    final_periods = [8, 10, 12, 14]

    def __init__(self, output, gate):
        super().__init__(0, "LToF", "Laser distance sensor VL53L0X", 0x29, output, gate)

    def activate(self, i2c, state):
        # Pre: 12 to 18 (initialized to 14 by default)
        self.pre_period = state.get("pre_period", 14)  # TODO: This should be configurable by UI
        # Final: 8 to 14 (initialized to 10 by default)
        self.final_period = state.get("final_period", 10)  # TODO: This should be configurable by UI

        self.vl53l0x = VL53L0X(i2c)
        self.config()
        super().activate(i2c, state)

    def get_reading(self):
        distance = min(max(self.vl53l0x.ping() - self.OFFSET_MM, 0), self.MAX_MM)
        voltage = distance / self.MAX_MM * self.MAX_VOLTAGE
        if voltage < self.MAX_VOLTAGE:
            return SensorReading(True, voltage)
        else:
            return SensorReading(False, 0)

    def config(self):
        self.vl53l0x.set_Vcsel_pulse_period(self.vl53l0x.vcsel_period_type[0], self.pre_period)
        self.vl53l0x.set_Vcsel_pulse_period(self.vl53l0x.vcsel_period_type[1], self.final_period)
        

class SonicDistanceSensorHCSR04(Sensor):
    def __init__(self, output, gate):
        super().__init__(1, "SON", "Sonic distance sensor HC-SR04", 0x57, output, gate)

    def activate(self, i2c, state):
        super().activate(i2c, state)


class LightSensorGY302(Sensor):
    def __init__(self, output, gate):
        super().__init__(2, "LUX", "Brightness sensor GY302 (BH1750)", 0x23, output, gate)

    def activate(self, i2c):
        super().activate(i2c)


class SensitiveEuroPi(EuroPiScript):

    sensors = [
        LaserDistanceSensorVL53L0X(cv1, cv4),
        SonicDistanceSensorHCSR04(cv2, cv5),
        LightSensorGY302(cv3, cv6)
        ];

    def __init__(self):
        super().__init__()

        # Configure EuroPi options to improve performance.
        b1.debounce_delay = 200
        oled.contrast(0)  # dim the oled

        state = self.load_state_json()
        self.enabled = state.get("enabled", True)

        b1.handler(self.toggle_enablement)

        self.i2c = I2C(id=I2C_ID, sda=Pin(I2C_SDA_PIN), scl=Pin(I2C_SCL_PIN))

        self.init_sensors(state)

        for sensor in self.sensors:
            print(sensor)

    def init_sensors(self, state):
        i2c_addresses = self.i2c.scan()
        print(i2c_addresses)
        for sensor in self.sensors:
            if sensor.i2c_address in i2c_addresses:
                sensor.activate(self.i2c, state)

    @classmethod
    def display_name(cls):
        return "Sensitive EuroPi"

    def toggle_enablement(self):
            self.enabled = not self.enabled
            self.save_state()

    def save_state(self):
        """Save the current state variables as JSON."""
        # Don't save if it has been less than 5 seconds since last save.
#         if self.last_saved() < 5000:
#             return
 
        state = {
             "enabled": self.enabled
            #  .... ADD SENSOR STATES
        }
        self.save_state_json(state)


    def main(self):
        oled.centre_text(f"Sensitive EuroPi\n{VERSION}")
        sleep(2)
        while True:
            if self.enabled:
                for sensor in self.sensors:
                    sensor.update()
                oled.fill(0)
                for sensor in self.sensors:
                    sensor.display_reading()
                oled.show()
            else:
                oled.centre_text(f"Sensitive EuroPi\n{VERSION}\nPAUSED")
                sleep(0.25)


# Main script execution
if __name__ == '__main__':
    script = SensitiveEuroPi()
    script.main()
