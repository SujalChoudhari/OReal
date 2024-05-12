import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from src.screen_recorder import ScreenRecorder
from threading import Thread
import subprocess
from src.constants import APP_NAME
from PIL import Image
import time


class ScreenRecorderGUI:
    def __init__(self, master: ctk.CTk, screen_recorder: ScreenRecorder):
        self.master = master
        self.screen_recorder = screen_recorder
        self.recording = False
        self.playing = False
        master.title(APP_NAME)
        master.resizable(False, False)
        self.max_live_preview_size = screen_recorder.max_size

        # Outer Frame
        self.outer_frame = ctk.CTkFrame(master)
        self.outer_frame.pack()

        # Create a frame for better organization
        self.main_frame = ctk.CTkFrame(self.outer_frame)
        self.main_frame.pack(padx=20, pady=20)

        # Add a title label
        self.title_label = ctk.CTkLabel(
            self.main_frame, text=APP_NAME, font=("Arial", 24, "bold")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(10, 10))

        # Name changer
        self.name_label = ctk.CTkLabel(self.main_frame, text="File Name:")
        self.name_label.grid(row=1, column=0, sticky="w", pady=20, padx=20)
        self.name_entry = ctk.CTkEntry(self.main_frame)
        self.name_entry.grid(row=1, column=1, pady=20, padx=20, sticky="ew")

        # Audio selection
        self.audio_var = ctk.BooleanVar(value=True)
        self.audio_checkbox = ctk.CTkCheckBox(
            self.main_frame,
            text="Record Audio",
            variable=self.audio_var,
            font=("Arial", 12),
        )
        self.audio_checkbox.grid(row=2, column=0, columnspan=2, sticky="w", padx=20)

        self.tk_recording_frame = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Arial", 24),
            width=self.max_live_preview_size[0],
            height=self.max_live_preview_size[1],
        )
        self.tk_recording_frame.grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=20,
            pady=(20, 10),
        )

        # Record button
        self.record_button = ctk.CTkButton(
            self.main_frame,
            text="Record",
            command=self.toggle_record,
            font=("Arial", 14),
        )
        self.record_button.grid(
            row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=(20, 10)
        )

        # Replay button
        self.replay_button = ctk.CTkButton(
            self.main_frame,
            text="Replay",
            command=self.replay,
            font=("Arial", 14),
        )
        self.replay_button.grid(
            row=5, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 20)
        )

    def toggle_record(self):
        def start_recording_after(i):
            if i > 0:
                self.tk_recording_frame.configure(text=f"Recording in {i}")
                self.master.after(1000, start_recording_after, i - 1)
            else:
                self.recording = True
                self.record_thread = Thread(target=self.recording_thread)
                self.record_thread.start()
                self.record_button.configure(text="Stop Recording")
                self.tk_recording_frame.configure(text="Recording...")

        if not self.recording:
            start_recording_after(3)  # Start the countdown to record
        else:
            self.tk_recording_frame.configure(text="")
            self.screen_recorder.stop_recording()
            if self.record_thread.is_alive():
                self.record_thread.join()
                print("Recording stopped.")
            self.recording = False
            self.record_button.configure(text="Record")

    def recording_thread(self):
        filename = self.name_entry.get() if self.name_entry.get() else "new_file"
        audio = self.audio_var.get()
        self.screen_recorder.setup(filename, audio, self.tk_recording_frame)
        self.screen_recorder.record()

    def replay(self):
        filename = self.name_entry.get() if self.name_entry.get() else "new_file"
        video_file = f"{filename}.avi"
        audio_file = f"{filename}.wav"

        # If audio was recorded, play it
        if self.audio_var.get():
            subprocess.Popen(["ffplay", "-autoexit", audio_file])

        # Start video replay in a subprocess
        subprocess.Popen(["ffplay", "-autoexit", video_file])
