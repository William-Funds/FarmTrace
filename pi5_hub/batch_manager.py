"""
FarmTrace — Batch Manager
Creates and manages harvest batches. Auto-locks when target weight reached.
"""
import logging, json
from datetime import datetime
from .database import get_conn

log = logging.getLogger(__name__)

CROP_CODES = {
    "avocado": "AVO", "groundnuts": "GNT", "small grains": "SGM",
    "maize": "MLT", "tomatoes": "TOM", "other": "OTH"
}

class BatchManager:
    def __init__(self, config: dict):
        self.cfg = config
        self.country = config.get("country", "ZW")

    def _next_seq(self, date_str: str, crop_code: str) -> str:
        conn = get_conn()
        like = f"{self.country}-{crop_code}-{date_str}-%"
        row = conn.execute(
            "SELECT COUNT(*) FROM batches WHERE batch_id LIKE ?", (like,)
        ).fetchone()
        conn.close()
        return str((row[0] if row else 0) + 1).zfill(4)

    def create_batch(self, crop_type: str, buyer_name: str,
                     buyer_email: str, target_kg: float) -> dict:
        date_str = datetime.utcnow().strftime("%Y%m%d")
        crop_code = CROP_CODES.get(crop_type.lower(), "OTH")
        seq = self._next_seq(date_str, crop_code)
        batch_id = f"{self.country}-{crop_code}-{date_str}-{seq}"

        conn = get_conn()
        conn.execute(
            """INSERT INTO batches
               (batch_id, crop_type, buyer_name, buyer_email, target_kg, created_at)
               VALUES (?,?,?,?,?,?)""",
            (batch_id, crop_type, buyer_name, buyer_email, target_kg,
             datetime.utcnow().isoformat())
        )
        conn.commit(); conn.close()
        log.info("Batch created: %s", batch_id)
        return self.get_batch(batch_id)

    def add_parcel(self, batch_id: str, farmer_name: str, farmer_id: str,
                   weight_kg: float, lat: float, lon: float,
                   location_name: str = None,
                   photo_path: str = None) -> dict:
        conn = get_conn()
        batch = conn.execute(
            "SELECT * FROM batches WHERE batch_id=?", (batch_id,)
        ).fetchone()

        if not batch:
            conn.close(); raise ValueError(f"Batch {batch_id} not found")
        if batch["status"] != "open":
            conn.close(); raise ValueError(f"Batch {batch_id} is {batch['status']}")

        conn.execute(
            """INSERT INTO parcels
               (batch_id, farmer_name, farmer_id, weight_kg, lat, lon,
                location_name, harvest_date, photo_path, added_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (batch_id, farmer_name, farmer_id, weight_kg, lat, lon,
             location_name, datetime.utcnow().strftime("%Y-%m-%d"), photo_path,
             datetime.utcnow().isoformat())
        )
        new_total = batch["current_kg"] + weight_kg
        conn.execute(
            "UPDATE batches SET current_kg=? WHERE batch_id=?",
            (new_total, batch_id)
        )
        conn.commit()

        # Auto-lock if target reached
        if self.cfg["batch"].get("auto_lock") and new_total >= batch["target_kg"]:
            conn.execute(
                "UPDATE batches SET status=?,locked_at=? WHERE batch_id=?",
                ("locked", datetime.utcnow().isoformat(), batch_id)
            )
            conn.commit()
            log.info("Batch %s auto-locked at %.1f kg", batch_id, new_total)
        conn.close()
        return self.get_batch(batch_id)

    def lock_batch(self, batch_id: str) -> dict:
        conn = get_conn()
        conn.execute(
            "UPDATE batches SET status=?,locked_at=? WHERE batch_id=?",
            ("locked", datetime.utcnow().isoformat(), batch_id)
        )
        conn.commit(); conn.close()
        log.info("Batch %s locked manually", batch_id)
        return self.get_batch(batch_id)

    def get_batch(self, batch_id: str) -> dict:
        conn = get_conn()
        row = conn.execute(
            "SELECT * FROM batches WHERE batch_id=?", (batch_id,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def get_all_batches(self) -> list:
        conn = get_conn()
        rows = conn.execute(
            "SELECT * FROM batches ORDER BY created_at DESC"
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_parcels(self, batch_id: str) -> list:
        conn = get_conn()
        rows = conn.execute(
            "SELECT * FROM parcels WHERE batch_id=? ORDER BY added_at",
            (batch_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]
