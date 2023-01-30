"""
Sensitive Euro Pi - generating CV from sensor reading
author: Thomas Herrmann (github.com/thoherr)
date: 2023-01-29
labels: sensor

digital_in: not used
analog_in: not used

knob_1: adjust the value of the current configuration parameter
knob_2: not used

button_1: cycle through editable configuration parameter
button_2: edit current configuration parameter

output_1: VL53L0X CV
output_2: not used
output_3: not used
output_4: not used
output_5: not used
output_6: not used

"""

from time import sleep
from europi import oled, b1, din, cv1
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

pre_periods = [12, 14, 16, 18]
final_periods = [8, 10, 12, 14]

class Sensor:
    active = False
    def __init__(self, name, type, i2c_address):
        self.name = name
        self.type = type
        self.i2c_address = i2c_address

    def __str__(self):
        status = f"@ 0x{self.i2c_address:x}" if self.active else "not connected"
        return f"{self.name} - {self.type} {status}"

    def activate(self):
        self.active = True


class LaserDistanceSensorVL53L0X(Sensor):
    def __init__(self):
        super().__init__("Laser distance", "VL53L0X", 0x29)

    def activate(self):
        super().activate()


class SonicDistanceSensorHCSR04(Sensor):
    def __init__(self):
        super().__init__("Sonic distance", "HC-SR04", 0x57)

    def activate(self):
        super().activate()


class LightSensorGY302(Sensor):
    def __init__(self):
        super().__init__("Light", "GY302 (BH1750)", 0x23)

    def activate(self):
        super().activate()


class SensitiveEuroPi(EuroPiScript):

    sensors = [
        LaserDistanceSensorVL53L0X(),
        SonicDistanceSensorHCSR04(),
        LightSensorGY302()
        ];

    def __init__(self):
        super().__init__()

        # Configure EuroPi options to improve performance.
        b1.debounce_delay = 200
        oled.contrast(0)  # dim the oled

        state = self.load_state_json()

        # Pre: 12 to 18 (initialized to 14 by default)
        self.pre_period = state.get("pre_period", 14)
        # Final: 8 to 14 (initialized to 10 by default)
        self.final_period = state.get("final_period", 10)

        #self.enabled = state.get("enabled", True)

        #din.handler(self.increment_counter)
        #b1.handler(self.toggle_enablement)

        self.i2c = I2C(id=I2C_ID, sda=Pin(I2C_SDA_PIN), scl=Pin(I2C_SCL_PIN))

        self.init_sensors()

        self.vl53l0x = VL53L0X(self.i2c)
        self.config_vl53l0x()

        for sensor in self.sensors:
            print(sensor)

    def init_sensors(self):
        i2c_addresses = self.i2c.scan()
        print(i2c_addresses)
        for sensor in self.sensors:
            if sensor.i2c_address in i2c_addresses:
                sensor.activate()
                print(f"{sensor.name} present")
            else:
                print(f"{sensor.name} not found")
                

    def config_vl53l0x(self):
        self.vl53l0x.set_Vcsel_pulse_period(self.vl53l0x.vcsel_period_type[0], self.pre_period)
        self.vl53l0x.set_Vcsel_pulse_period(self.vl53l0x.vcsel_period_type[1], self.final_period)
        
    @classmethod
    def display_name(cls):
        return "Sensitive EuroPi"

    def increment_counter(self):
        if self.enabled:
            self.counter += 1
            self.save_state()

    def toggle_enablement(self):
            self.enabled = not self.enabled
            self.save_state()

    def save_state(self):
        """Save the current state variables as JSON."""
        # Don't save if it has been less than 5 seconds since last save.
        if self.last_saved() < 5000:
            return

        state = {
            "pre_period": self.pre_period,
            "final_period": self.final_period,
        }
        self.save_state_json(state)

    def main(self):
        oled.centre_text(f"Sensitive EuroPi\n{VERSION}")
        sleep(2)
        while True:
            distance = min(max(self.vl53l0x.ping() - VL53L0X_OFFSET_MM, 0), VL53L0X_MAX_MM)
            voltage = distance / VL53L0X_MAX_MM * MAX_VOLTAGE
            cv1.voltage(voltage)
            oled.centre_text(f"{distance} mm\n{voltage:.2f} V")
            sleep(0.1)


# Main script execution
if __name__ == '__main__':
    script = SensitiveEuroPi()
    script.main()
