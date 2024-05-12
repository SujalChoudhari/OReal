import tkinter as tk
from tkinter import filedialog

class ScreenRecorderGUI:
    def __init__(self, master, screen_recorder):
        self.master = master
        self.screen_recorder = screen_recorder
        self.recording = False

        master.title("Screen Recorder")

        # Name changer
        self.name_label = tk.Label(master, text="File Name:")
        self.name_label.grid(row=0, column=0)
        self.name_entry = tk.Entry(master)
        self.name_entry.grid(row=0, column=1)

        # Audio selection
        self.audio_var = tk.IntVar(value=1)
        self.audio_checkbox = tk.Checkbutton(master, text="Record Audio", variable=self.audio_var)
        self.audio_checkbox.grid(row=1, columnspan=2)

        # Record button
        self.record_button = tk.Button(master, text="Record", command=self.toggle_record)
        self.record_button.grid(row=2, columnspan=2)

        # Retake button
        self.retake_button = tk.Button(master, text="Retake", command=self.retake)
        self.retake_button.grid(row=3, columnspan=2)

    def toggle_record(self):
        if not self.recording:
            filename = self.name_entry.get() if self.name_entry.get() else "new_file"
            audio = True if self.audio_var.get() == 1 else False
            self.screen_recorder.record_screen(filename, audio)
            self.recording = True
            self.record_button.config(text="Stop Recording")
        else:
            self.screen_recorder.stop_recording()
            self.recording = False
            self.record_button.config(text="Record")

    def retake(self):
        if self.recording:
            self.screen_recorder.stop_recording()
            self.recording = False
            self.record_button.config(text="Record")
        self.name_entry.delete(0, tk.END)