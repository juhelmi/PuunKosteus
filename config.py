# Configuration for PuunKosteus (Raspberry Pi Pico 2 W, MicroPython)

WIFI_SSID = "your-ssid"
WIFI_PASSWORD = "your-password"

MQTT_BROKER = "192.168.1.10"
MQTT_PORT = 1883
MQTT_USER = None
MQTT_PASSWORD = None
MQTT_CLIENT_ID = "puunkosteus"
MQTT_TOPIC = b"puunkosteus/measurements"

# I2C bus of ADS1115
I2C_ID = 0
I2C_SDA = 4
I2C_SCL = 5
ADS_ADDR = 0x48

# Measurement interval and measuring (excitation) time
INTERVAL_S = 3600
MEASURE_MS = 30

# Supply voltage of the divider (GPIO high level)
VCC = 3.3
R_REF = 1000000  # 1 Mohm pull up / pull down resistor

# Two resistors to measure. GPIO configuration is to be defined later.
#  adc_ch : ADS1115 input AIN0..AIN3
#  side   : "low"  = sensor between ADC node and GND, reference is pull up
#                    (excitation pin driven high while measuring)
#           "high" = sensor between Vcc and ADC node, reference is pull down
#                    (excitation pin driven low while measuring)
#  pin    : GPIO driving the reference resistor (hi-Z when not measuring)
CHANNELS = [
    {"name": "r1", "adc_ch": 0, "side": "low", "pin": 14},
    {"name": "r2", "adc_ch": 1, "side": "low", "pin": 15},
]

HISTORY_LEN = 168  # one week of hourly samples
HTTP_PORT = 80
