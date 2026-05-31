"""
FarmTrace — Google Sync (Sheets + Drive)
Queues sync jobs locally; processes them with retry + back-off.
Enable by setting google.enabled=true in hub_config.json.
"""
import os, json, logging, time, threading
from datetime import datetime
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from pi5_hub.database import get_conn

log = logging.getLogger(__name__)

class GoogleSync:
    def __init__(self, config):
        self.cfg = config.get("google", {})
        self.enabled = self.cfg.get("enabled", False)
        self._stop = threading.Event()
        self._sheets = self._drive = None
        if self.enabled:
            self._init_services()

    def _init_services(self):
        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
                      "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_file(
                self.cfg["credentials_file"], scopes=SCOPES)
            self._sheets = build("sheets", "v4", credentials=creds)
            self._drive  = build("drive",  "v3", credentials=creds)
            log.info("Google services initialised")
        except Exception as e:
            log.warning("Google init failed (%s) — sync disabled", e)
            self.enabled = False

    def start(self):
        threading.Thread(target=self._loop, daemon=True, name="GoogleSync").start()

    def stop(self): self._stop.set()

    def _loop(self):
        interval = self.cfg.get("sync_interval_seconds", 300)
        while not self._stop.wait(interval):
            if self.enabled: self._process_queue()

    def queue_batch(self, batch, parcels, passport_path):
        payload = json.dumps({"batch": dict(batch), "parcels": [dict(p) for p in parcels],
                               "passport_path": passport_path})
        conn = get_conn()
        conn.execute("INSERT INTO sync_queue (record_type,record_id,payload,created_at) VALUES (?,?,?,?)",
                     ("batch", batch["id"], payload, datetime.utcnow().isoformat()))
        conn.commit(); conn.close()
        log.info("Queued batch %s for Google sync", batch["batch_id"])

    def _process_queue(self):
        conn = get_conn()
        rows = conn.execute("SELECT * FROM sync_queue WHERE attempts < 5 ORDER BY id LIMIT 10").fetchall()
        conn.close()
        for row in rows:
            try:
                payload = json.loads(row["payload"])
                if row["record_type"] == "batch":
                    self._sync_batch(payload)
                conn2 = get_conn()
                conn2.execute("DELETE FROM sync_queue WHERE id=?", (row["id"],))
                conn2.commit(); conn2.close()
            except Exception as e:
                log.warning("Sync item %d failed: %s", row["id"], e)
                conn2 = get_conn()
                conn2.execute("UPDATE sync_queue SET attempts=attempts+1, last_error=? WHERE id=?",
                              (str(e), row["id"]))
                conn2.commit(); conn2.close()
                time.sleep(min(60, 2 ** row["attempts"]))

    def _sync_batch(self, payload):
        batch = payload["batch"]
        parcels = payload["parcels"]
        passport_path = payload.get("passport_path")
        if self._sheets:
            row = [[batch["batch_id"], batch["crop_type"],
                    batch["current_kg"], batch.get("buyer_name",""),
                    batch.get("locked_at",""), len(parcels), batch.get("passport_hash","")]]
            self._sheets.spreadsheets().values().append(
                spreadsheetId=self.cfg["sheet_id"], range="Sheet1!A:G",
                valueInputOption="RAW", body={"values": row}).execute()
        if self._drive and passport_path and os.path.exists(passport_path):
            from googleapiclient.http import MediaFileUpload
            media = MediaFileUpload(passport_path, mimetype="application/pdf")
            self._drive.files().create(
                body={"name": os.path.basename(passport_path),
                      "parents": [self.cfg.get("drive_folder_id","")]},
                media_body=media).execute()
            log.info("Passport uploaded to Drive: %s", os.path.basename(passport_path))
