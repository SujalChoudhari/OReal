import tkinter as tk
from tkinter import colorchooser
import customtkinter as ctk
from tkinterweb import HtmlFrame
import os

from src.processors.cursor_renderer import CursorRenderer
from src.processors.mouse_event_recorder import MouseEventRecorder
from src.processors.screen_recorder import ScreenRecorder
from src.processors.encoder import Encoder
from src.constants import (
    OREAL_APP_NAME,
    OREAL_APP_DESCRIPTION,
    OREAL_FEED_WEB_PAGE,
    OREAL_RECORDINGS_DIR,
    OREAL_FILE_EXT,
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

        self.current_page = 1
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

        def load_recordings(event=None, page=1, items_per_page=12):
            self.page_number_display.configure(text=f"Page {page}")
            if main_frame.get() != "Recordings":
                return

            # Clear previous content
            for widget in recordings_frame.winfo_children():
                widget.destroy()

            # Add files from /recordings directory to the listbox
            recordings_dir = OREAL_RECORDINGS_DIR
            if os.path.exists(recordings_dir) and os.path.isdir(recordings_dir):
                recordings = [
                    filename
                    for filename in os.listdir(recordings_dir)
                    if filename.endswith(OREAL_FILE_EXT)
                ]
                total_items = len(recordings)
                start_index = (page - 1) * items_per_page
                end_index = min(start_index + items_per_page, total_items)

                row, col = 0, 0
                for i in range(start_index, end_index):
                    filename = recordings[i]
                    row = (i - start_index) // 4  # Calculate row index
                    col = (i - start_index) % 4  # Calculate column index

                    decoder = Encoder(
                        os.path.join(recordings_dir, filename),
                        os.path.join(recordings_dir, filename),
                    )
                    image_content = decoder.get_thumbnail()

                    frame = ctk.CTkFrame(recordings_frame)
                    frame.grid(
                        row=row,
                        column=col,
                        padx=5,
                        pady=5,
                    )

                    image = ctk.CTkLabel(
                        frame,
                        text="",
                        image=ctk.CTkImage(light_image=image_content, size=(200, 150)),
                    )
                    image.pack(side=tk.TOP, padx=5, pady=2)

                    title = ctk.CTkLabel(
                        frame,
                        text=filename,
                    )
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

        # Add a function to load the next page of recordings
        def load_next_page():
            self.current_page += 1
            load_recordings(page=self.current_page)

        # Add a function to load the previous page of recordings
        def load_previous_page():
            self.current_page = max(self.current_page - 1, 1)
            load_recordings(page=self.current_page)

        main_frame = ctk.CTkTabview(self.master, command=load_recordings)
        main_frame.add("Recordings")
        main_frame.add("Feed")

        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        past_project_tab = ctk.CTkFrame(main_frame.tab("Recordings"))
        past_project_tab.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        # Add recordings tab
        recordings_frame = ctk.CTkScrollableFrame(past_project_tab)
        recordings_frame.pack(fill=tk.BOTH, expand=True)

        # Add navigation buttons
        next_button = ctk.CTkButton(
            past_project_tab, text="Next", command=load_next_page
        )
        next_button.pack(side=tk.RIGHT, anchor="n", padx=5, pady=5)

        self.page_number_display = ctk.CTkLabel(past_project_tab, text="Page 1")
        self.page_number_display.pack(side=tk.RIGHT, anchor="n", padx=5, pady=5)

        previous_button = ctk.CTkButton(
            past_project_tab, text="Previous", command=load_previous_page
        )
        previous_button.pack(side=tk.RIGHT, anchor="n", padx=5, pady=5)

        load_recordings()  # Initial load

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
