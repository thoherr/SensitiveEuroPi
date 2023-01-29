from time import sleep
from europi import oled, b1, din, cv1
from europi_script import EuroPiScript
from machine import Pin, I2C
from vl53l0x import VL53L0X

VERSION = "0.1"

VL53L0X_OFFSET = 30
VL53L0X_MAX = 999
MAX_VOLTAGE = 9.99

class SensitiveEuroPi(EuroPiScript):
    def __init__(self):
        super().__init__()
        state = self.load_state_json()

        #self.counter = state.get("counter", 0)
        #self.enabled = state.get("enabled", True)

        #din.handler(self.increment_counter)
        #b1.handler(self.toggle_enablement)

        self.i2c = self.init_i2c()
        self.vl53l0x = self.init_vl53l0x(self.i2c)

    def init_i2c(self):
        # TODO: make this configurable
        sda = Pin(2)
        scl = Pin(3)
        id = 1
        return I2C(id=id, sda=sda, scl=scl)

    def init_vl53l0x(self, i2c):
        tof = VL53L0X(i2c)

        # Pre: 12 to 18 (initialized to 14 by default)
        # Final: 8 to 14 (initialized to 10 by default)

        tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 18)
        # tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 12)

        tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 14)
        # tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 8)

        return tof
        
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
            "counter": self.counter,
            "enabled": self.enabled,
        }
        self.save_state_json(state)

    def main(self):
        oled.centre_text(f"Sensitive EuroPi\n{VERSION}")
        sleep(2)
        while True:
            distance = min(max(self.vl53l0x.ping() - VL53L0X_OFFSET, 0), VL53L0X_MAX)
            voltage = distance / VL53L0X_MAX * MAX_VOLTAGE
            cv1.voltage(voltage)
            oled.centre_text(f"{distance} mm\n{voltage:.2f} V")
            sleep(0.1)

if __name__ == "__main__":
    SensitiveEuroPi().main()
