# /path/to/video_editor.py

import os
import tkinter as tk
from PIL import Image
import customtkinter as ctk
import matplotlib
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from src.constants import (
    OREAL_WORKING_DIR,
    OREAL_RECORDINGS_DIR,
    OREAL_DEFAULT_THUMBNAIL_EXT,
    OREAL_BACKGROUNDS_DIR,
    OREAL_CURSOR_DIR,
    OREAL_BACKGROUND_PREVIEWS_DIR,
)
from src.processors.encoder import Encoder
from src.processors.mouse_input_processor import MouseInputProcessor
from src.processors.make_video import make_video

matplotlib.use("TkAgg")


class VideoEditor:
    def __init__(self, master, current_vid_path: str):
        self.main = master
        self.master = ctk.CTkToplevel(self.main)
        self.master.title("Video Editor")
        self.master.geometry("1080x720")
        self.master.focus()

        self.backgrounds_dir = OREAL_BACKGROUNDS_DIR
        self.cursors_dir = OREAL_CURSOR_DIR
        self.background_previews_dir = OREAL_BACKGROUND_PREVIEWS_DIR

        self.backgrounds = os.listdir(self.backgrounds_dir)
        self.cursors = os.listdir(self.cursors_dir)

        self.selected_background = self.backgrounds[0]
        self.selected_cursor = self.cursors[0]
        self.zoom_smoothness_variable = tk.IntVar(value=0)
        self.scale_smoothness_variable = tk.IntVar(value=0)
        self.mouse_event_processor = MouseInputProcessor()
        self.create_ui()

        self.current_vid_path = current_vid_path
        self.clear_working_directory()

        encoder = Encoder(
            os.path.join(OREAL_WORKING_DIR, current_vid_path),
            os.path.join(OREAL_RECORDINGS_DIR, current_vid_path),
        )
        encoder.decode()

        self.master.update()
        self.preview_image(is_background=True, preset=self.selected_background)
        self.preview_image(is_background=False, preset=self.selected_cursor)
        self.generate_background_zoom_graph()
        self.generate_mouse_size_graph()

    def clear_working_directory(self):
        for f in os.listdir(OREAL_WORKING_DIR):
            os.remove(os.path.join(OREAL_WORKING_DIR, f))

    def create_ui(self):
        title_holder = ctk.CTkFrame(self.master)
        title_holder.pack(side=tk.TOP, fill=tk.X)
        ctk.CTkLabel(title_holder, text="Video Editor", font=("Arial", 14)).pack(
            side=tk.LEFT, padx=10, pady=10
        )

        self.center_preview_area = ctk.CTkTabview(self.master)
        self.center_preview_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.center_preview_area.add("Preview")
        self.center_preview_area.add("Mouse Size Visualizer")
        self.center_preview_area.add("Screen Zoom Visualizer")
        self.center_preview_area.add("Generate Video")

        self.create_generate_video_tab()
        self.create_preview_tab()
        self.create_mouse_size_visualizer_tab()
        self.create_screen_zoom_visualizer_tab()

    def create_generate_video_tab(self):
        self.generate_video_frame = ctk.CTkFrame(
            self.center_preview_area.tab("Generate Video")
        )
        self.generate_video_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.save_smoothness_parameter_button = ctk.CTkButton(
            self.generate_video_frame,
            text="Save Smoothness Parameters",
            command=self.save_smoothness_parameter,
        )
        self.save_smoothness_parameter_button.pack(side=tk.TOP, padx=10, pady=10)
        self.make_btn = ctk.CTkButton(
            self.generate_video_frame,
            text="Make",
            command=lambda: make_video(self.selected_background, self.selected_cursor),
        )
        self.make_btn.pack(side=tk.TOP, padx=10, pady=10)

    def save_smoothness_parameter(self):
        self.mouse_event_processor.save_to_file()

    def create_preview_tab(self):
        self.preview_area = ctk.CTkFrame(self.center_preview_area.tab("Preview"))
        self.preview = ctk.CTkFrame(self.preview_area)
        self.preview.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        self.preview_area.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        self.preview_label = ctk.CTkLabel(self.preview, text="")
        self.preview_label.pack(expand=True, fill=tk.BOTH)

        self.pallet = ctk.CTkTabview(self.preview_area)
        self.pallet.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        self.pallet.add("Background")
        self.pallet.add("Cursor")

        self.create_preset_selector(
            self.background_previews_dir, "Background", self.backgrounds, True
        )
        self.create_preset_selector(self.cursors_dir, "Cursor", self.cursors, False)

    def create_mouse_size_visualizer_tab(self):
        self.mouse_size_visualizer = ctk.CTkFrame(
            self.center_preview_area.tab("Mouse Size Visualizer")
        )
        self.mouse_size_visualizer.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.mouse_size_visualizer_graph = ctk.CTkFrame(self.mouse_size_visualizer)
        self.mouse_size_visualizer_graph.pack(expand=True, fill=tk.BOTH)

        label_frame = ctk.CTkFrame(self.mouse_size_visualizer)
        label_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        ctk.CTkLabel(label_frame, text="Scale Smoothness").pack(side=tk.LEFT)

        self.scale_smoothness_input = ctk.CTkSlider(
            self.mouse_size_visualizer,
            from_=1,
            to=100,
            number_of_steps=100,
            variable=self.scale_smoothness_variable,
            command=self.schedule_mouse_size_graph_update,
        )
        self.scale_smoothness_input.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

    def create_screen_zoom_visualizer_tab(self):
        self.screen_zoom_visualizer = ctk.CTkFrame(
            self.center_preview_area.tab("Screen Zoom Visualizer")
        )
        self.screen_zoom_visualizer.pack(side=tk.TOP, expand=True, fill=tk.BOTH)
        self.screen_zoom_visualizer_graph = ctk.CTkFrame(self.screen_zoom_visualizer)
        self.screen_zoom_visualizer_graph.pack(expand=True, fill=tk.BOTH)

        label_frame = ctk.CTkFrame(self.screen_zoom_visualizer)
        label_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        ctk.CTkLabel(label_frame, text="Zoom Smoothness").pack(side=tk.LEFT)

        self.zoom_smoothness_input = ctk.CTkSlider(
            self.screen_zoom_visualizer,
            from_=1,
            to=100,
            number_of_steps=100,
            variable=self.zoom_smoothness_variable,
            command=self.schedule_background_zoom_graph_update,
        )
        self.zoom_smoothness_input.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

    def create_preset_selector(self, directory, title, presets, is_background=True):
        holder_frame = ctk.CTkScrollableFrame(self.pallet.tab(title))
        holder_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        for preset in presets:
            preset_image = Image.open(os.path.join(directory, preset))
            preset_photo = ctk.CTkImage(
                light_image=preset_image,
                dark_image=preset_image,
                size=(200, 200 * 9 / 16) if is_background else (200, 200),
            )

            frame = ctk.CTkFrame(holder_frame)
            frame.pack(pady=5)
            label = ctk.CTkLabel(frame, text="", image=preset_photo)
            label.image = preset_photo
            label.pack(side=tk.LEFT)
            label.bind(
                "<Button-1>",
                lambda event, image=preset_photo, is_background=is_background, preset=preset: self.preview_image(
                    is_background, preset
                ),
            )

    def preview_image(self, is_background=True, preset=""):
        if is_background:
            self.selected_background = preset
        else:
            self.selected_cursor = preset

        new_background = Image.open(
            os.path.join(self.backgrounds_dir, self.selected_background)
        )
        new_cursor = Image.open(os.path.join(self.cursors_dir, self.selected_cursor))

        vid_thumbnail = Image.open(
            f"{OREAL_WORKING_DIR}{self.current_vid_path}.{OREAL_DEFAULT_THUMBNAIL_EXT}"
        )

        vid_thumbnail = vid_thumbnail.resize(
            (
                int(new_background.size[0] * 0.8),
                int(new_background.size[0] * 9 // 16 * 0.8),
            ),
        )

        cursor_height = new_background.size[1] // 4
        cursor_width = new_background.size[1] // 4
        new_cursor = new_cursor.resize((cursor_width, cursor_height))

        paste_position = (
            new_background.size[0] // 2 - vid_thumbnail.size[0] // 2,
            new_background.size[1] // 2 - vid_thumbnail.size[1] // 2,
        )
        new_background.paste(vid_thumbnail, paste_position)

        cursor_position = (
            new_background.size[0] - new_cursor.size[0] - 150 * 16 // 9,
            new_background.size[1] - new_cursor.size[1] - 150,
        )
        new_background.paste(new_cursor, cursor_position, new_cursor)

        new_background = new_background.resize(
            (
                self.preview_label.winfo_height() * 16 // 9 // 2,
                self.preview_label.winfo_height() // 2,
            ),
        )

        display_image = ctk.CTkImage(
            light_image=new_background,
            size=(
                self.preview_label.winfo_width() * 0.8,
                self.preview_label.winfo_width() * 0.8 * 9 // 16,
            ),
        )
        self.preview_label.configure(image=display_image)

    def draw_line_graph(self, root: ctk.CTkFrame, data: list[float], smoothness: int):
        plt.close("all")
        fig, ax = plt.subplots(figsize=(4, 5))
        fig.patch.set_facecolor("#2b2b2b")
        ax.set_facecolor("#2b2b2b")

        ax.plot(data, color="cyan", linestyle="-")
        ax.set_xlabel("Frame Count", color="white")
        ax.set_ylabel("Value", color="white")
        ax.set_title(
            f"Smoothness Graph ({(smoothness * smoothness / 100):.2f} units)",
            color="white",
        )

        ax.tick_params(axis="x", colors="white")
        ax.tick_params(axis="y", colors="white")
        ax.spines["bottom"].set_color("white")
        ax.spines["top"].set_color("white")
        ax.spines["left"].set_color("white")
        ax.spines["right"].set_color("white")

        for widget in root.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()

        toolbar = NavigationToolbar2Tk(canvas, root)
        toolbar.update()
        toolbar.config(background="#2e2e2e")
        canvas.get_tk_widget().pack(fill=tk.BOTH)

    def generate_background_zoom_graph(self):
        data = self.mouse_event_processor.generate_zooming_values(
            self.zoom_smoothness_variable.get()
        )

        self.draw_line_graph(
            self.screen_zoom_visualizer_graph, data, self.zoom_smoothness_variable.get()
        )

    def generate_mouse_size_graph(self):
        data = self.mouse_event_processor.generate_mouse_size_values(
            self.scale_smoothness_variable.get()
        )

        self.draw_line_graph(
            self.mouse_size_visualizer_graph, data, self.scale_smoothness_variable.get()
        )

    def schedule_background_zoom_graph_update(self, _):
        if hasattr(self, "background_zoom_graph_update_id"):
            self.master.after_cancel(self.background_zoom_graph_update_id)
        self.background_zoom_graph_update_id = self.master.after(
            200, self.generate_background_zoom_graph
        )

    def schedule_mouse_size_graph_update(self, _):
        if hasattr(self, "mouse_size_graph_update_id"):
            self.master.after_cancel(self.mouse_size_graph_update_id)
        self.mouse_size_graph_update_id = self.master.after(
            200, self.generate_mouse_size_graph
        )
