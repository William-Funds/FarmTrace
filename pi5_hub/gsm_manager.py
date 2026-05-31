"""
FarmTrace — GSM Manager (STUB — ready for your module)
Set gsm.enabled=true in hub_config.json once you have the hardware.
Supports SIM800L (SMS only) and SIM7600/EC21 (SMS + HTTP POST).
"""
import logging, threading, time
log = logging.getLogger(__name__)

class GSMManager:
    def __init__(self, config):
        self.cfg = config.get("gsm", {})
        self.enabled = self.cfg.get("enabled", False)
        self._serial = None; self._lock = threading.Lock()
        if self.enabled: self._init_serial()

    def _init_serial(self):
        try:
            import serial
            self._serial = serial.Serial(
                port=self.cfg.get("port", "/dev/ttyUSB0"),
                baudrate=self.cfg.get("baud", 115200), timeout=5)
            time.sleep(2)
            if "OK" in self._at("AT"):
                log.info("GSM module ready on %s", self.cfg["port"])
            else:
                log.warning("GSM module not responding")
        except Exception as e:
            log.warning("GSM init failed (%s)", e); self.enabled = False

    def _at(self, cmd, wait=1.0):
        if not self._serial: return ""
        with self._lock:
            self._serial.write((cmd + "\r\n").encode())
            time.sleep(wait)
            return self._serial.read(self._serial.in_waiting).decode(errors="ignore")

    def send_sms(self, number, message):
        if not self.enabled:
            log.info("[GSM STUB] SMS to %s: %s", number, message); return True
        try:
            self._at("AT+CMGF=1")
            self._at(f'AT+CMGS="{number}"', 0.5)
            with self._lock:
                self._serial.write((message + chr(26)).encode())
                time.sleep(3)
            log.info("SMS sent to %s", number); return True
        except Exception as e:
            log.error("SMS failed: %s", e); return False

    def notify_passport_ready(self, batch_id, buyer_number, passport_path=None):
        """Call this after passport generation to notify the buyer."""
        msg = f"FarmTrace: Batch {batch_id} passport ready. Verify at farmtrace.coop/verify/{batch_id}"
        self.send_sms(buyer_number, msg)

    # HTTP POST — SIM7600 / EC21 only (not SIM800L)
    def send_http_post(self, url, json_data):
        import json
        body = json.dumps(json_data)
        if not self.enabled:
            log.info("[GSM STUB] POST %s: %s", url, body[:60]); return True
        try:
            self._at(f'AT+HTTPURL="{url}",10000')
            self._at("AT+HTTPMETHOD=1")
            self._at('AT+HTTPPARA="Content-Type","application/json"')
            self._at(f"AT+HTTPDATA={len(body)},10000")
            self._at(body)
            resp = self._at("AT+HTTPACTION=1", wait=5)
            return "200" in resp
        except Exception as e:
            log.error("HTTP POST failed: %s", e); return False
