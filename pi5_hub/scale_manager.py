"""
FarmTrace — HX711 Load Cell Manager (5 kg)
Tares automatically on startup. Exposes get_weight_kg() for UI polling.
"""
import threading, logging, time, random

log = logging.getLogger(__name__)

class ScaleManager:
    def __init__(self, config: dict):
        self.cfg = config
        self.simulate = config.get("simulate_sensors", False)
        self._weight = 0.0
        self._lock = threading.Lock()
        self._hx = None

        if not self.simulate:
            self._init_hardware()

    def _init_hardware(self):
        try:
            from hx711 import HX711
            sc = self.cfg["scale"]
            self._hx = HX711(dout_pin=sc["dout_pin"], pd_sck_pin=sc["sck_pin"])
            self._hx.set_scale_ratio(sc.get("calibration_factor", 420.0))
            if sc.get("tare_on_startup", True):
                self._hx.tare()
            log.info("HX711 load cell initialised and tared")
        except Exception as e:
            log.warning("HX711 init failed (%s) — switching to simulate", e)
            self.simulate = True

    def start(self):
        t = threading.Thread(target=self._loop, daemon=True, name="Scale")
        t.start()

    def _loop(self):
        while True:
            w = self._read()
            with self._lock:
                self._weight = max(0.0, w)
            time.sleep(0.5)

    def _read(self) -> float:
        if self.simulate:
            return round(random.uniform(0.5, 4.5), 2)
        try:
            return self._hx.get_weight_mean(readings=5) / 1000.0
        except Exception:
            return 0.0

    def get_weight_kg(self) -> float:
        with self._lock:
            return self._weight

    def tare(self):
        if not self.simulate and self._hx:
            self._hx.tare()
            log.info("Scale tared")
