# sqlite_main_app.py
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import os
import threading
from pathlib import Path
from datetime import datetime, timedelta
import atexit
import random   
from matplotlib.pyplot import bar
# Import our custom modules
import db
import ai_client
from db import get_database, get_or_create_pet, save_chat_message
from db import init_database, close_database

db_instance = init_database()
atexit.register(close_database)



class PetCareApp:
    def __init__(self, root):
        # --- WINDOW SETUP ---
        self.root = root
        self.decay_job = None
        self.current_pet_id = None
        self.setup_database() 

        import customtkinter as ctk
        import tkinter as tk

        # CustomTkinter appearance
        ctk.set_appearance_mode("light")  # or "dark"
        ctk.set_default_color_theme("blue")

        self.root.title("PetPal Game")
        self.root.geometry("590x750")  # consistent window size
        self.root.resizable(False, False)
        # --- MAIN CONTAINER ---
        self.content_frame = ctk.CTkFrame(self.root, fg_color="white")
        self.content_frame.pack(fill="both", expand=True)

        # --- CORE DATA ---
        self.pet_data = {"id": 1, "name": "Buddy"}
        self.pet_status = {
            "health": 100,
            "hunger": 100,
            "happiness": 100,
            "energy": 100,
            "cleanliness": 100,
            "level": 1
        }
        self.status_bars = {}

        self.idle_after_id = None  # store after() ID for cancelling
        self.idle_delay = 5000     # 5000 ms = 5 seconds

        # --- SCENE HANDLING ---
        self.current_scene = "happy"
        self.scenes = {}  # loaded in load_assets()

        # --- ALL APP PAGES / FRAMES ---
        self.frames = {}
        self.frames["login"] = ctk.CTkFrame(self.content_frame)
        self.frames["welcome"] = ctk.CTkFrame(self.content_frame)
        self.frames["gameplay"] = ctk.CTkFrame(self.content_frame)
        self.frames["chat"] = ctk.CTkFrame(self.content_frame)
        self.frames["appointments"] = ctk.CTkFrame(self.content_frame)
        self.frames["medical"] = ctk.CTkFrame(self.content_frame)
        self.frames["achievements"] = ctk.CTkFrame(self.content_frame)

        # --- LOAD ASSETS FIRST ---
        try:
            self.load_assets()
        except Exception as e:
            print("⚠️ Asset loading error:", e)

        # --- INITIALIZE ALL SCREENS ---
        try:
            self.setup_login_frame()
        except Exception as e:
            print("⚠️ Could not start login:", e)

        try:
            self.setup_welcome_frame()
            self.setup_gameplay_frame()
            self.setup_chat_frame()
            self.setup_appointments_frame()
            self.setup_medical_frame()
            self.setup_achievements_frame()
        except Exception as e:
            print("⚠️ Setup frame error:", e)

        for frame in self.frames.values():
            frame.pack_forget()

        # --- SHOW FIRST PAGE ---
        self.show_frame("login")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def setup_window(self):
        import platform
        self.root.title("PetPal AI")

        # --- Size lock ---
        width, height = 560, 720  # slightly smaller than before
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False, False)
        self.root.minsize(width, height)
        self.root.maxsize(width, height)

        # --- Force disable maximize (Windows specific) ---
        if platform.system() == "Windows":
            self.root.attributes('-toolwindow', True)  # removes maximize button
            self.root.overrideredirect(False)          # keep title bar visible
            self.root.update_idletasks()

    def load_assets(self):
        moods = ["eating", "happy", "playing", "showering", "sick", "sleeping", "sad"]
        for mood in moods:
            path = os.path.join("assets", f"{mood}.png")
            if os.path.exists(path):
                img = Image.open(path).resize((600, 750))
                self.scenes[mood] = ImageTk.PhotoImage(img)
            else:
                # fallback placeholder so self.scenes["happy"] always exists
                self.scenes[mood] = ImageTk.PhotoImage(Image.new("RGB", (600, 750), "grey"))

        # Load action button images
        self.action_images = {}
        actions_files = {
            "Feed": "food.png",
            "Play": "play.png",
            "Clean": "shower.png",
            "Sleep": "sleep.png"
        }

        for action, file in actions_files.items():
            img_path = os.path.join("assets", file)
            if os.path.exists(img_path):
                img = Image.open(img_path).resize((60, 60))  # adjust size to your preference
                self.action_images[action] = ImageTk.PhotoImage(img)
            else:
                # fallback: empty image if missing
                self.action_images[action] = ImageTk.PhotoImage(Image.new("RGBA", (60, 60), (200, 200, 200, 0)))

