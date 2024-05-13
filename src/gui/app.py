import tkinter as tk
import customtkinter as ctk
from tkinterweb import HtmlFrame

from src.processors.cursor_renderer import CursorRenderer
from src.processors.mouse_event_recorder import MouseEventRecorder
from src.processors.screen_recorder import ScreenRecorder
from src.constants import (
    OREAL_APP_NAME,
    OREAL_APP_DESCRIPTION,
    OREAL_FEED_WEB_PAGE,
    APP_MULTIPLE_INSTANCE_OF_RECORDER_MESSAGE,
    APP_MULTIPLE_INSTANCE_OF_VIDEO_EDITOR_MESSAGE,
)
from src.gui.recorder import ScreenRecorderGUI
from src.gui.editor import VideoEditor
from tkinter import messagebox


class OrealApp:
    def __init__(self):
        self.width = 980
        self.height = 700
        self.master = ctk.CTk()
        self.master.title(OREAL_APP_NAME)
        self.master.geometry("980x700")
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

        oreal_desc = ctk.CTkLabel(
            title_container,
            text=OREAL_APP_DESCRIPTION,
        )
        oreal_desc.pack(pady=10, side=tk.RIGHT, padx=30)

        main_frame = tk.PanedWindow(
            self.master,
            orient=tk.HORIZONTAL,
            bg="#2b2b2b",
            showhandle=True,
            handlepad=self.height / 2,
            sashwidth=5,
            handlesize=10,
        )
        main_frame.pack(fill=tk.BOTH, expand=True)
        left_side = ctk.CTkFrame(main_frame)
        right_side = ctk.CTkFrame(main_frame)
        main_frame.add(left_side)
        main_frame.add(right_side)
        # Add sidebar with tabs for old projects and past recordings
        sidebar_frame = ctk.CTkFrame(left_side)
        sidebar_frame.pack(
            side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(10, 0), pady=10
        )

        # Add feed of some things
        feed_frame = ctk.CTkFrame(right_side)
        feed_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        feed = HtmlFrame(feed_frame, messages_enabled=False)
        feed.load_url(OREAL_FEED_WEB_PAGE)
        feed.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Add record new button at the bottom
        record_new_button = ctk.CTkButton(
            feed_frame, text="Record New", command=self.open_screen_recorder
        )
        record_new_button.pack(side=tk.BOTTOM, padx=10, pady=10)

    def open_video_editor(self):
        if self.video_editor is None:
            self.video_editor = VideoEditor(master=self.master)
        else:
            messagebox.showwarning(
                APP_MULTIPLE_INSTANCE_OF_VIDEO_EDITOR_MESSAGE[0],
                APP_MULTIPLE_INSTANCE_OF_VIDEO_EDITOR_MESSAGE[1],
            )

    def open_screen_recorder(self):
        if self.recorder is None:
            self.recorder = ScreenRecorderGUI(
            self.master,
            ScreenRecorder(CursorRenderer("assets/cursor.png"), MouseEventRecorder()),
        )
        else:
            messagebox.showwarning(
                APP_MULTIPLE_INSTANCE_OF_RECORDER_MESSAGE[0],
                APP_MULTIPLE_INSTANCE_OF_RECORDER_MESSAGE[1],
            )

    def edit_project(self):
        # Implement edit project functionality
        pass

    def run(self):
        self.master.mainloop()


if __name__ == "__main__":
    app = OrealApp()
    app.run()
