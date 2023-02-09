# SensitiveEuroPi

EuroPI application that creates CV output from several I2C sensors

## Basic idea

Inspired by Eurorack-Modules interacting with the environment, like e.g. Dieter Doepfer's Theremin (https://doepfer.de/a178.htm) and light controlled voltage source (https://doepfer.de/A1792.htm), I wanted to add some environmental influencce to my modular system.

I recently got a EuroPi module from Allen Synthesis (https://github.com/Allen-Synthesis/EuroPi), which introduces a Raspberry Pi Pico to the modular world. This module seemed to be the perfect starting point to add some sensory to my rack.

Since the EuroPi provides an I2C bus for expansion, I decided to concentrate on I2C capable sensory.

The connection to the sensors is done via an expansion panel. I use TRRS plugs to connect the sensors to the EuroPi module (see [hardware](hardware/README.md)).

## Overview

Supported sensors are specified by their I2C id and name. SensitiveEuroPi holds a table of known values and checks
the I2C devices on startup.

The connected devices are assigned to one of the 6 output channels of EuroPi. The output CV for each channel can be configured by a factor that is multiplied with the sensor reading.

TBD

## Supported sensors

* GY-302 - light sensor
* VL53L0X - laser distance sensor

## Planned sensors

* HC-SR04 - ultrasonic distance sensor

## Installation and configuration

TBD

## Caveats / Missing features

* poor error handling
* settings/configuration missing
* enabling/disabling sensors based on I2C scan

