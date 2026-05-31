"""
FarmTrace — Email Sender
Sends passport PDF to buyer automatically on batch lock.
Uses Gmail SMTP with App Password — no Google API needed.
"""
import smtplib, os, logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

log = logging.getLogger(__name__)


def send_passport_email(config: dict, batch: dict, passport_path: str,
                         parcels: list) -> bool:
    """
    Send passport PDF to buyer email.
    Returns True if sent successfully, False otherwise.
    """
    email_cfg = config.get("email", {})

    if not email_cfg.get("enabled", False):
        log.info("Email sending disabled in config — skipping")
        return False

    sender_email  = email_cfg.get("sender_email", "")
    sender_name   = email_cfg.get("sender_name", "FarmTrace Cooperative")
    app_password  = email_cfg.get("app_password", "")
    buyer_email   = batch.get("buyer_email", "")
    buyer_name    = batch.get("buyer_name", "Buyer")

    if not all([sender_email, app_password, buyer_email]):
        log.warning("Email config incomplete — sender, password or buyer email missing")
        return False

    if not os.path.exists(passport_path):
        log.warning("Passport PDF not found at %s", passport_path)
        return False

    # ── Build email ───────────────────────────────────────────────────────
    msg = MIMEMultipart()
    msg["From"]    = f"{sender_name} <{sender_email}>"
    msg["To"]      = buyer_email
    msg["Subject"] = (f"FarmTrace Digital Trade Passport — "
                      f"Batch {batch['batch_id']} | "
                      f"{batch['crop_type'].title()} | "
                      f"{batch['current_kg']:.1f} kg")

    # ── Email body ────────────────────────────────────────────────────────
    body = f"""Dear {buyer_name},

Please find attached the Digital Trade Passport for your recent order.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BATCH SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Batch ID      : {batch['batch_id']}
  Crop Type     : {batch['crop_type'].title()}
  Total Weight  : {batch['current_kg']:.2f} kg
  No. Farmers   : {len(parcels)}
  Cooperative   : {config.get('cooperative_name', 'FarmTrace Cooperative')}
  Generated     : {datetime.utcnow().strftime('%d %B %Y at %H:%M UTC')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FARMER CONTRIBUTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    for i, p in enumerate(parcels, 1):
        body += f"\n  {i}. {p['farmer_name']:<20}  {p['weight_kg']:.2f} kg"

    body += f"""

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The attached PDF passport contains:
  • Full farmer traceability records with GPS coordinates
  • Farmer photos captured at time of weighing
  • Environmental sensor data (temperature, humidity, soil moisture)
  • COMESA/SADC compliance checklist
  • Chain of custody with signature blocks
  • SHA-256 integrity hash for tamper detection

This passport was generated automatically by the FarmTrace Hub
and is ready for border inspection and buyer verification.

Kind regards,
{sender_name}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Powered by FarmTrace — Giving smallholder farmers the proof,
visibility and scale they deserve.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
    msg.attach(MIMEText(body, "plain"))

    # ── Attach PDF ────────────────────────────────────────────────────────
    with open(passport_path, "rb") as f:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename={os.path.basename(passport_path)}"
    )
    msg.attach(part)

    # ── Send via Gmail SMTP ───────────────────────────────────────────────
    try:
        log.info("Sending passport email to %s ...", buyer_email)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, buyer_email, msg.as_string())
        log.info("Email sent successfully to %s", buyer_email)
        return True
    except smtplib.SMTPAuthenticationError:
        log.error("Gmail authentication failed — check your App Password in config")
        return False
    except smtplib.SMTPException as e:
        log.error("SMTP error sending email: %s", e)
        return False
    except Exception as e:
        log.error("Email send failed: %s", e)
        return False
