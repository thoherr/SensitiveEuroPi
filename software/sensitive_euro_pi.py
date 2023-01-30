"""
Sensitive Euro Pi - generating CV from sensor reading
author: Thomas Herrmann (github.com/thoherr)
date: 2023-01-29
labels: sensor

digital_in: not used
analog_in: not used

knob_1: adjust the value of the current configuration parameter
knob_2: not used

button_1: cycle through editable configuration parameters
button_2: edit current configuration parameter ??

output_1: VL53L0X CV
output_2: HC-SR04 CV
output_3: GY302 CV
output_4: not used
output_5: not used
output_6: not used

"""

from time import sleep
from europi import oled, b1, din, cv1, cv2, cv3
from europi_script import EuroPiScript
from machine import Pin, I2C
from vl53l0x import VL53L0X

VERSION = "0.2"

I2C_ID = 1
I2C_SDA_PIN = 2
I2C_SCL_PIN = 3

VL53L0X_OFFSET_MM = 30
VL53L0X_MAX_MM = 999
MAX_VOLTAGE = 9.99

class Sensor:
    active = False
    def __init__(self, name, type, i2c_address, output):
        self.name = name
        self.type = type
        self.i2c_address = i2c_address
        self.output = output

    def __str__(self):
        status = f"@ 0x{self.i2c_address:x}" if self.active else "not connected"
        return f"{self.name} - {self.type} {status}"

    def activate(self, i2c, state):
        self.active = True

    def update(self):
        if self.active:
            self.output.voltage(self.calculate_voltage())

    def calculate_voltage(self):
        return 0


class LaserDistanceSensorVL53L0X(Sensor):
    pre_periods = [12, 14, 16, 18]
    final_periods = [8, 10, 12, 14]

    def __init__(self, output):
        super().__init__("Laser distance", "VL53L0X", 0x29, output)

    def activate(self, i2c, state):
        # Pre: 12 to 18 (initialized to 14 by default)
        self.pre_period = state.get("pre_period", 14)
        # Final: 8 to 14 (initialized to 10 by default)
        self.final_period = state.get("final_period", 10)

        self.vl53l0x = VL53L0X(i2c)
        self.config()
        super().activate(i2c, state)

    def calculate_voltage(self):
        distance = min(max(self.vl53l0x.ping() - VL53L0X_OFFSET_MM, 0), VL53L0X_MAX_MM)
        voltage = distance / VL53L0X_MAX_MM * MAX_VOLTAGE
        oled.centre_text(f"{distance} mm\n{voltage:.2f} V")

    def config(self):
        self.vl53l0x.set_Vcsel_pulse_period(self.vl53l0x.vcsel_period_type[0], self.pre_period)
        self.vl53l0x.set_Vcsel_pulse_period(self.vl53l0x.vcsel_period_type[1], self.final_period)
        

class SonicDistanceSensorHCSR04(Sensor):
    def __init__(self, output):
        super().__init__("Sonic distance", "HC-SR04", 0x57, output)

    def activate(self, i2c, state):
        super().activate(i2c, state)


class LightSensorGY302(Sensor):
    def __init__(self, output):
        super().__init__("Light", "GY302 (BH1750)", 0x23, output)

    def activate(self, i2c):
        super().activate(i2c)


class SensitiveEuroPi(EuroPiScript):

    sensors = [
        LaserDistanceSensorVL53L0X(cv1),
        SonicDistanceSensorHCSR04(cv2),
        LightSensorGY302(cv3)
        ];

    def __init__(self):
        super().__init__()

        # Configure EuroPi options to improve performance.
        b1.debounce_delay = 200
        oled.contrast(0)  # dim the oled

        state = self.load_state_json()
        #self.enabled = self.state.get("enabled", True)

        #din.handler(self.increment_counter)
        #b1.handler(self.toggle_enablement)

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

#    def increment_counter(self):
#        if self.enabled:
#            self.counter += 1
#            self.save_state()

#    def toggle_enablement(self):
#            self.enabled = not self.enabled
#            self.save_state()

#    def save_state(self):
#        """Save the current state variables as JSON."""
#        # Don't save if it has been less than 5 seconds since last save.
#        if self.last_saved() < 5000:
#            return
# 
#         state = {
#             .... ADD SENSOR STATES
#         }
#         self.save_state_json(state)

    def main(self):
        oled.centre_text(f"Sensitive EuroPi\n{VERSION}")
        sleep(2)
        while True:
            for sensor in self.sensors:
                sensor.update()


# Main script execution
if __name__ == '__main__':
    script = SensitiveEuroPi()
    script.main()
