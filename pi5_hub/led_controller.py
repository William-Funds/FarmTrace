"""
FarmTrace — LED Controller
Green  (GPIO 18) : Heartbeat — slow blink always while system runs
Yellow (GPIO 23) : Activity  — fast blink during parcel/photo/lookup tasks
Red    (GPIO 24) : Passport  — solid ON when passport generated and email sent
"""
import RPi.GPIO as GPIO
import threading
import time
import logging

log = logging.getLogger(__name__)

GREEN  = 18
YELLOW = 23
RED    = 24

class LEDController:
    def __init__(self, config: dict):
        self.simulate = config.get("simulate_sensors", False)
        self._stop = threading.Event()
        self._yellow_active = False
        self._lock = threading.Lock()

        if not self.simulate:
            self._init_gpio()
        else:
            log.info("LED controller in simulate mode — no GPIO")

    def _init_gpio(self):
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(GREEN,  GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(YELLOW, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(RED,    GPIO.OUT, initial=GPIO.LOW)
            log.info("LED GPIO initialised — Green:18 Yellow:23 Red:24")
        except Exception as e:
            log.warning("GPIO init failed (%s) — LEDs disabled", e)
            self.simulate = True

    def _set(self, pin, state):
        if not self.simulate:
            try:
                GPIO.output(pin, GPIO.HIGH if state else GPIO.LOW)
            except Exception:
                pass

    # ── Heartbeat — green slow blink always ──────────────────────────────
    def start_heartbeat(self):
        def _blink():
            while not self._stop.wait(0.1):
                self._set(GREEN, True)
                time.sleep(0.8)
                if self._stop.is_set():
                    break
                self._set(GREEN, False)
                time.sleep(1.2)
        threading.Thread(target=_blink, daemon=True, name="GreenBlink").start()
        log.info("Heartbeat LED started")

    # ── Yellow — fast blink during any active task ────────────────────────
    def start_activity(self):
        """Call this when a task starts — yellow blinks fast."""
        with self._lock:
            self._yellow_active = True
        def _fast_blink():
            while True:
                with self._lock:
                    if not self._yellow_active:
                        self._set(YELLOW, False)
                        break
                self._set(YELLOW, True)
                time.sleep(0.1)
                self._set(YELLOW, False)
                time.sleep(0.1)
        threading.Thread(target=_fast_blink, daemon=True, name="YellowBlink").start()

    def stop_activity(self):
        """Call this when a task finishes — yellow stops."""
        with self._lock:
            self._yellow_active = False
        self._set(YELLOW, False)

    # ── Red — solid ON when passport ready ────────────────────────────────
    def signal_ready(self):
        """Passport generated and email sent — red solid ON."""
        self._set(RED, True)
        log.info("Red LED ON — passport ready")

    def signal_error(self):
        """Error occurred — red fast blink 5 times."""
        def _err_blink():
            for _ in range(5):
                self._set(RED, True)
                time.sleep(0.15)
                self._set(RED, False)
                time.sleep(0.15)
        threading.Thread(target=_err_blink, daemon=True, name="RedError").start()

    def reset_ready(self):
        """Turn red off — ready for next batch."""
        self._set(RED, False)

    # ── Startup sequence — show all 3 LEDs on boot ────────────────────────
    def startup_sequence(self):
        """Run once on startup to show system is alive."""
        def _seq():
            for pin in [GREEN, YELLOW, RED]:
                self._set(pin, True)
                time.sleep(0.3)
                self._set(pin, False)
                time.sleep(0.1)
            for _ in range(2):
                for pin in [GREEN, YELLOW, RED]:
                    self._set(pin, True)
                time.sleep(0.2)
                for pin in [GREEN, YELLOW, RED]:
                    self._set(pin, False)
                time.sleep(0.2)
        threading.Thread(target=_seq, daemon=True, name="StartupSeq").start()

    def stop(self):
        self._stop.set()
        self._set(GREEN,  False)
        self._set(YELLOW, False)
        self._set(RED,    False)
        if not self.simulate:
            try:
                GPIO.cleanup()
            except Exception:
                pass
        log.info("LED controller stopped")
