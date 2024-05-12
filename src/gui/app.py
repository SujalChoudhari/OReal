import tkinter as tk
import customtkinter as ctk
from tkinterweb import HtmlFrame

from src.cursor_renderer import CursorRenderer
from src.mouse_event_recorder import MouseEventRecorder
from src.screen_recorder import ScreenRecorder
from src.constants import OREAL_APP_NAME, OREAL_APP_DESCRIPTION, OREAL_FEED_WEB_PAGE
from src.gui.recorder import ScreenRecorderGUI
from src.gui.editor import VideoEditor


class OrealApp:
    def __init__(self):
        self.width = 980
        self.height = 700
        self.master = ctk.CTk()
        self.master.title(OREAL_APP_NAME)
        self.master.geometry("980x700")
        self.create_ui()

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

        main_frame = tk.PanedWindow(self.master, orient=tk.HORIZONTAL, bg="#2b2b2b",showhandle=True,handlepad=self.height/2,sashwidth=5,handlesize=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        left_side = ctk.CTkFrame(main_frame)
        right_side = ctk.CTkFrame(main_frame)
        main_frame.add(left_side)
        main_frame.add(right_side)
        # Add sidebar with tabs for old projects and past recordings
        sidebar_frame = ctk.CTkFrame(left_side)
        sidebar_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(10, 0), pady=10)

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
        VideoEditor(master=self.master)

    def open_screen_recorder(self):
        ScreenRecorderGUI(
            self.master,
            ScreenRecorder(CursorRenderer("assets/cursor.png"), MouseEventRecorder()),
        )

    def edit_project(self):
        # Implement edit project functionality
        pass

    def run(self):
        self.master.mainloop()


if __name__ == "__main__":
    app = OrealApp()
    app.run()
