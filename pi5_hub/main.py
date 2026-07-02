"""
FarmTrace Hub — Main Entry Point
Run from the farmtrace/ root directory:
    python -m pi5_hub.main
"""
import json, os, sys, logging, signal
from datetime import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

os.makedirs(os.path.join(ROOT, "logs"), exist_ok=True)
log_file = os.path.join(ROOT, "logs", f"farmtrace_{datetime.utcnow():%Y%m%d}.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler(sys.stdout)]
)
log = logging.getLogger("main")

CFG_PATH = os.path.join(ROOT, "config", "hub_config.json")
with open(CFG_PATH) as f:
    CONFIG = json.load(f)

from pi5_hub.database       import init_db
from pi5_hub.sensor_manager import SensorManager
from pi5_hub.scale_manager  import ScaleManager
from pi5_hub.led_controller import LEDController
from pi5_hub.camera_manager import CameraManager
from pi5_hub.batch_manager  import BatchManager
from pi5_hub.gsm_manager    import GSMManager
from pi5_hub.chatbot_api    import ChatbotAPI
from cloud_sync.google_sync import GoogleSync
from ui.app                 import FarmTraceApp

def main():
    log.info("=== FarmTrace Hub Starting ===")
    init_db()

    sensors = SensorManager(CONFIG)
    scale   = ScaleManager(CONFIG)
    leds    = LEDController(CONFIG)
    camera  = CameraManager(CONFIG)
    batches = BatchManager(CONFIG)
    gsm     = GSMManager(CONFIG)
    gsync   = GoogleSync(CONFIG)
    chatbot = ChatbotAPI(CONFIG, sensors=sensors)

    sensors.start()
    scale.start()
    leds.startup_sequence()
    leds.start_heartbeat()
    gsync.start()
    chatbot.start()

    log.info("All background services started")

    def _shutdown(sig, frame):
        log.info("Shutting down...")
        sensors.stop(); leds.stop(); gsync.stop(); chatbot.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT,  _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    app = FarmTraceApp(
        config=CONFIG, sensors=sensors, scale=scale,
        leds=leds, camera=camera, batches=batches,
        gsm=gsm, gsync=gsync
    )
    app.run()

if __name__ == "__main__":
    main()