# ---------------- Frame Management ----------------
    def setup_login_frame(self):
        frame = self.frames["login"]

        # --- CLEAR PREVIOUS WIDGETS ---
        for widget in frame.winfo_children():
            widget.destroy()

        import os
        import tkinter as tk
        from PIL import Image, ImageTk
        from customtkinter import CTkImage

        base_path = os.path.dirname(os.path.abspath(__file__))

        # === BACKGROUND IMAGE ===
        bg_path = os.path.join(base_path, "assets", "login_bg.png")
        if os.path.exists(bg_path):
            bg_image = Image.open(bg_path)
            window_width, window_height = 600, 759
            img_width, img_height = bg_image.size

            scale = min(window_width / img_width, window_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            bg_image = bg_image.resize((new_width, new_height), Image.LANCZOS)

            bg_photo = ImageTk.PhotoImage(bg_image)
            self.login_bg_photo = bg_photo

            bg_label = tk.Label(frame, image=bg_photo)
            bg_label.place(relx=0.5, rely=0.5, anchor="center")

        # === COLORS & PLACEMENT CONSTANTS ===
        CENTER_X = 0.5
        START_Y = 0.40 # slightly higher to fit extra spacing
        Y_STEP = 0.09   # increased spacing
        TEXT_COLOR = "#2E3A59"
        ENTRY_BG = "#F2F5F9"
        LINE_COLOR = "#FFA642"

        # === USERNAME ===
        ctk.CTkLabel(frame, text="Username", 
                     text_color=TEXT_COLOR,
                    font=("Poppins", 14, "bold"), fg_color="#FFFFFF").place(relx=0.5, rely=0.44, anchor="s")

        self.username_entry = ctk.CTkEntry(
            frame,
            width=290,
            placeholder_text="Enter your username",
            corner_radius=6,
            fg_color=ENTRY_BG,
            border_width=0,
            text_color=TEXT_COLOR
        )
        self.username_entry.place(relx=CENTER_X, rely=START_Y + Y_STEP * 0.55, anchor="center")
        ctk.CTkFrame(frame, width=290, height=2, fg_color=LINE_COLOR).place(
            relx=CENTER_X, rely=START_Y + Y_STEP * 0.8, anchor="center")

        # === PET NAME ===
        ctk.CTkLabel(frame, text="Pet Name", text_color=TEXT_COLOR,
                    font=("Poppins", 14, "bold"),fg_color="#FFFFFF").place(relx=0.5, rely=0.5, anchor="s")

        self.petname_entry = ctk.CTkEntry(
            frame,
            width=290,
            placeholder_text="(Optional)",
            corner_radius=6,
            fg_color=ENTRY_BG,
            border_width=0,
            text_color=TEXT_COLOR
        )
        self.petname_entry.place(relx=CENTER_X, rely=START_Y + Y_STEP * 1.35, anchor="center")
        ctk.CTkFrame(frame, width=290, height=2, fg_color=LINE_COLOR).place(
            relx=CENTER_X, rely=START_Y + Y_STEP * 1.6, anchor="center")

        # === PASSWORD ===
        ctk.CTkLabel(frame, text="Password", text_color=TEXT_COLOR,
                    font=("Poppins", 14, "bold"), fg_color="#FFFFFF").place(relx=0.5, rely=0.59, anchor="s")

        self.password_entry = ctk.CTkEntry(
            frame,
            width=290,
            placeholder_text="Enter password",
            corner_radius=6,
            fg_color=ENTRY_BG,
            border_width=0,
            show="*",
            text_color=TEXT_COLOR
        )
        self.password_entry.place(relx=CENTER_X, rely=START_Y + Y_STEP * 2.35, anchor="center")
        ctk.CTkFrame(frame, width=290, height=2, fg_color=LINE_COLOR).place(
            relx=CENTER_X, rely=START_Y + Y_STEP * 2.6, anchor="center")

        # === PLAY BUTTON ===
        play_btn = ctk.CTkButton(
            frame,
            text="PLAY!",
            width=200,
            height=40,
            fg_color="#FF8C42",
            hover_color="#FFA466",
            corner_radius=15,
            command=self.handle_login
        )
        play_btn.place(relx=CENTER_X, rely=START_Y + Y_STEP * 3.4, anchor="center")

        # === PET SELECTION LABEL ===
        ctk.CTkLabel(frame, text="SELECT A DOG", font=("Poppins", 16, "bold"),
                    text_color=TEXT_COLOR).place(relx=0.5, rely=0.76, anchor="center")

        # === DOG AVATARS ===
        self.selected_pet = None
        avatar_names = ["d1.png", "d2.png", "d3.png"]
        self.pet_avatar_buttons = []
        self.pet_avatar_photos = []
        avatars_folder = os.path.join(base_path, "assets")

        start_x = 120
        spacing = 180
        y_pos_rel = 0.86

        def highlight_selected(index):
            """Visually highlight the selected pet."""
            for j, btn in enumerate(self.pet_avatar_buttons):
                if j == index:
                    btn.configure(fg_color="#FFD580", hover_color="#FFE0A3", border_width=3, border_color="#FF8C42")
                else:
                    btn.configure(fg_color="#FFF2D0", hover_color="#FFE0A3", border_width=0)

        for i, file_name in enumerate(avatar_names):
            avatar_path = os.path.join(avatars_folder, file_name)
            if not os.path.exists(avatar_path):
                print(f"⚠️ Avatar not found: {avatar_path}")
                continue

            img = Image.open(avatar_path).resize((85, 85), Image.LANCZOS)
            ctk_img = CTkImage(img, size=(85, 85))
            self.pet_avatar_photos.append(ctk_img)

            def on_select(idx=i):
                self.select_pet(idx)
                highlight_selected(idx)

            btn = ctk.CTkButton(
                frame,
                image=ctk_img,
                text="",
                width=60,
                height=60,
                corner_radius=42,
                fg_color="#FFF2D0",
                hover_color="#FFE0A3",
                border_width=0,
                command=on_select
            )
            btn.place(x=start_x + spacing * i, rely=y_pos_rel, anchor="center")
            self.pet_avatar_buttons.append(btn)

    def setup_welcome_frame(self):
        frame = self.frames["welcome"]
        for widget in frame.winfo_children():
            widget.destroy()

        import os
        from PIL import Image, ImageTk

        base_path = os.path.dirname(os.path.abspath(__file__))
        bg_path = os.path.join(base_path, "assets", "welcome.png")

        if os.path.exists(bg_path):
            bg_image = Image.open(bg_path).resize((600, 750))
            self.welcome_bg = ImageTk.PhotoImage(bg_image)
            bg_label = tk.Label(frame, image=self.welcome_bg)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # animated text
        self.welcome_label = ctk.CTkLabel(
            frame,
            text="",
            font=("Poppins", 26, "bold"),
            text_color="#0B0B0B",  # soft white, visible on dark bg
            justify="center",
            wraplength=500,
            fg_color="transparent"
        )
        self.welcome_label.place(relx=0.5, rely=0.4, anchor="center")

        # start button with subtle shadow color
        self.start_button = ctk.CTkButton(
            frame,
            text="🎮 Start Game",
            fg_color="#FF8C42",
            hover_color="#FFA861",
            width=200,
            height=45,
            corner_radius=12,
            font=("Poppins", 15, "bold"),
            command=self.fade_out_to_gameplay
        )
        self.start_button.place(relx=0.5, rely=0.7, anchor="center")

        # make everything initially invisible for fade-in
        frame.attributes = {"alpha": 0.0}

    def setup_gameplay_frame(self):
        frame = self.frames["gameplay"]
        # Pass the gameplay frame as parent to widgets
        self.create_ui(frame)  # make sure create_action_buttons accepts parent_frame if needed
        print("Gameplay frame setup called")

    def setup_chat_frame(self):
        import customtkinter as ctk
        import tkinter as tk

        frame = self.frames["chat"]
        for widget in frame.winfo_children():
            widget.destroy()

        # Title
        title = ctk.CTkLabel(frame, text="🐾 Chat with your Pet", font=("Poppins", 22, "bold"))
        title.pack(pady=(20, 10))

        # === Scrollable Canvas ===
        self.chat_canvas = tk.Canvas(frame, bg="#C1DFF0", highlightthickness=0, height=550)  # height
        self.chat_canvas.pack(side="top", fill="both", expand=True, padx=20, pady=(0, 5))  # button padding

        scrollbar = ctk.CTkScrollbar(frame, command=self.chat_canvas.yview)
        scrollbar.pack(side="right", fill="y")

        self.chat_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.chat_canvas.yview)
        
        # Inner frame inside canvas
        self.chat_frame_inner = tk.Frame(self.chat_canvas, bg="#C1DFF0")
        self.chat_window = self.chat_canvas.create_window((0, 0), window=self.chat_frame_inner, anchor="nw")

        # Update scroll region when content changes
        def on_frame_configure(event):
            self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))

        self.chat_frame_inner.bind("<Configure>", on_frame_configure)

        def _on_mousewheel(event):
            self.chat_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            self.chat_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # === Entry + Send button ===
        entry_frame = ctk.CTkFrame(frame, fg_color="transparent")
        entry_frame.pack(fill="x", pady=(10,20))#down push  with more botto padding

        self.chat_entry = ctk.CTkEntry(
            entry_frame,
            placeholder_text="Type your message...",
            height=40,
            corner_radius=10,
            text_color="#4A4A4A",
            fg_color="#FFFFFF"
        )
        self.chat_entry.pack(side="left", padx=(20, 10), fill="x", expand=True)
        self.chat_entry.bind("<Return>", lambda e: self.send_chat_message())

        send_btn = ctk.CTkButton(
            entry_frame,
            text="Send",
            width=80,
            height=40,
            fg_color="#FF9933",
            hover_color="#FFA642",
            corner_radius=10,
            command=self.send_chat_message
        )
        send_btn.pack(side="right", padx=(0, 20))

        # Show a welcome message
        self._add_message_bubble("pet", "Woof! I'm PetPal — ready to chat 🐾")

    def setup_appointments_frame(self):
        frame = self.frames["appointments"]

        # === HEADER ===
        header = ctk.CTkLabel(
            frame,
            text="🐾 Pet Appointments",
            font=("Poppins", 22, "bold"),
            text_color="#333"
        )
        header.pack(pady=(20, 10))

        # === AVAILABLE APPOINTMENTS ===
        ctk.CTkLabel(
            frame,
            text="Available Appointments:",
            font=("Poppins", 16, "bold"),
            text_color="#444"
        ).pack(pady=(5, 5))

        self.available_appts = [
            "🩺 Vet Checkup",
            "💉 Vaccination",
            "✂️ Grooming",
            "🦷 Dental Cleaning",
            "🏃 Physiotherapy",
            "🍖 Diet Consultation"
        ]

        self.selected_appt = ctk.StringVar(value=self.available_appts[0])

        self.appt_menu = ctk.CTkOptionMenu(
            frame,
            values=self.available_appts,
            variable=self.selected_appt,
            fg_color="#FF8C42",
            button_color="#FFA45B",
            button_hover_color="#FFB066",
            text_color="white",
            dropdown_hover_color="#FFD8A3",
            width=300
        )
        self.appt_menu.pack(pady=(0, 15))

        # === BUTTONS ===
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=5)

        add_btn = ctk.CTkButton(
            btn_frame,
            text="Book Appointment",
            width=160,
            height=35,
            fg_color="#4CAF50",
            hover_color="#66BB6A",
            command=self.book_appointment
        )
        add_btn.grid(row=0, column=0, padx=10)

        del_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel Last",
            width=120,
            height=35,
            fg_color="#FF5252",
            hover_color="#FF6B6B",
            command=self.cancel_last_appointment
        )
        del_btn.grid(row=0, column=1, padx=10)

        done_btn = ctk.CTkButton(
            btn_frame,
            text="Mark as Completed",
            width=160,
            height=35,
            fg_color="#2196F3",
            hover_color="#64B5F6",
            command=self.mark_appointment_done
        )
        done_btn.grid(row=0, column=2, padx=10)

        # === YOUR UPCOMING APPOINTMENTS ===
        ctk.CTkLabel(
            frame,
            text="Your Upcoming Appointments:",
            font=("Poppins", 16, "bold"),
            text_color="#444"
        ).pack(pady=(15, 5))

        self.upcoming_box = ctk.CTkTextbox(
            frame,
            width=500,
            height=250,
            fg_color="#F9F9F9",
            text_color="#333",
            font=("Poppins", 14),
            corner_radius=10
        )
        self.upcoming_box.pack(pady=5)
        self.upcoming_box.insert("end", "No appointments booked yet.\n")
        self.upcoming_box.configure(state="disabled")

    def setup_medical_frame(self):
        frame = self.frames["medical"]

        title = ctk.CTkLabel(
            frame,
            text="🏥 Medical Records",
            font=("Poppins", 20, "bold"),
            text_color="#333"
        )
        title.pack(pady=(20, 10))

        # === Treeview with scrollbar ===
        columns = ("Visit Date", "Type", "Diagnosis", "Treatment", "Medications", "Vet", "Follow-Up", "Notes")

        tree_frame = ctk.CTkFrame(frame, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.medical_tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=12)

        for col in columns:
            self.medical_tree.heading(col, text=col)
            self.medical_tree.column(col, anchor="center", width=120)

        yscroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.medical_tree.yview)
        self.medical_tree.configure(yscrollcommand=yscroll.set)

        self.medical_tree.pack(side="left", fill="both", expand=True)
        yscroll.pack(side="right", fill="y")

        # === Refresh button ===
        refresh_btn = ctk.CTkButton(
            frame,
            text="🔄 Refresh Records",
            width=160,
            height=35,
            fg_color="#4CAF50",
            hover_color="#45A049",
            command=self.load_medical_records
        )
        refresh_btn.pack(pady=10)
        
        self.load_medical_records()

    def setup_achievements_frame(self):
        frame = self.frames["achievements"]

        # === TITLE ===
        title = ctk.CTkLabel(
            frame,
            text="🏆 Achievements",
            font=("Poppins", 24, "bold"),
            text_color="#FFD700",
        )
        title.pack(pady=(20, 10))

        # === SCROLLABLE CONTAINER ===
        scroll = ctk.CTkScrollableFrame(
            frame,
            fg_color="transparent",
            width=600,
            height=400,
        )
        scroll.pack(fill="both", expand=True, padx=30, pady=10)

        # === STATIC ACHIEVEMENTS ===
        achievements = [
            ("🥇", "First Meal", "Fed your pet for the first time"),
            ("🧼", "Clean Pup", "Gave your pet a refreshing bath"),
            ("🎾", "Happy Walk", "Played fetch or walked your pet"),
            ("💤", "Sleepy Time", "Let your pet get a full nap"),
            ("🩺", "Healthy Buddy", "Visited the vet"),
            ("🎉", "Perfect Care", "Completed all daily tasks"),
        ]

        for icon, title_text, desc in achievements:
            box = ctk.CTkFrame(
                scroll,
                fg_color="#2B2B2B",
                corner_radius=15,
            )
            box.pack(fill="x", padx=10, pady=10)

            # === Icon + Text ===
            icon_label = ctk.CTkLabel(
                box,
                text=icon,
                font=("Arial", 30),
                text_color="#FFD700",
                width=50,
            )
            icon_label.pack(side="left", padx=15, pady=10)

            text_frame = ctk.CTkFrame(box, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, pady=10)

            title_label = ctk.CTkLabel(
                text_frame,
                text=title_text,
                font=("Poppins", 16, "bold"),
                text_color="#FFFFFF",
                anchor="w",
            )
            title_label.pack(fill="x")

            desc_label = ctk.CTkLabel(
                text_frame,
                text=desc,
                font=("Poppins", 12),
                text_color="#BBBBBB",
                anchor="w",
            )
            desc_label.pack(fill="x")

    # Frame management and navigation methods
    def show_frame(self, frame_name):
        # Hide all frames
        for f in self.frames.values():
            f.pack_forget()

        # Show the selected frame
        self.frames[frame_name].pack(fill="both", expand=True)

        # ✅ Add nav button for all except login and welcome
        if frame_name not in ("login", "welcome"):
            self.setup_nav_button_for_frame(self.frames[frame_name])
        else:
            # Remove nav button if it exists (for login & welcome)
            if hasattr(self, "nav_button") and self.nav_button.winfo_exists():
                self.nav_button.destroy()

        # ✅ Pause the decay when not in gameplay
        if frame_name != "gameplay":
            if hasattr(self, "decay_job") and self.decay_job:
                self.root.after_cancel(self.decay_job)
                self.decay_job = None
        else:
            # ✅ Resume or start decay when gameplay is active
            self.start_status_decay()

    def setup_nav_button_for_frame(self, frame):
            # Destroy old button if exists
            if hasattr(self, "nav_button") and self.nav_button.winfo_exists():
                self.nav_button.destroy()

            # Determine options based on frame
            if frame == self.frames["gameplay"]:
                values = ["Play Area", "Chat with me!", "Appointments", "Medical Records", "Achievements", "Logout"]
            else:
                values = ["Play Area", "Chat with me!", "Appointments", "Medical Records", "Achievements"]

            self.nav_button = ctk.CTkOptionMenu(
                frame,
                values=values,
                width=40,                # small icon-like button
                height=30,
                corner_radius=20,
                fg_color="#1365BC",       # main button color from setup_nav_button()
                dropdown_fg_color="#5192D7",  # dropdown background
                button_color="#1365BC",       # button color
                button_hover_color="#5192D7", # hover effect
                text_color="black",
                dropdown_text_color="black",
                font=("Arial", 14, "bold"),
                command=self.home_dropdown_action
            )
            self.nav_button.set("🏠")
            self.nav_button.pack(side="top", anchor="ne", padx=10, pady=10)

    def home_dropdown_action(self, selection):
            mapping = {
                "Play Area": "gameplay",
                "Chat with me!": "chat",
                "Appointments": "appointments",
                "Medical Records": "medical",
                "Achievements": "achievements",
                "Logout": "login"
            }
            frame = mapping.get(selection, "gameplay")
            self.show_frame(frame)

    # === login/pet ===
    def select_pet(self, idx):
        """Highlight selected pet and store selection"""
        self.selected_pet = idx
        for i, btn in enumerate(self.pet_avatar_buttons):
            if i == idx:
                btn.configure(fg_color="#FF8C42")  # highlight selected
            else:
                btn.configure(fg_color="#F2E5C6")

    def handle_login(self):
        import hashlib

        username = self.username_entry.get().strip()
        petname = self.petname_entry.get().strip()
        password = self.password_entry.get().strip()
        selected_pet_index = getattr(self, "selected_pet", None)

        if not username:
            ctk.CTkLabel(self.frames["login"], text="⚠️ Enter username!", text_color="red").place(relx=0.5, rely=0.5, anchor="center")
            return
        if not self.password_entry.get().strip():
            ctk.CTkLabel(self.frames["login"], text="⚠️ Enter password!", text_color="red").place(relx=0.5, rely=0.55, anchor="center")
            return
        if selected_pet_index is None:
            ctk.CTkLabel(self.frames["login"], text="⚠️ Select a dog!", text_color="red").place(relx=0.5, rely=0.6, anchor="center")
            return

        # Default pet name if left empty
        if not petname:
            petname = "Buddy"


        # Save/update pet in database
        db = get_database()

        # hash the password
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        user = db.execute_query("SELECT * FROM users WHERE username = ?", (username,), fetch=True)
        password = self.password_entry.get().strip()

        if user:
            stored_hash = user[0]["password_hash"]
            user_id = user[0]["id"]

            # compute entered password's hash
            entered_hash = hashlib.sha256(password.encode()).hexdigest()

            # compare hashes
            if stored_hash != entered_hash:
                ctk.CTkLabel(
                    self.frames["login"], 
                    text="❌ Incorrect password!", 
                    text_color="red"
                ).place(relx=0.5, rely=0.5, anchor="center")
                return  # stop here if password doesn't match

            # password correct → update last login
            db.execute_query("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))

        else:
            # new user → create with hashed password
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
            user_id = db.execute_query(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                (username, hashed_pw)
            )
            
       
        # Save or create pet
        pet = db.execute_query("SELECT * FROM pet WHERE user_id = ?", (user_id,), fetch=True)
        if pet:
            pet_id = pet[0]["id"]
            db.execute_query("UPDATE pet SET name = ? WHERE id = ?", (petname, pet_id))
        else:
            pet_id = db.execute_query(
                """INSERT INTO pet (user_id, name, species, breed, mood, health, hunger, happiness, energy, cleanliness)
                VALUES (?, ?, 'dog', 'mixed', 'happy', 100, 100, 100, 100, 100)""",
                (user_id, petname)
            )

        self.pet_data["id"] = pet_id
        self.pet_data["name"] = petname
        self.current_pet_id = pet_id  
        self.current_username = username
        self.current_pet_name = petname

        self.setup_welcome_frame()
        self.update_welcome_message()

        # Now show welcome frame (instead of directly gameplay)
        self.show_frame("welcome")
        self.update_pet_name_display()

    def update_pet_name_display(self):
        """Refresh the pet name label in the gameplay UI."""
        if hasattr(self, "pet_name_label"):
            pet_name = self.pet_data.get("name", "Buddy")
            self.pet_name_label.configure(text=f"🐶 {pet_name}")

    def update_welcome_message(self):
        username = getattr(self, "current_username", "Player")
        pet_name = getattr(self, "current_pet_name", "Buddy")

        self.welcome_label.configure(text=f"👋 Hey {username}! Let's play with {pet_name}!")
        self.animate_fade_in(self.frames["welcome"], step=0.15)  

    def animate_fade_in(self, target_frame, step=0.15):
        """Gradually fades in the frame contents"""
        alpha = getattr(target_frame, "alpha", 0.0)
        alpha += step
        if alpha >= 1.0:
            alpha = 1.0
        target_frame.alpha = alpha
        target_frame.winfo_toplevel().attributes("-alpha", alpha)
        if alpha < 1.0:
            target_frame.after(20, lambda: self.animate_fade_in(target_frame))

    def fade_out_to_gameplay(self, alpha=0.15):
        """Fades out and then switches to gameplay"""
        alpha -= 0.05
        if alpha <= 0:
            self.root.attributes("-alpha", 1.0)
            self.show_frame("gameplay")
            return
        self.root.attributes("-alpha", alpha)
        self.root.after(20, lambda: self.fade_out_to_gameplay(alpha))
            
    # === Chat System ===
    def _add_message_bubble(self, sender, message):
        """Adds a message bubble to the chat frame."""
        if not hasattr(self, "chat_frame_inner"):
            print("⚠️ chat_frame_inner not found")
            return
        
        bubble_color = "#8DC63F" if sender == "pet" else "#FF9933"
        text_color = "#FFFFFF"
        align = "e" if sender == "user" else "w"
        
        bubble_frame = tk.Frame(self.chat_frame_inner, bg="#C1DFF0")
        bubble_frame.pack(anchor=align, pady=5, padx=10, fill="x")
        
        label = tk.Label(
            bubble_frame,
            text=message,
            bg=bubble_color,
            fg=text_color,
            font=("Poppins", 12),
            wraplength=350,
            justify="left" if sender == "pet" else "right",
            padx=10,
            pady=5
        )
        label.pack(anchor=align, padx=5)

        # === Update scroll region and auto-scroll to bottom ===
        self.chat_frame_inner.update_idletasks()  # recalc size
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        self.chat_canvas.yview_moveto(1.0)  # scroll to bottom
    
    def send_chat_message(self):
            import ai_client

            msg = self.chat_entry.get().strip()
            if not msg:
                return

            self.chat_entry.delete(0, "end")

            # Show user message bubble
            self._add_message_bubble("user", msg)

            try:
                response = ai_client.send_message(msg)
            except Exception as e:
                response = f"(AI Error: {e})"

            # Show pet response bubble
            self._add_message_bubble("pet", response)

    #=====appointmnets helpers=====
    def book_appointment(self):
        new_appt = self.selected_appt.get()
        self.upcoming_box.configure(state="normal")

        current_text = self.upcoming_box.get("1.0", "end-1c").strip()
        if "No appointments" in current_text:
            self.upcoming_box.delete("1.0", "end")

        # Add date automatically
        import datetime
        today = datetime.date.today()
        appt_date = today + datetime.timedelta(days=5)
        self.upcoming_box.insert("end", f"{new_appt} – {appt_date.strftime('%d %b %Y')}\n")

        self.upcoming_box.configure(state="disabled")

    def cancel_last_appointment(self):
        self.upcoming_box.configure(state="normal")
        lines = self.upcoming_box.get("1.0", "end-1c").strip().split("\n")
        if lines and "No appointments" not in lines[0]:
            lines.pop()
            self.upcoming_box.delete("1.0", "end")
            if lines:
                self.upcoming_box.insert("1.0", "\n".join(lines) + "\n")
            else:
                self.upcoming_box.insert("1.0", "No appointments booked yet.\n")
        self.upcoming_box.configure(state="disabled")

    def mark_appointment_done(self):
        self.upcoming_box.configure(state="normal")
        lines = self.upcoming_box.get("1.0", "end-1c").strip().split("\n")

        if not lines or "No appointments" in lines[0]:
            self.upcoming_box.configure(state="disabled")
            return

        # Get the last appointment
        completed_appt = lines.pop()

        # Remove it from upcoming list
        self.upcoming_box.delete("1.0", "end")
        if lines:
            self.upcoming_box.insert("1.0", "\n".join(lines) + "\n")
        else:
            self.upcoming_box.insert("1.0", "No appointments booked yet.\n")

        self.upcoming_box.configure(state="disabled")

        # === STORE IN MEDICAL RECORDS TEMP LIST ===
        if not hasattr(self, "completed_appointments"):
            self.completed_appointments = []

        self.completed_appointments.append(completed_appt)

        # Optional: Confirmation
        ctk.CTkLabel(
            self.frames["appointments"],
            text=f"✅ Completed: {completed_appt}",
            text_color="#4CAF50",
            font=("Poppins", 12)
        ).pack(pady=(5, 0))

        # Add corresponding medical record for the completed appointment
        self.db.execute_query("""
            INSERT INTO medical_records 
            (pet_id, record_type, diagnosis, treatment, medications, veterinarian, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            self.pet_data["id"],
            "Appointment",
            "Routine Checkup",
            "N/A",
            "N/A",
            "Dr. Brown",
            "Completed appointment added from Appointments tab."
        ))

    def load_medical_records(self):
        # Clear old entries
        for row in self.medical_tree.get_children():
            self.medical_tree.delete(row)

        # Fetch records from DB (filter by selected pet if you have one)
        query = """
        SELECT visit_date, record_type, diagnosis, treatment, medications, veterinarian, follow_up_date, notes
        FROM medical_records
        ORDER BY visit_date DESC
        """
        records = self.db.execute_query(query, fetch=True)

        for rec in records:
            # Convert sqlite3.Row → tuple of column values
            self.medical_tree.insert("", "end", values=tuple(rec))
        db = get_database()
        
    def setup_database(self):
        """Ensure medical_records table exists using the shared DatabaseManager."""
        db = get_database()
        db.execute_query("""
            CREATE TABLE IF NOT EXISTS medical_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pet_id INTEGER NOT NULL,
                record_type TEXT NOT NULL,
                diagnosis TEXT,
                treatment TEXT,
                medications TEXT,
                veterinarian TEXT,
                visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                follow_up_date TIMESTAMP,
                notes TEXT,
                attachments TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pet_id) REFERENCES pet (id)
            )
        """)
        # Store this for convenience
        self.db = db

    def on_close(self):
        if hasattr(self, "db_connection"):
            self.db_connection.close()
        self.destroy()


    # === Gameplay UI & Actions ===
    def create_ui(self, parent_frame):
        # === BACKGROUND IMAGE ===
        self.canvas = tk.Label(parent_frame, image=self.scenes[self.current_scene])
        self.canvas.place(x=0, y=0, relwidth=1, relheight=1)

        # STATUS PANEL
       # STATUS PANEL
        self.status_frame = ctk.CTkFrame(parent_frame, fg_color="#E4EAFA", corner_radius=1)
        self.status_frame.place(x=20, y=20)

        # 🐶 Store reference to the pet name label so we can update it later
        self.pet_name_label = ctk.CTkLabel(
            self.status_frame,
            text=f"🐶 {self.pet_data.get('name', 'Buddy')}",
            font=("Poppins", 16, "bold"),
            text_color="#1E1E1E"
        )
        self.pet_name_label.grid(row=0, column=0, columnspan=2, padx=12, pady=(2, 1))

        # Status Bars (Stylish)
        icons = {"health": "❤️", "hunger": "🍗", "happiness": "😺", "energy": "⚡", "cleanliness": "🧼"}
        colors = {"health": "#FF5252", "hunger": "#FFA726", "happiness": "#66BB6A",
                "energy": "#42A5F5", "cleanliness": "#AB47BC"}

        self.status_bars = {}
        for i, key in enumerate(icons.keys(), start=1):
            ctk.CTkLabel(self.status_frame, text=f"{icons[key]} {key.title()}",
                        font=("Poppins", 12), text_color="#333").grid(row=i, column=0, padx=10, pady=4, sticky="w")

            bar = ctk.CTkProgressBar(self.status_frame, width=160, height=13,
                                    fg_color="#D4D4D4", progress_color=colors[key], corner_radius=100)
            bar.set(self.pet_status.get(key, 100) / 100)
            bar.grid(row=i, column=1, padx=8, pady=4)
            self.status_bars[key] = bar
        
        # === ACTION PANEL AT BOTTOM ===
        self.action_frame = tk.Frame(
            parent_frame,
            bg="#D87000",      # translucent grey (adjust last two digits for opacity)
            highlightthickness=0
        )
        # slim, long container hugging the bottom
        self.action_frame.place(relx=0.5, rely=1.0, anchor="s", height=70, relwidth=0.87)

        # === BUTTON PLACEMENT ===
        spacing = 120   # adjust horizontal gap
        start_x = 55
        y_pos = 5       # small padding from top of the bar

        
        for i, (action, img) in enumerate(self.action_images.items()):
            btn = tk.Button(
                self.action_frame,
                image=img,
                text="",
                bd=0,
                bg="#D87000",           # transparent background
                activebackground="#F48C1D",  # subtle hover flash
                relief="flat",
                highlightthickness=0,
                command=lambda a=action: self.perform_action(a)
            )
            btn.place(x=start_x + spacing * i, y=y_pos)
            
        self.update_status_bars()  # sets correct red/green bars immediately

        # Start decay loop immediately if not already running
        if not hasattr(self, "decay_job"):
            self.start_status_decay()

    def show_idle_scene(self):
        """Called after user is idle for 5 seconds"""
        # Decide scene based on pet stats (example: happiness threshold)
        if self.pet_status.get("happiness", 100) > 50:
            idle_scene = "happy"
        else:
            idle_scene = "sad"

        if idle_scene in self.scenes:
            self.current_scene = idle_scene
            self.canvas.configure(image=self.scenes[idle_scene])

    def perform_action(self, action):
        # --- Reset idle timer ---
        if self.idle_after_id:
            self.root.after_cancel(self.idle_after_id)  # cancel previous timer
        self.idle_after_id = self.root.after(self.idle_delay, self.show_idle_scene)

        """Handle user actions like Feed, Play, Clean, Sleep."""
        print(f"Action performed: {action}")  # debug output

        # --- Update status values ---
        if "Feed" in action:
            self.pet_status["hunger"] = min(100, self.pet_status["hunger"] + 20)
            new_scene = "eating"
        elif "Play" in action:
            self.pet_status["happiness"] = min(100, self.pet_status["happiness"] + 15)
            self.pet_status["energy"] = max(0, self.pet_status["energy"] - 10)
            new_scene = "playing"
        elif "Clean" in action:
            self.pet_status["cleanliness"] = 100
            new_scene = "showering"
        elif "Sleep" in action:
            self.pet_status["energy"] = 100
            new_scene = "sleeping"
        else:
            new_scene = "happy"

        # --- YOUR TWEAK: randomly switch mood to happy or sad for fun ---
        if new_scene not in ["eating", "playing", "showering", "sleeping"]:
            # Only apply for neutral actions
            new_scene = random.choice(["happy", "sad"])

        # --- Update all progress bars ---
        self.update_status_bars()

        # --- Update the pet scene ---
        if new_scene in self.scenes:
            self.current_scene = new_scene
            self.canvas.configure(image=self.scenes[new_scene])
        else:
            print(f"⚠️ Scene '{new_scene}' not found in self.scenes")

    def reset_game(self):
        """Restart game with fresh stats"""
        self.pet_status = {
            "health": 100,
            "hunger": 100,
            "happiness": 100,
            "energy": 100,
            "cleanliness": 100
        }
        self.neglect_timer = 0
        self.current_scene = "happy"
        self.change_scene("happy")
        self.update_status_bars()

    def update_status_bars(self):
        for key, bar in self.status_bars.items():
            val = max(0, min(100, self.pet_status.get(key, 0)))
            bar.set(val / 100)

            # Dynamically update progress color
            if val < 50:
                bar.configure(progress_color="#E53935")  # red
            else:
                bar.configure(progress_color="#4CAF50")  # green

    def start_status_decay(self):
        """Decay loop with health logic"""
        self.neglect_timer = getattr(self, "neglect_timer", 0)  # track seconds

        def decay():
            # Passive decay
            self.pet_status["hunger"] = max(0, self.pet_status["hunger"] - 1)
            self.pet_status["energy"] = max(0, self.pet_status["energy"] - 1)
            self.pet_status["cleanliness"] = max(0, self.pet_status["cleanliness"] - 1)
            self.pet_status["happiness"] = max(0, self.pet_status["happiness"] - 1)

            # Check neglect conditions
            critical_stats = ["hunger", "energy", "cleanliness", "happiness"]
            neglected = any(self.pet_status[s] < 50 for s in critical_stats)

            if neglected:
                self.neglect_timer += 5  # seconds
                if self.neglect_timer >= 60:  # 1 min neglected
                    self.pet_status["health"] = max(0, self.pet_status["health"] - 5)
            else:
                self.neglect_timer = 0  # reset timer if cared
                self.pet_status["health"] = min(100, self.pet_status["health"] + 1)

            # Sick logic
            if self.pet_status["health"] < 50:
                self.change_scene("sick")

            # Game over
            if self.pet_status["health"] <= 0:
                messagebox.showinfo("Game Over", "Your pet got too sick! Restarting...")
                self.reset_game()

            # Update UI
            self.update_status_bars()

            # schedule again
            self.decay_job = self.root.after(1000, decay)


        self.decay_job = self.root.after(5000, decay)

    def create_action_buttons(self, parent_frame):
        """Creates a slim bottom action bar with only images (no extra boxes)."""

        # === Bottom bar ===
        self.action_frame = tk.Frame(
            parent_frame,
            bg="#00000040",      # translucent black strip (you can adjust)
            highlightthickness=0
        )
        # long, slim bar touching the bottom
        self.action_frame.place(relx=0.5, rely=1.0, anchor="s", height=80, relwidth=0.9)

        # === Load button images ===
        actions = ["Feed", "Play", "Clean", "Sleep"]
        self.action_images = {}
        for action in actions:
            img_path = os.path.join("assets", f"{action.lower()}.png")
            if os.path.exists(img_path):
                img = Image.open(img_path).resize((60, 60))
                self.action_images[action] = ImageTk.PhotoImage(img)
            else:
                self.action_images[action] = None

        # === Center buttons evenly ===
        total_actions = len(actions)
        spacing = (self.action_frame.winfo_reqwidth() // (total_actions + 1))

        # After the frame is visible, place the buttons centered
        parent_frame.after(100, lambda: self._place_action_buttons(actions))

    def _place_action_buttons(self, actions):
        """Helper to place action buttons evenly after frame is drawn."""
        self.action_frame.update_idletasks()

        frame_width = self.action_frame.winfo_width()
        spacing = frame_width // (len(actions) + 1)
        y_pos = 10  # small top padding

        for i, action in enumerate(actions, start=1):
            btn = tk.Button(
                self.action_frame,
                image=self.action_images[action],
                bd=0,
                bg="#00000000",  # fully transparent background
                activebackground="#00000000",
                highlightthickness=0,
                relief="flat",
                command=lambda a=action: self.perform_action(a)
            )
            btn.place(x=spacing * i - 30, y=y_pos)  # center horizontally

    def change_scene(self, mood):
        """Safely switch background scenes and retain image reference."""
        if mood in self.scenes:
            self.current_scene = mood
            self.canvas.configure(image=self.scenes[mood])
            self.canvas.image = self.scenes[mood]  # 🧠 keep a reference!
        else:
            print(f"⚠️ Scene '{mood}' not found in self.scenes")

   

def main():
    """Main application entry point"""
    try:
        # Initialize database
        print("Initializing database...")
        db.init_database()
        print("✓ Database initialized successfully")
        
        # Test AI connection
        print("Testing AI connection...")
        ai_available = ai_client.test_ai_connection()
        if ai_available:
            print("✓ AI client connected successfully")
        else:
            print("⚠ AI client using fallback responses only")
        
        # Create and run GUI
        print("Starting PetPal application...")
        root = tk.Tk()
        app = PetCareApp(root)
        
        # Handle window closing
        def on_closing():
            try:
                print("Closing application...")
                db.close_database()
                root.destroy()
            except Exception as e:
                print(f"Error during shutdown: {e}")
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        print("✓ PetPal started successfully!")
        print("=" * 50)
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Startup Error", f"Could not start PetPal: {e}")

if __name__ == "__main__":
    main()
    
    
