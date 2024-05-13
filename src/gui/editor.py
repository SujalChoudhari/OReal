import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

from src.constants import OREAL_APP_NAME

class VideoEditor:
    def __init__(self, master):
        self.main = master
        self.master = ctk.CTkToplevel(self.main)
        self.master.title(f"{OREAL_APP_NAME} | Video Editor")
        self.master.geometry("800x600")
        self.master.focus()
        self.create_sidebar()
        self.create_preview_area()
        self.create_timeline()

    def create_sidebar(self):
        sidebar_frame = ctk.CTkFrame(self.master, width=100)
        sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Add buttons to the sidebar
        open_button = ctk.CTkButton(
            sidebar_frame, text="Open Video", command=self.open_video
        )
        open_button.pack(pady=10)

    def create_preview_area(self):
        self.preview_frame = ctk.CTkFrame(self.master)
        self.preview_frame.pack(expand=True, fill=tk.BOTH)

        # Add a canvas to show video preview
        self.preview_canvas = ctk.CTkCanvas(self.preview_frame)
        self.preview_canvas.pack(expand=True, fill=tk.BOTH)

        # You can add video preview functionality here...

    def create_timeline(self):
        timeline_frame = ctk.CTkFrame(self.master)
        timeline_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Add timeline elements such as sliders, buttons, etc.
        self.timeline_slider = ctk.CTkSlider(
            timeline_frame, orientation=tk.HORIZONTAL, number_of_steps=100
        )
        self.timeline_slider.pack(fill=tk.X)

        # You can add more timeline elements and functionality here...

    def open_video(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Video Files", "*.mp4;*.avi")]
        )
        # Here you can load and display the video in the preview area
