import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from threading import Thread
import subprocess
import random
from src.constants import (
    OREAL_APP_NAME,
    OREAL_WORKING_DIR,
    OREAL_RECORDINGS_DIR,
    OREAL_DEFAULT_VIDEO_EXT,
    OREAL_FILE_EXT,
    OREAL_DEFAULT_THUMBNAIL_EXT,
    RECORDER_GUI_NAME,
    RECORDER_INPUT_FILENAME_TEXT,
    RECORDER_AUDIO_CHECKBOX_TEXT,
    RECORDER_RECORD_BUTTON_TEXT,
    RECORDER_STOP_RECORDING_BUTTON_TEXT,
    RECORDER_REPLAY_BUTTON_TEXT,
    RECORDER_SAVE_BUTTON_TEXT,
    RECORDER_DEFAULT_NAME_PREFIX_POOL,
    RECORDER_DEFAULT_NAME_SUFFIX_POOL,
)
from src.processors.encoder import Encoder
from PIL import Image
import time
import os
from src.processors.screen_recorder import ScreenRecorder
from src.processors.thumbnail import generate_thumbnail


class ScreenRecorderGUI:
    def __init__(self, master: ctk.CTk, screen_recorder: ScreenRecorder):
        self.main = master
        self.master = ctk.CTkToplevel(self.main)
        self.screen_recorder = screen_recorder
        self.recording = False
        self.playing = False
        self.master.title(RECORDER_GUI_NAME)
        self.master.resizable(False, False)
        self.max_live_preview_size = screen_recorder.max_size

        # Outer Frame
        self.outer_frame = ctk.CTkFrame(self.master)
        self.outer_frame.pack()

        # Create a frame for better organization
        self.main_frame = ctk.CTkFrame(self.outer_frame)
        self.main_frame.pack(padx=20, pady=20)

        # Add a title label
        self.title_label = ctk.CTkLabel(
            self.main_frame, text=OREAL_APP_NAME, font=("Arial", 24, "bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(10, 10))

        # Name changer
        self.name_label = ctk.CTkLabel(
            self.main_frame, text=RECORDER_INPUT_FILENAME_TEXT
        )
        self.name_label.grid(row=1, column=0, sticky="w", pady=20, padx=20)
        self.filename_var = tk.StringVar()
        self.filename_var.trace_add(
            "write",
            lambda name, index, mode, var=self.filename_var: self.on_file_name_input_change(
                var
            ),
        )
        self.name_entry = ctk.CTkEntry(self.main_frame, textvariable=self.filename_var)
        self.name_entry.grid(row=1, column=1, pady=20, padx=20, sticky="ew")
        self.name_entry_error = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Arial", 12),
            text_color="#ff9999",
        )
        self.name_entry_error.grid(row=2, column=1, columnspan=2, padx=20)

        # Audio selection
        self.audio_var = ctk.BooleanVar(value=True)
        self.audio_checkbox = ctk.CTkCheckBox(
            self.main_frame,
            text=RECORDER_AUDIO_CHECKBOX_TEXT,
            variable=self.audio_var,
            font=("Arial", 12),
        )
        self.audio_checkbox.grid(row=3, column=0, columnspan=2, sticky="w", padx=20)

        self.tk_recording_frame = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Arial", 24),
            width=self.max_live_preview_size[0],
            height=self.max_live_preview_size[1],
        )
        self.tk_recording_frame.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=20,
            pady=(20, 10),
        )

        # Record button
        self.record_button = ctk.CTkButton(
            self.main_frame,
            text=RECORDER_RECORD_BUTTON_TEXT,
            command=self.toggle_record,
            font=("Arial", 14),
        )
        self.record_button.grid(
            row=5, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 10)
        )

        # Replay button
        self.replay_button = ctk.CTkButton(
            self.main_frame,
            text=RECORDER_REPLAY_BUTTON_TEXT,
            command=self.replay,
            font=("Arial", 14),
        )
        self.replay_button.grid(
            row=6, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 20)
        )
        self.replay_button.configure(state="disabled")

        self.compress_button = ctk.CTkButton(
            self.main_frame,
            text=RECORDER_SAVE_BUTTON_TEXT,
            command=self.save,
            font=("Arial", 14),
        )
        self.compress_button.configure(state="disabled")
        self.compress_button.grid(
            row=7, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 20)
        )

        self.name_entry.insert(0, self.get_default_name())

    def on_file_name_input_change(self, var):
        name = var.get()
        if os.path.exists(
            os.path.join(OREAL_RECORDINGS_DIR, name + "." + OREAL_FILE_EXT)
        ):
            self.name_entry_error.configure(text="File already exists")
            self.record_button.configure(state="disabled")
        else:
            self.name_entry_error.configure(text="")
            self.record_button.configure(state="normal")

    def get_default_name(self):
        name = random.choice(RECORDER_DEFAULT_NAME_PREFIX_POOL) + random.choice(
            RECORDER_DEFAULT_NAME_SUFFIX_POOL
        )
        # check if exists in RECORDINGS oif yes, append another prefix.
        while os.path.exists(
            os.path.join(OREAL_RECORDINGS_DIR, name + "." + OREAL_FILE_EXT)
        ):
            name = random.choice(RECORDER_DEFAULT_NAME_PREFIX_POOL) + name
        return name

    def toggle_record(self):
        def create_thumbnail():
            name = self.name_entry.get() + "." + OREAL_DEFAULT_THUMBNAIL_EXT
            generate_thumbnail(name)

        def start_recording_after(i):
            if i > 0:
                self.tk_recording_frame.configure(text=f"Recording in {i}")
                self.master.after(1000, start_recording_after, i - 1)
            else:
                self.recording = True
                self.record_thread = Thread(target=self.recording_thread)
                self.record_thread.start()
                self.record_button.configure(text=RECORDER_STOP_RECORDING_BUTTON_TEXT)
                self.tk_recording_frame.configure(text="Recording...")
                self.name_entry.configure(state="disabled")
                self.master.after(2000, create_thumbnail)

        if not self.recording:
            start_recording_after(3)  # Start the countdown to record
            # clear the working directory
            for f in os.listdir(OREAL_WORKING_DIR):
                os.remove(os.path.join(OREAL_WORKING_DIR, f))
            self.compress_button.configure(state="disabled")
        else:
            self.tk_recording_frame.configure(text="")
            self.screen_recorder.stop_recording()
            if self.record_thread.is_alive():
                self.record_thread.join()
            self.recording = False
            self.record_button.configure(text=RECORDER_RECORD_BUTTON_TEXT)
            self.compress_button.configure(state="normal")

            self.name_entry.configure(state="normal")
            self.replay_button.configure(state="normal")
            self.record_button.configure(state="disabled")
            self.name_entry_error.configure(text="Name already exists.")

    def recording_thread(self):
        filename = self.name_entry.get() if self.name_entry.get() else "new_file"
        audio = self.audio_var.get()
        self.screen_recorder.setup(filename, audio, self.tk_recording_frame)
        self.screen_recorder.record()

    def replay(self):
        filename = self.name_entry.get() if self.name_entry.get() else "new_file"
        video_file = f"{OREAL_WORKING_DIR}{filename}.avi"
        audio_file = f"{OREAL_WORKING_DIR}{filename}.wav"

        # If audio was recorded, play it
        if self.audio_var.get():
            subprocess.Popen(["ffplay", "-autoexit", audio_file])

        # Start video replay in a subprocess
        subprocess.Popen(["ffplay", "-autoexit", video_file])

    def save(self):
        def reset_states():
            self.compress_button.configure(text=RECORDER_SAVE_BUTTON_TEXT)

        filename = self.name_entry.get() if self.name_entry.get() else "new_file"
        encoder = Encoder(OREAL_WORKING_DIR + filename, OREAL_RECORDINGS_DIR + filename)
        encoder.encode()
        self.compress_button.configure(state="disabled", text="Done")
        self.master.after(2000, reset_states)
