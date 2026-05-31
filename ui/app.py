"""
FarmTrace — Vibrant Touchscreen UI
Rich green agricultural theme with gradients, emoji icons, card layouts,
colour-coded status badges and animated feedback.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging, threading
from datetime import datetime

log = logging.getLogger(__name__)

# ── Colour Palette ────────────────────────────────────────────────────────────
C = {
    "bg_dark":    "#0A2E0A",   # very dark green background
    "bg_mid":     "#1B5E20",   # mid green panels
    "bg_card":    "#1E4620",   # card background
    "bg_header":  "#003300",   # header strip
    "accent1":    "#4CAF50",   # bright green
    "accent2":    "#8BC34A",   # lime green
    "accent3":    "#FFEB3B",   # yellow highlight
    "accent4":    "#FF9800",   # orange / amber
    "accent5":    "#00BCD4",   # cyan for scale
    "red":        "#F44336",
    "white":      "#FFFFFF",
    "offwhite":   "#E8F5E9",
    "grey":       "#A5D6A7",
    "text_dim":   "#81C784",
}

FONT_XL  = ("Courier", 20, "bold")
FONT_L   = ("Courier", 15, "bold")
FONT_M   = ("Courier", 12, "bold")
FONT_S   = ("Courier", 10)
FONT_XS  = ("Courier", 9)

BTN_OPTS = dict(relief="flat", cursor="hand2", borderwidth=0)


class FarmTraceApp:
    def __init__(self, config, sensors, scale, leds, camera, batches, gsm, gsync):
        self.config  = config
        self.sensors = sensors
        self.scale   = scale
        self.leds    = leds
        self.camera  = camera
        self.batches = batches
        self.gsm     = gsm
        self.gsync   = gsync

        self.root = tk.Tk()
        self.root.title("🌿 FarmTrace — Digital Trade Passport")
        self.root.configure(bg=C["bg_dark"])
        try:
            self.root.attributes("-fullscreen", True)
        except Exception:
            self.root.geometry("900x600")
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self._active_batch_id = tk.StringVar(value="")
        self._last_photo      = None
        self.leds.startup_sequence()
        self._build_ui()

    def run(self):
        self._poll_sensors()
        self.root.mainloop()

    # ── TOP HEADER ────────────────────────────────────────────────────────────
    def _build_ui(self):
        # Header
        hdr = tk.Frame(self.root, bg=C["bg_header"], pady=6)
        hdr.pack(fill="x")
        tk.Label(hdr, text="🌿  F A R M T R A C E",
                 bg=C["bg_header"], fg=C["accent2"],
                 font=FONT_XL).pack(side="left", padx=16)
        tk.Label(hdr, text="Digital Trade Passport System",
                 bg=C["bg_header"], fg=C["text_dim"],
                 font=FONT_S).pack(side="left", padx=4)
        self._time_lbl = tk.Label(hdr, text="", bg=C["bg_header"],
                                   fg=C["accent3"], font=FONT_M)
        self._time_lbl.pack(side="right", padx=16)

        # Live sensor strip
        strip = tk.Frame(self.root, bg=C["bg_mid"], pady=5)
        strip.pack(fill="x")
        self._temp_lbl   = self._sensor_badge(strip, "🌡", "-- °C",   C["accent2"])
        self._hum_lbl    = self._sensor_badge(strip, "💧", "-- %",    C["accent5"])
        self._soil_lbl   = self._sensor_badge(strip, "🌱", "-- %",    C["accent1"])
        self._weight_lbl = self._sensor_badge(strip, "⚖️", "-- kg",   C["accent3"])
        self._active_lbl = tk.Label(strip, text="● No active batch",
                                     bg=C["bg_mid"], fg=C["accent4"], font=FONT_S)
        self._active_lbl.pack(side="right", padx=16)

        # Tab bar (manual, styled)
        tab_bar = tk.Frame(self.root, bg=C["bg_dark"], pady=0)
        tab_bar.pack(fill="x")

        self._pages = {}
        self._tab_btns = {}
        self._content = tk.Frame(self.root, bg=C["bg_dark"])
        self._content.pack(fill="both", expand=True)

        tabs = [
            ("home",    "🏠  Home"),
            ("batch",   "📦  Batches"),
            ("parcel",  "➕  Add Parcel"),
            ("history", "📋  History"),
        ]
        for key, label in tabs:
            btn = tk.Button(tab_bar, text=label, font=FONT_M,
                            bg=C["bg_card"], fg=C["grey"],
                            activebackground=C["accent1"],
                            activeforeground=C["white"],
                            padx=18, pady=8,
                            command=lambda k=key: self._show_page(k),
                            **BTN_OPTS)
            btn.pack(side="left", padx=2, pady=4)
            self._tab_btns[key] = btn
            frame = tk.Frame(self._content, bg=C["bg_dark"])
            self._pages[key] = frame

        self._build_home()
        self._build_batch_tab()
        self._build_parcel_tab()
        self._build_history_tab()
        self._show_page("home")

    def _show_page(self, key):
        for k, f in self._pages.items():
            f.pack_forget()
        self._pages[key].pack(fill="both", expand=True)
        for k, b in self._tab_btns.items():
            b.config(bg=C["bg_card"], fg=C["grey"])
        self._tab_btns[key].config(bg=C["accent1"], fg=C["white"])

    def _sensor_badge(self, parent, icon, default, colour):
        f = tk.Frame(parent, bg=C["bg_mid"])
        f.pack(side="left", padx=10)
        tk.Label(f, text=icon, bg=C["bg_mid"], fg=colour,
                 font=FONT_M).pack(side="left")
        lbl = tk.Label(f, text=default, bg=C["bg_mid"],
                       fg=colour, font=FONT_M)
        lbl.pack(side="left", padx=2)
        return lbl

    # ── HOME ──────────────────────────────────────────────────────────────────
    def _build_home(self):
        f = self._pages["home"]

        # Welcome card
        top = tk.Frame(f, bg=C["bg_card"], pady=14)
        top.pack(fill="x", padx=16, pady=(14, 6))
        tk.Label(top, text="Welcome to FarmTrace 🌍",
                 bg=C["bg_card"], fg=C["white"], font=FONT_L).pack()
        tk.Label(top, text=self.config.get("cooperative_name", ""),
                 bg=C["bg_card"], fg=C["accent2"], font=FONT_M).pack()

        # Action buttons grid
        grid = tk.Frame(f, bg=C["bg_dark"])
        grid.pack(pady=10, padx=16)

        actions = [
            ("📦\nNew Batch",      C["accent1"],  self._open_new_batch,       0, 0),
            ("➕\nAdd Parcel",     C["accent2"],  lambda: self._show_page("parcel"), 0, 1),
            ("🔒\nLock & Passport",C["accent4"],  self._lock_and_generate,    1, 0),
            ("📋\nView History",   C["accent5"],  lambda: self._show_page("history"), 1, 1),
        ]
        for text, colour, cmd, row, col in actions:
            btn = tk.Button(grid, text=text, font=FONT_L,
                            bg=colour, fg=C["white"],
                            activebackground=C["white"],
                            activeforeground=colour,
                            width=16, height=4,
                            command=cmd, **BTN_OPTS)
            btn.grid(row=row, column=col, padx=10, pady=8)

        # Status bar
        status_card = tk.Frame(f, bg=C["bg_card"], pady=8)
        status_card.pack(fill="x", padx=16, pady=8)
        tk.Label(status_card, text="ACTIVE BATCH", bg=C["bg_card"],
                 fg=C["text_dim"], font=FONT_XS).pack()
        self._home_batch_lbl = tk.Label(status_card, text="None selected",
                                         bg=C["bg_card"], fg=C["accent3"], font=FONT_M)
        self._home_batch_lbl.pack()

    # ── BATCHES ───────────────────────────────────────────────────────────────
    def _build_batch_tab(self):
        f = self._pages["batch"]
        tk.Label(f, text="📦  Harvest Batches", bg=C["bg_dark"],
                 fg=C["accent2"], font=FONT_L).pack(pady=10)

        # Listbox with scrollbar
        list_frame = tk.Frame(f, bg=C["bg_dark"])
        list_frame.pack(fill="both", expand=True, padx=16)
        sb = tk.Scrollbar(list_frame)
        sb.pack(side="right", fill="y")
        self._batch_list = tk.Listbox(list_frame, font=FONT_S,
                                       bg=C["bg_card"], fg=C["offwhite"],
                                       selectbackground=C["accent1"],
                                       selectforeground=C["white"],
                                       height=10, width=70,
                                       yscrollcommand=sb.set,
                                       borderwidth=0, highlightthickness=0)
        self._batch_list.pack(side="left", fill="both", expand=True)
        sb.config(command=self._batch_list.yview)

        btn_row = tk.Frame(f, bg=C["bg_dark"])
        btn_row.pack(pady=8)
        self._action_btn(btn_row, "🔄  Refresh",        C["accent2"], self._refresh_batches).pack(side="left", padx=8)
        self._action_btn(btn_row, "✅  Set as Active",   C["accent1"], self._select_active_batch).pack(side="left", padx=8)
        self._refresh_batches()

    def _refresh_batches(self):
        self._batch_list.delete(0, tk.END)
        for b in self.batches.get_all_batches():
            pct = (b["current_kg"] / b["target_kg"] * 100) if b["target_kg"] else 0
            bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
            status_icon = {"open": "🟢", "locked": "🔒", "passport_generated": "📄"}.get(b["status"], "⚪")
            line = f"{status_icon} {b['batch_id']}  |  {b['crop_type'].upper()}  |  {b['current_kg']:.1f}/{b['target_kg']:.1f}kg  [{bar}] {pct:.0f}%"
            self._batch_list.insert(tk.END, line)

    def _select_active_batch(self):
        sel = self._batch_list.curselection()
        if not sel:
            messagebox.showwarning("Select", "Click a batch first."); return
        line = self._batch_list.get(sel[0])
        # extract batch_id (second token after status icon)
        parts = line.split("|")
        bid = parts[0].split()[-1].strip()
        self._active_batch_id.set(bid)
        self._active_lbl.config(text=f"● Active: {bid}")
        self._home_batch_lbl.config(text=bid)
        messagebox.showinfo("✅ Active Batch", f"Active batch set to:\n{bid}")

    # ── ADD PARCEL ────────────────────────────────────────────────────────────
    def _build_parcel_tab(self):
        f = self._pages["parcel"]
        tk.Label(f, text="➕  Add Farmer Parcel", bg=C["bg_dark"],
                 fg=C["accent2"], font=FONT_L).pack(pady=10)

        # Form card
        card = tk.Frame(f, bg=C["bg_card"], pady=16, padx=20)
        card.pack(padx=20, pady=4, fill="x")

        self._parcel_vars = {}
        self._location_name = tk.StringVar(value="")
        fields = [
            ("👤  Farmer Name",          "farmer_name"),
            ("🪪  Farmer ID (optional)", "farmer_id"),
        ]
        for i, (label, key) in enumerate(fields):
            tk.Label(card, text=label, bg=C["bg_card"], fg=C["grey"],
                     font=FONT_M, anchor="w", width=26).grid(row=i, column=0, pady=6, sticky="w")
            var = tk.StringVar()
            entry = tk.Entry(card, textvariable=var, font=FONT_M,
                             bg=C["bg_mid"], fg=C["white"],
                             insertbackground=C["white"],
                             relief="flat", width=26)
            entry.grid(row=i, column=1, pady=6, padx=10)
            self._parcel_vars[key] = var

        # Location row
        tk.Label(card, text="📍  Farm Area / Village", bg=C["bg_card"],
                 fg=C["accent5"], font=FONT_M, anchor="w", width=26).grid(row=2, column=0, pady=6, sticky="w")
        self._location_entry_var = tk.StringVar()
        tk.Entry(card, textvariable=self._location_entry_var, font=FONT_M,
                 bg=C["bg_mid"], fg=C["accent5"],
                 insertbackground=C["white"],
                 relief="flat", width=26).grid(row=2, column=1, pady=6, padx=10)

        # Location result display
        self._location_result = tk.Label(card, text="e.g. Mazowe, Harare, Mutoko...",
                                          bg=C["bg_card"], fg=C["text_dim"], font=FONT_XS)
        self._location_result.grid(row=3, column=0, columnspan=2, pady=2)

        # Weight row
        tk.Label(card, text="⚖️  Weight (kg)", bg=C["bg_card"],
                 fg=C["accent3"], font=FONT_M, anchor="w", width=26).grid(row=4, column=0, pady=6, sticky="w")
        self._weight_var = tk.StringVar(value="0.000")
        tk.Entry(card, textvariable=self._weight_var, font=FONT_M,
                 bg=C["bg_mid"], fg=C["accent3"],
                 insertbackground=C["white"],
                 relief="flat", width=26).grid(row=4, column=1, pady=6, padx=10)

        # Buttons
        btn_row = tk.Frame(f, bg=C["bg_dark"])
        btn_row.pack(pady=10)
        self._action_btn(btn_row, "📍  Lookup Location", C["accent5"], self._lookup_location).pack(side="left", padx=6)
        self._action_btn(btn_row, "⚖️  Read Scale",      C["accent3"], self._read_scale_to_form).pack(side="left", padx=6)
        self._action_btn(btn_row, "📸  Capture Photo",   C["accent5"], self._capture_photo).pack(side="left", padx=6)
        self._action_btn(btn_row, "✅  Save Parcel",     C["accent1"], self._save_parcel).pack(side="left", padx=6)

        self._parcel_status = tk.Label(f, text="", bg=C["bg_dark"],
                                        fg=C["accent2"], font=FONT_M, wraplength=600)
        self._parcel_status.pack(pady=8)

    def _lookup_location(self):
        place = self._location_entry_var.get().strip()
        if not place:
            self._location_result.config(
                text="Type a village, town or area name first", fg=C["accent4"])
            return
        self._location_result.config(text="Looking up...", fg=C["text_dim"])
        self.root.update()
        self.leds.start_activity()
        try:
            from pi5_hub.location_lookup import lookup
            result = lookup(place)
            if result:
                self._location_name.set(result["short_name"])
                self._location_result.config(
                    text=f"✅  {result['short_name']}", fg=C["accent1"])
            else:
                self._location_name.set(place)
                self._location_result.config(
                    text=f"Not found online — saving as typed: {place}",
                    fg=C["accent4"])
        except Exception as e:
            self._location_name.set(place)
            self._location_result.config(
                text=f"Offline — saving as typed: {place}", fg=C["accent4"])
        finally:
            self.leds.stop_activity()

    def _read_scale_to_form(self):
        w = self.scale.get_weight_kg()
        self._weight_var.set(f"{w:.3f}")

    def _capture_photo(self):
        bid = self._active_batch_id.get()
        fname = self._parcel_vars["farmer_name"].get() or "unknown"
        if not bid:
            messagebox.showwarning("No Batch", "Set an active batch first."); return
        self._last_photo = self.camera.capture(bid, fname)
        self._parcel_status.config(text=f"📸  Photo saved: {self._last_photo}",
                                    fg=C["accent5"])

    def _save_parcel(self):
        bid = self._active_batch_id.get()
        if not bid:
            messagebox.showwarning("No Batch", "Set an active batch first."); return
        fname = self._parcel_vars["farmer_name"].get().strip()
        if not fname:
            messagebox.showwarning("Missing", "Enter the farmer's name."); return
        try:
            weight = float(self._weight_var.get())
        except ValueError:
            messagebox.showwarning("Invalid", "Enter a valid weight."); return

        s = self.sensors.get_latest()
        loc_name = self._location_name.get() or self._location_entry_var.get() or None
        self.leds.start_activity()
        try:
            batch = self.batches.add_parcel(
                batch_id=bid, farmer_name=fname,
                farmer_id=self._parcel_vars["farmer_id"].get(),
                weight_kg=weight, lat=s.get("lat"), lon=s.get("lon"),
                location_name=loc_name,
                photo_path=self._last_photo
            )
            self._last_photo = None
            pct = batch["current_kg"] / batch["target_kg"] * 100 if batch["target_kg"] else 0
            bar = "█" * int(pct / 10) + "░" * (10 - int(pct / 10))
            self._parcel_status.config(
                text=f"✅  Parcel saved!  [{bar}] {pct:.0f}%  ({batch['current_kg']:.1f}/{batch['target_kg']:.1f} kg)",
                fg=C["accent1"])
            # Clear form
            for v in self._parcel_vars.values(): v.set("")
            self._weight_var.set("0.000")
            self._location_entry_var.set("")
            self._location_name.set("")
            self._location_result.config(text="e.g. Mazowe, Harare, Mutoko...", fg=C["text_dim"])
            self.leds.stop_activity()
            if batch["status"] == "locked":
                messagebox.showinfo("🔒 Auto-Locked",
                                    f"Batch {bid} reached target weight!\nReady to generate passport.")
        except Exception as e:
            self.leds.stop_activity()
            messagebox.showerror("Error", str(e))

    # ── HISTORY ───────────────────────────────────────────────────────────────
    def _build_history_tab(self):
        f = self._pages["history"]
        tk.Label(f, text="📋  Passport History", bg=C["bg_dark"],
                 fg=C["accent2"], font=FONT_L).pack(pady=10)

        list_frame = tk.Frame(f, bg=C["bg_dark"])
        list_frame.pack(fill="both", expand=True, padx=16)
        sb = tk.Scrollbar(list_frame)
        sb.pack(side="right", fill="y")
        self._hist_list = tk.Listbox(list_frame, font=FONT_S,
                                      bg=C["bg_card"], fg=C["offwhite"],
                                      selectbackground=C["accent1"],
                                      height=12, width=75,
                                      yscrollcommand=sb.set,
                                      borderwidth=0, highlightthickness=0)
        self._hist_list.pack(side="left", fill="both", expand=True)
        sb.config(command=self._hist_list.yview)
        self._action_btn(f, "🔄  Refresh", C["accent2"], self._refresh_history).pack(pady=8)
        self._refresh_history()

    def _refresh_history(self):
        self._hist_list.delete(0, tk.END)
        for b in self.batches.get_all_batches():
            if b.get("passport_path"):
                line = (f"📄  {b['batch_id']}  |  {b['crop_type'].upper()}  |  "
                        f"{b['current_kg']:.1f} kg  |  {b['status'].upper()}")
                self._hist_list.insert(tk.END, line)

    # ── NEW BATCH DIALOG ──────────────────────────────────────────────────────
    def _open_new_batch(self):
        win = tk.Toplevel(self.root)
        win.title("📦 New Batch")
        win.configure(bg=C["bg_dark"])
        win.geometry("520x400")

        tk.Label(win, text="📦  Create New Batch", bg=C["bg_dark"],
                 fg=C["accent2"], font=FONT_L).pack(pady=14)

        card = tk.Frame(win, bg=C["bg_card"], pady=16, padx=20)
        card.pack(padx=20, fill="x")

        fields = [
            ("🌾  Crop Type", "crop", "avocado"),
            ("🏢  Buyer Name", "buyer_name", ""),
            ("📧  Buyer Email", "buyer_email", ""),
            ("⚖️  Target Weight (kg)", "target_kg",
             str(self.config["batch"].get("target_weight_kg", 100))),
        ]
        vars_ = {}
        for i, (lbl, key, default) in enumerate(fields):
            tk.Label(card, text=lbl, bg=C["bg_card"], fg=C["grey"],
                     font=FONT_M, anchor="w", width=24).grid(row=i, column=0, pady=6, sticky="w")
            v = tk.StringVar(value=default)
            tk.Entry(card, textvariable=v, font=FONT_M,
                     bg=C["bg_mid"], fg=C["white"],
                     insertbackground=C["white"],
                     relief="flat", width=24).grid(row=i, column=1, pady=6, padx=10)
            vars_[key] = v

        def _create():
            try:
                batch = self.batches.create_batch(
                    crop_type=vars_["crop"].get(),
                    buyer_name=vars_["buyer_name"].get(),
                    buyer_email=vars_["buyer_email"].get(),
                    target_kg=float(vars_["target_kg"].get())
                )
                self._active_batch_id.set(batch["batch_id"])
                self._active_lbl.config(text=f"● Active: {batch['batch_id']}")
                self._home_batch_lbl.config(text=batch["batch_id"])
                self.leds.reset_ready()
                self._refresh_batches()
                win.destroy()
                messagebox.showinfo("✅ Batch Created",
                                    f"Batch ID:\n{batch['batch_id']}\n\nNow add farmer parcels!")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        self._action_btn(win, "✅  Create Batch", C["accent1"], _create).pack(pady=16)

    # ── LOCK & GENERATE ───────────────────────────────────────────────────────
    def _lock_and_generate(self):
        bid = self._active_batch_id.get()
        if not bid:
            messagebox.showwarning("No Batch", "Set an active batch first."); return
        if not messagebox.askyesno("🔒 Confirm",
                                    f"Lock batch:\n{bid}\n\nAnd generate passport PDF?"):
            return

        def _run():
            try:
                from passport.passport_generator import generate
                self.batches.lock_batch(bid)
                path = generate(bid, self.config)
                self.leds.signal_ready()
                self._refresh_history()
                self.root.after(0, lambda: messagebox.showinfo(
                    "Passport Ready!",
                    f"Passport generated successfully!\n\n"
                    f"Saved to:\n{path}\n\n"
                    f"Open the data/passports/ folder to view it."))
                batch   = self.batches.get_batch(bid)
                parcels = self.batches.get_parcels(bid)
                self.gsync.queue_batch(batch, parcels, path)

                # Send email to buyer
                from pi5_hub.email_sender import send_passport_email
                email_sent = send_passport_email(self.config, batch, path, parcels)
                if email_sent:
                    buyer_addr = batch.get('buyer_email','buyer')
                    self.root.after(0, lambda: messagebox.showinfo(
                        "Email Sent!", f"Passport emailed to:\n{buyer_addr}"))
            except Exception as e:
                log.exception("Passport generation failed")
                self.leds.signal_error()
                err_msg = str(e)
                self.root.after(0, lambda: messagebox.showerror("Error", err_msg))

        threading.Thread(target=_run, daemon=True).start()

    # ── HELPERS ───────────────────────────────────────────────────────────────
    def _action_btn(self, parent, text, colour, cmd):
        return tk.Button(parent, text=text, command=cmd,
                         font=FONT_M, bg=colour, fg=C["white"],
                         activebackground=C["white"], activeforeground=colour,
                         padx=14, pady=10, width=18, **BTN_OPTS)

    def _poll_sensors(self):
        s = self.sensors.get_latest()
        w = self.scale.get_weight_kg()
        if s.get("temp_c"):
            self._temp_lbl.config(text=f"{s['temp_c']:.1f} °C")
        if s.get("humidity"):
            self._hum_lbl.config(text=f"{s['humidity']:.1f} %")
        if s.get("soil_pct"):
            self._soil_lbl.config(text=f"{s['soil_pct']:.1f} %")
        self._weight_lbl.config(text=f"{w:.3f} kg")
        self._time_lbl.config(
            text=datetime.utcnow().strftime("%d %b %Y  %H:%M:%S"))
        self.root.after(5000, self._poll_sensors)
