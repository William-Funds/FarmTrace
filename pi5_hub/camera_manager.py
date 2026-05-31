"""
FarmTrace — Pi AI Camera Manager
Uses rpicam-still command (reliable on Pi 5).
Photos saved to data/photos/ and path stored in parcels DB table.
"""
import os, subprocess, logging
from datetime import datetime

log = logging.getLogger(__name__)

class CameraManager:
    def __init__(self, config: dict):
        self.cfg = config.get("camera", {})
        self.simulate = config.get("simulate_sensors", False)
        self.photo_dir = self.cfg.get("photo_dir", "data/photos")
        os.makedirs(self.photo_dir, exist_ok=True)

    def capture(self, batch_id: str, farmer_name: str) -> str:
        """Capture photo with rpicam-still and return saved file path."""
        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        safe_name = farmer_name.replace(" ", "_")
        filename = f"{batch_id}_{safe_name}_{ts}.jpg"
        filepath = os.path.join(self.photo_dir, filename)

        if self.simulate:
            self._write_placeholder(filepath)
            log.info("Placeholder photo saved: %s", filepath)
            return filepath

        try:
            result = subprocess.run(
                [
                    "rpicam-still",
                    "-o", filepath,
                    "--timeout", "2000",
                    "--nopreview",
                    "--width", "1920",
                    "--height", "1080"
                ],
                capture_output=True,
                text=True,
                timeout=15
            )
            if result.returncode == 0 and os.path.exists(filepath):
                size = os.path.getsize(filepath)
                log.info("Photo captured: %s (%d bytes)", filename, size)
            else:
                log.warning("rpicam-still failed: %s", result.stderr[:200])
                self._write_placeholder(filepath)
        except Exception as e:
            log.warning("Camera capture error: %s", e)
            self._write_placeholder(filepath)

        return filepath

    def _write_placeholder(self, path: str):
        """Minimal 1x1 white JPEG placeholder."""
        PLACEHOLDER = bytes([
            0xFF,0xD8,0xFF,0xE0,0x00,0x10,0x4A,0x46,0x49,0x46,0x00,0x01,
            0x01,0x00,0x00,0x01,0x00,0x01,0x00,0x00,0xFF,0xDB,0x00,0x43,
            0x00,0x08,0x06,0x06,0x07,0x06,0x05,0x08,0x07,0x07,0x07,0x09,
            0x09,0x08,0x0A,0x0C,0x14,0x0D,0x0C,0x0B,0x0B,0x0C,0x19,0x12,
            0x13,0x0F,0x14,0x1D,0x1A,0x1F,0x1E,0x1D,0x1A,0x1C,0x1C,0x20,
            0x24,0x2E,0x27,0x20,0x22,0x2C,0x23,0x1C,0x1C,0x28,0x37,0x29,
            0x2C,0x30,0x31,0x34,0x34,0x34,0x1F,0x27,0x39,0x3D,0x38,0x32,
            0x3C,0x2E,0x33,0x34,0x32,0xFF,0xC0,0x00,0x0B,0x08,0x00,0x01,
            0x00,0x01,0x01,0x01,0x11,0x00,0xFF,0xC4,0x00,0x1F,0x00,0x00,
            0x01,0x05,0x01,0x01,0x01,0x01,0x01,0x01,0x00,0x00,0x00,0x00,
            0x00,0x00,0x00,0x00,0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,
            0x09,0x0A,0x0B,0xFF,0xDA,0x00,0x08,0x01,0x01,0x00,0x00,0x3F,
            0x00,0xFB,0xD2,0x8A,0x28,0x03,0xFF,0xD9
        ])
        with open(path, 'wb') as f:
            f.write(PLACEHOLDER)

    def stop(self):
        pass
