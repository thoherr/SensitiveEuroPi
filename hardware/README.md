# Hardware used to connect sensors

The EuroPI features a (second) I2C bus, which has a 4 pin connector on the PCB right between the
Raspberry Pi Pico and the power connector.

The pins are (going from top to bottom on the PCB)

4 - SDA  
3 - SCL  
2 - 3V3  
1 - GND

In order to be able to connect sensors while the module is mounted in my rack, I used a TRRS connection with
a jack mounted on a blank module panel and connected my sensors to a replacement audio cablei
for headphones and microphone (see picture).

![TRRS jack and plug](TRRS.png)

I used [this jack](https://www.amazon.de/-/en/dp/B089222S84?psc=1&ref=ppx_yo2ov_dt_b_product_details)
and [this plug with cable](https://www.amazon.de/-/en/dp/B0B3R6BM1B?psc=1&ref=ppx_yo2ov_dt_b_product_details).
