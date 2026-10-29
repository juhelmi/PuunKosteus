import time


def calc_resistance(v, side, vcc, r_ref):
    """Resistance of the sensor from the measured node voltage (ohms).
    Returns None if the divider is open or shorted."""
    if side == "low":
        d = vcc - v
        return r_ref * v / d if d > 0.001 else None
    if v <= 0.001:
        return None
    return r_ref * (vcc - v) / v


def measure(adc, cfg, machine_pin, measure_ms, vcc, r_ref):
    """Excite the divider for measure_ms and average ADC readings."""
    pin = machine_pin(cfg["pin"], machine_pin.OUT)
    pin.value(1 if cfg["side"] == "low" else 0)
    total = 0.0
    n = 0
    t0 = time.ticks_ms()
    try:
        while True:
            total += adc.read_voltage(cfg["adc_ch"])
            n += 1
            if time.ticks_diff(time.ticks_ms(), t0) >= measure_ms:
                break
    finally:
        pin.init(machine_pin.IN)  # hi-Z between measurements
    return calc_resistance(total / n, cfg["side"], vcc, r_ref)
