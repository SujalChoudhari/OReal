import tkinter as tk
import customtkinter as ctk
from tkinterweb import HtmlFrame
import os

from src.processors.cursor_renderer import CursorRenderer
from src.processors.mouse_event_recorder import MouseEventRecorder
from src.processors.screen_recorder import ScreenRecorder
from src.constants import (
    OREAL_APP_NAME,
    OREAL_APP_DESCRIPTION,
    OREAL_FEED_WEB_PAGE,
    OREAL_RECORDINGS_DIR,
    OREAL_FILE_EXT,
    APP_MULTIPLE_INSTANCE_OF_RECORDER_MESSAGE,
    APP_MULTIPLE_INSTANCE_OF_VIDEO_EDITOR_MESSAGE,
)
from src.gui.recorder import ScreenRecorderGUI
from src.gui.editor import VideoEditor


class OrealApp:
    def __init__(self):
        self.width = 980
        self.height = 700
        self.master = ctk.CTk()
        self.master.title(OREAL_APP_NAME)
        self.master.geometry("980x700")
        self.master.minsize(800, 600)  # Set minimum size
        self.create_ui()

        self.video_editor = None
        self.recorder = None

    def create_ui(self):
        # Add data about Oreal
        title_container = ctk.CTkFrame(self.master)
        title_container.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        oreal_title = ctk.CTkLabel(
            title_container, text=OREAL_APP_NAME, font=("Open Sans", 36, "bold")
        )
        oreal_title.pack(pady=10, side=tk.LEFT, padx=30)

        # # Add record new button at the bottom of the projects tab
        record_new_button = ctk.CTkButton(
            title_container,
            text="New",
            command=self.open_screen_recorder,
        )
        record_new_button.pack(side=tk.RIGHT, fill=tk.BOTH, pady=10, padx=(5, 30))

        oreal_desc = ctk.CTkLabel(
            title_container,
            text=OREAL_APP_DESCRIPTION,
        )
        oreal_desc.pack(pady=10, side=tk.RIGHT, padx=10)

        main_frame = ctk.CTkTabview(self.master)
        main_frame.add("Recordings")
        main_frame.add("Feed")

        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add recordings tab
        recordings_frame = ctk.CTkScrollableFrame(main_frame.tab("Recordings"))
        recordings_frame.pack(fill=tk.BOTH, expand=True)

        # Add files from /recordings directory to the listbox
        # Add files from /recordings directory to the listbox
        if os.path.exists(OREAL_RECORDINGS_DIR) and os.path.isdir(OREAL_RECORDINGS_DIR):
            for i, filename in enumerate(os.listdir(OREAL_RECORDINGS_DIR)):
                if filename.endswith(
                    OREAL_FILE_EXT
                ):  # Assuming you want to show only files with a specific extension
                    row = i // 4  # Calculate row index
                    col = i % 4  # Calculate column index

                    frame = ctk.CTkFrame(recordings_frame)
                    frame.grid(row=row, column=col, padx=5, pady=5)

                    title = ctk.CTkLabel(frame, text=filename)
                    title.pack(side=tk.TOP, padx=5, pady=2)

                    edit_button = ctk.CTkButton(
                        frame,
                        text="Edit",
                        command=lambda f=filename: self.open_video_editor(f),
                    )
                    edit_button.pack(side=tk.TOP, padx=5, pady=2)

            # Configure row and column weights to fill the entire space
            for i in range(row + 1):  # Add 1 to row to account for 0-based indexing
                recordings_frame.grid_rowconfigure(i, weight=1)
            for j in range(4):  # Assuming 4 columns
                recordings_frame.grid_columnconfigure(j, weight=1)

        # Add projects tab
        main_frame.set("Feed")
        feed_frame = ctk.CTkFrame(main_frame.tab("Feed"))
        feed_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        feed = HtmlFrame(feed_frame, messages_enabled=False)
        feed.load_url(OREAL_FEED_WEB_PAGE)
        feed.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def open_video_editor(self, file_name):
        self.master.iconify()
        self.video_editor = VideoEditor(master=self.master)

    def open_screen_recorder(self):
        self.master.iconify()
        self.recorder = ScreenRecorderGUI(
            self.master,
            ScreenRecorder(CursorRenderer("assets/cursor.png"), MouseEventRecorder()),
        )

    def run(self):
        self.master.mainloop()


if __name__ == "__main__":
    app = OrealApp()
    app.run()
