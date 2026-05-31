"""
FarmTrace — Sensor Manager
Reads DHT22 (temp/humidity), soil moisture, and GPS.
Set simulate_sensors=true in config to run without hardware.
DHT22 is on GPIO 4 (Pin 7) by default.
"""
import time, logging, threading, random
from datetime import datetime
from .database import get_conn

log = logging.getLogger(__name__)

class SensorManager:
    def __init__(self, config: dict):
        self.cfg = config
        self.simulate = config.get("simulate_sensors", False)
        self.latest = {"temp_c": None, "humidity": None, "soil_pct": None,
                       "lat": None, "lon": None, "ts": None}
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._dht  = None

        if not self.simulate:
            self._init_hardware()

    def _init_hardware(self):
        try:
            import adafruit_dht, board
            pin_num = self.cfg["sensors"]["dht22_pin"]
            pin_map = {
                4:  board.D4,
                17: board.D17,
                27: board.D27,
                22: board.D22,
                23: board.D23,
            }
            dht_pin = pin_map.get(pin_num)
            if dht_pin is None:
                raise ValueError(f"GPIO {pin_num} not in supported pin map")
            self._dht = adafruit_dht.DHT22(dht_pin)
            log.info("DHT22 initialised on GPIO %d (Pin %d)", pin_num,
                     {4:7, 17:11, 27:13, 22:15, 23:16}.get(pin_num, pin_num))
        except Exception as e:
            log.warning("DHT22 init failed (%s) — switching to simulate", e)
            self.simulate = True

    def start(self):
        t = threading.Thread(target=self._loop, daemon=True, name="SensorMgr")
        t.start()
        log.info("SensorManager started (simulate=%s)", self.simulate)

    def stop(self):
        self._stop.set()

    def get_latest(self) -> dict:
        with self._lock:
            return dict(self.latest)

    def _loop(self):
        interval = self.cfg["sensors"].get("poll_interval_seconds", 30)
        while not self._stop.wait(interval):
            reading = self._read()
            with self._lock:
                self.latest = reading
            self._store(reading)

    def _read(self) -> dict:
        ts = datetime.utcnow().isoformat()
        if self.simulate:
            return {
                "ts":       ts,
                "temp_c":   round(20 + random.uniform(0, 10), 1),
                "humidity": round(50 + random.uniform(0, 30), 1),
                "soil_pct": round(30 + random.uniform(0, 40), 1),
                "lat":  self.cfg["hub_gps"]["lat"] + random.uniform(-0.001, 0.001),
                "lon":  self.cfg["hub_gps"]["lon"] + random.uniform(-0.001, 0.001),
            }
        temp, hum = self._read_dht22()
        soil      = self._read_soil()
        lat, lon  = self._read_gps()
        return {"ts": ts, "temp_c": temp, "humidity": hum,
                "soil_pct": soil, "lat": lat, "lon": lon}

    def _read_dht22(self):
        """Try up to 3 times — DHT22 occasionally misreads, that is normal."""
        if not self._dht:
            return None, None
        for attempt in range(3):
            try:
                temp = self._dht.temperature
                hum  = self._dht.humidity
                if temp is not None and hum is not None:
                    log.debug("DHT22 read OK: %.1f°C  %.1f%%", temp, hum)
                    return temp, hum
            except RuntimeError as e:
                log.debug("DHT22 read attempt %d failed: %s", attempt + 1, e)
                time.sleep(0.5)
            except Exception as e:
                log.warning("DHT22 unexpected error: %s", e)
                break
        log.warning("DHT22 failed all 3 read attempts — returning None")
        return None, None

    def _read_soil(self):
        try:
            import spidev
            spi = spidev.SpiDev()
            spi.open(0, 0)
            spi.max_speed_hz = 1350000
            channel = self.cfg["sensors"].get("soil_adc_channel", 0)
            adc = spi.xfer2([1, (8 + channel) << 4, 0])
            spi.close()
            val = ((adc[1] & 3) << 8) + adc[2]
            return round((1 - val / 1023) * 100, 1)
        except Exception:
            return None

    def _read_gps(self):
        gps_cfg = self.cfg.get("hub_gps", {})
        if gps_cfg.get("simulate"):
            return gps_cfg.get("lat"), gps_cfg.get("lon")
        try:
            import serial, pynmea2
            with serial.Serial("/dev/ttyAMA0", 9600, timeout=1) as ser:
                for _ in range(20):
                    line = ser.readline().decode("ascii", errors="ignore").strip()
                    if line.startswith("$GPGGA"):
                        msg = pynmea2.parse(line)
                        return float(msg.latitude), float(msg.longitude)
        except Exception as e:
            log.debug("GPS read error: %s", e)
        return None, None

    def _store(self, r: dict):
        try:
            conn = get_conn()
            conn.execute(
                "INSERT INTO sensor_readings (ts,temp_c,humidity,soil_pct,lat,lon) "
                "VALUES (?,?,?,?,?,?)",
                (r["ts"], r["temp_c"], r["humidity"],
                 r["soil_pct"], r["lat"], r["lon"])
            )
            conn.commit()
            conn.close()
            if r["temp_c"]:
                log.info("Sensor stored: temp=%.1f°C  humidity=%.1f%%",
                         r["temp_c"], r["humidity"])
        except Exception as e:
            log.warning("DB store error: %s", e)
