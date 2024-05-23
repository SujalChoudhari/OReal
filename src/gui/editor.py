import tkinter as tk
import os
from PIL import Image
import customtkinter as ctk
from src.constants import (
    OREAL_WORKING_DIR,
    OREAL_RECORDINGS_DIR,
    OREAL_DEFAULT_THUMBNAIL_EXT,
)
from src.processors.encoder import Encoder
from src.processors.mouse_input_processor import MouseInputProcessor
import matplotlib
from matplotlib import pyplot as plt

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class VideoEditor:
    def __init__(self, master, current_vid_path: str):
        self.main = master
        self.master = ctk.CTkToplevel(self.main)
        self.master.title("Video Editor")
        self.master.geometry("1080x720")
        self.master.focus()

        # Paths to preset backgrounds and cursors
        self.backgrounds_dir = "assets/backgrounds"
        self.cursors_dir = "assets/cursors"
        self.background_previews_dir = "assets/background_previews"

        # Get preset backgrounds and cursors
        self.backgrounds = os.listdir(self.backgrounds_dir)
        self.cursors = os.listdir(self.cursors_dir)

        # Variables to store selected background and cursor
        self.selected_background = self.backgrounds[0]
        self.selected_cursor = self.cursors[0]
        self.zoom_smoothness_variable = tk.IntVar(value=0)
        self.scale_smoothness_variable = tk.IntVar(value=0)
        self.create_ui()

        # load the current video in working directory
        self.current_vid_path = current_vid_path
        # clear the working directory
        for f in os.listdir(OREAL_WORKING_DIR):
            os.remove(os.path.join(OREAL_WORKING_DIR, f))

        encoder = Encoder(
            OREAL_WORKING_DIR + current_vid_path,
            OREAL_RECORDINGS_DIR + current_vid_path,
        )
        encoder.decode()

        self.master.update()
        self.preview_image(is_background=True, preset=self.selected_background)
        self.preview_image(is_background=False, preset=self.selected_cursor)

    def create_ui(self):
        # App Name
        title_holder = ctk.CTkFrame(self.master)
        title_holder.pack(side=tk.TOP, fill=tk.X)
        ctk.CTkLabel(title_holder, text="Video Editor", font=("Arial", 14)).pack(
            side=tk.LEFT, padx=10, pady=10
        )

        # Preview Area
        self.center_preview_area = ctk.CTkTabview(self.master)
        self.center_preview_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.center_preview_area.add("Preview")
        self.center_preview_area.add("Mouse Size Visualizer")
        self.center_preview_area.add("Screen Zoom Visualizer")
        self.center_preview_area.add("Generate Video")

        # Make Button
        self.generate_vide_frame = ctk.CTkFrame(
            self.center_preview_area.tab("Generate Video")
        )
        self.generate_vide_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.make_btn = ctk.CTkButton(
            self.generate_vide_frame, text="Make", command=self.make_video
        )
        self.make_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        # Preview Frame
        self.preview_area = ctk.CTkFrame(self.center_preview_area.tab("Preview"))
        self.preview_area.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        self.preview_label = ctk.CTkLabel(self.preview_area, text="")
        self.preview_label.pack(expand=True, fill=tk.BOTH)

        # Mouse Size Visualizer Frame
        self.mouse_size_visualizer = ctk.CTkFrame(
            self.center_preview_area.tab("Mouse Size Visualizer")
        )
        self.mouse_size_visualizer.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.scale_smoothness_input = ctk.CTkSlider(
            self.mouse_size_visualizer,
            from_=1,
            to=100,
            number_of_steps=100,
            variable=self.scale_smoothness_variable,
        )
        self.scale_smoothness_input.pack(side=tk.TOP, padx=10, pady=10)
        self.mouse_size_visualizer_label = ctk.CTkLabel(
            self.mouse_size_visualizer, text="Click Make to preview"
        )
        self.mouse_size_visualizer_label.pack()

        self.mouse_size_visualizer_graph = ctk.CTkFrame(
            self.mouse_size_visualizer,
        )
        self.mouse_size_visualizer_graph.pack(expand=True, fill=tk.BOTH)

        # Screen Zoom Visualizer Frame
        self.screen_zoom_visualizer = ctk.CTkFrame(
            self.center_preview_area.tab("Screen Zoom Visualizer")
        )
        self.screen_zoom_visualizer.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)

        self.zoom_smoothness_input = ctk.CTkSlider(
            self.screen_zoom_visualizer,
            from_=1,
            to=100,
            number_of_steps=100,
            variable=self.zoom_smoothness_variable,
        )
        self.zoom_smoothness_input.pack(side=tk.TOP, padx=10, pady=10)

        self.screen_zoom_visualizer_label = ctk.CTkLabel(
            self.screen_zoom_visualizer, text="Click Make to preview"
        )
        self.screen_zoom_visualizer_label.pack()
        self.screen_zoom_visualizer_graph = ctk.CTkFrame(
            self.screen_zoom_visualizer,
        )
        self.screen_zoom_visualizer_graph.pack(expand=True, fill=tk.BOTH)

        # Sidebar - Preset Selector
        self.pallet = ctk.CTkTabview(self.master)
        self.pallet.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.pallet.add("Background")
        self.pallet.add("Cursor")

        self.create_preset_selector(
            self.background_previews_dir, "Background", self.backgrounds, True
        )
        self.create_preset_selector(self.cursors_dir, "Cursor", self.cursors, False)

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
            OREAL_WORKING_DIR
            + self.current_vid_path
            + "."
            + OREAL_DEFAULT_THUMBNAIL_EXT
        )

        # Resize video thumbnail while preserving aspect ratio
        vid_thumbnail = vid_thumbnail.resize(
            (
                int(new_background.size[0] * 0.8),
                int(new_background.size[0] * 9 // 16 * 0.8),
            ),
        )

        # Scale the cursor to 1/5 of the background height
        cursor_height = new_background.size[1] // 4
        cursor_width = new_background.size[1] // 4
        new_cursor = new_cursor.resize(
            (cursor_width, cursor_height),
        )

        # Paste the thumbnail on the background (right in center)
        paste_position = (
            new_background.size[0] // 2 - vid_thumbnail.size[0] // 2,
            new_background.size[1] // 2 - vid_thumbnail.size[1] // 2,
        )
        new_background.paste(vid_thumbnail, paste_position)

        # Render cursor on image in bottom right corner with some padding
        cursor_position = (
            new_background.size[0] - new_cursor.size[0] - 150 * 16 // 9,
            new_background.size[1] - new_cursor.size[1] - 150,
        )
        new_background.paste(new_cursor, cursor_position, new_cursor)

        # Resize the background image to fit the preview label
        new_background = new_background.resize(
            (
                self.preview_label.winfo_height() * 16 // 9 // 2,
                self.preview_label.winfo_height() // 2,
            ),
        )

        # Display the updated background image
        display_image = ctk.CTkImage(
            light_image=new_background,
            size=(
                self.preview_label.winfo_width() * 0.8,
                self.preview_label.winfo_width() * 0.8 * 9 // 16,
            ),
        )
        self.preview_label.configure(image=display_image)

    def draw_line_graph(self, root: ctk.CTkFrame, data: list[float]):
        # Create a Matplotlib figure and axis
        fig, ax = plt.subplots(figsize=(4, 3))

        # Plot the line graph
        ax.plot(data, marker="o", color="blue", linestyle="-")

        # Set labels and title
        ax.set_xlabel("Frame Count")
        ax.set_ylabel("Value")
        ax.set_title("Smoothness Graph")

        # remove all the childs of root before appending
        for widget in root.winfo_children():
            widget.destroy()
        # Create a Tkinter-compatible canvas
        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.draw()

        toolbar = NavigationToolbar2Tk(canvas, root)
        toolbar.update()
        canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)

    def make_video(self):
        (
            screen_zoom_array,
            mouse_zoom_array,
        ) = MouseInputProcessor().process_mouse_events(
            zoom_smoothness=self.zoom_smoothness_variable.get(),
            scale_smoothness=self.scale_smoothness_variable.get(),
        )
        self.draw_line_graph(self.mouse_size_visualizer_graph, mouse_zoom_array)
        self.draw_line_graph(self.screen_zoom_visualizer_graph, screen_zoom_array)
