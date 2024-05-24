from src.constants import (
    OREAL_DEFAULT_VIDEO_EXT,
    OREAL_MOUSE_EVENT_EXT,
    OREAL_BACKGROUNDS_DIR,
    OREAL_CURSOR_DIR,
    OREAL_WORKING_DIR,
)
import os
import moviepy.editor as mp
import pandas as pd
from tkinter import filedialog


# the make_video function will zoom and scale the video based on the mouse events
def make_video(background: str, cursor: str):
    background_complete_path = os.path.join(OREAL_BACKGROUNDS_DIR, background)
    cursor_complete_path = os.path.join(OREAL_CURSOR_DIR, cursor)

    # Open mouse events file from the working directory
    mouse_path = os.path.join(
        OREAL_WORKING_DIR,
        next(
            x
            for x in os.listdir(OREAL_WORKING_DIR)
            if x.endswith(OREAL_MOUSE_EVENT_EXT)
        ),
    )

    avi_path = os.path.join(
        OREAL_WORKING_DIR,
        next(
            x
            for x in os.listdir(OREAL_WORKING_DIR)
            if x.endswith(OREAL_DEFAULT_VIDEO_EXT)
        ),
    )

    # Load the background image
    background_image = mp.ImageClip(background_complete_path)

    # Load the cursor image
    cursor_image = mp.ImageClip(cursor_complete_path)

    # Load the mouse events
    mouse_events = pd.read_csv(mouse_path, delim_whitespace=True, header=None)

    # Load the video
    video = mp.VideoFileClip(avi_path)

    # Function to process each frame
    # Function to process each frame
    def process_frame(get_frame, t):
        frame = get_frame(t)
        current_time = int(t * video.fps)
        event = mouse_events[mouse_events[0] == current_time]

        if not event.empty:
            x, y, zoom, scale = (
                event.iloc[0, 1],
                event.iloc[0, 2],
                event.iloc[0, 4],
                event.iloc[0, 5],
            )

            # Get frame dimensions
            frame_height, frame_width, _ = frame.shape

            # Calculate the scaled dimensions
            scaled_width = int(frame_width * zoom)
            scaled_height = int(frame_height * zoom)

            # Resize the frame
            scaled_frame = mp.ImageClip(frame).resize((scaled_width, scaled_height))

            # Calculate the position for the scaled frame
            scaled_x = max(
                0, min(scaled_width - frame_width, int(x - scaled_width / 2))
            )
            scaled_y = max(
                0, min(scaled_height - frame_height, int(y - scaled_height / 2))
            )

            # Overlay the cursor on the scaled frame
            scaled_cursor = cursor_image.resize(scale)
            cursor_x = x - scaled_x
            cursor_y = y - scaled_y
            scaled_frame_with_cursor = mp.CompositeVideoClip(
                [scaled_frame, scaled_cursor.set_position((cursor_x, cursor_y))]
            )

            scaled_frame_with_cursor = scaled_frame_with_cursor.set_position(
                (
                    background_image.size[0] / 2 - scaled_frame_with_cursor.size[0] / 2,
                    background_image.size[1] / 2 - scaled_frame_with_cursor.size[1] / 2,
                )
            )
            # Overlay the scaled frame on the background (centered)
            final_frame = mp.CompositeVideoClip(
                [
                    background_image.set_duration(video.duration),
                    mp.ImageClip(scaled_frame_with_cursor.get_frame(t)),
                ]
            ).get_frame(t)

        else:
            # If no event, return the original frame
            final_frame = frame

        return final_frame

    # Apply the processing function to the video
    processed_video = video.fl(process_frame)

    # Ask the user where to save the output using filedialog
    output_path = filedialog.asksaveasfilename(
        title="Save Video As",
        defaultextension=".mp4",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")],
    )

    if output_path:
        # Combine the processed video with the background
        # center the video on the background
        processed_video = processed_video.set_position(
            (
                background_image.size[0] / 2 - processed_video.size[0] / 2,
                background_image.size[1] / 2 - processed_video.size[1] / 2,
            )
        )
        final_video = mp.CompositeVideoClip(
            [background_image.set_duration(video.duration), processed_video]
        )
        final_video.write_videofile(output_path, codec="libx264")
