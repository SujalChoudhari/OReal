import cv2
import pyautogui
import numpy as np
import pyaudio
import wave
import threading
import tkinter as tk
import customtkinter as ctk
import queue
from PIL import Image

from src.cursor_renderer import CursorRenderer
from src.mouse_event_recorder import MouseEventRecorder
from src.constants import OREAL_DEFAULT_VIDEO_EXT


class ScreenRecorder:
    def __init__(
        self,
        cursor_renderer: CursorRenderer,
        mouse_event_recorder: MouseEventRecorder,
        max_preview_size=(400, 300),
    ):
        self.cursor_renderer = cursor_renderer
        self.mouse_event_recorder = mouse_event_recorder
        self.screen_width, self.screen_height = pyautogui.size()
        self.fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self.is_recording = False
        self.record_audio = False
        self.max_size = max_preview_size
        self.image_queue = queue.Queue()

    def setup(
        self,
        out_file_name: str,
        record_audio: bool = False,
        tk_frame: tk.Frame = None,
    ):
        self.output_file_name = out_file_name + "." + OREAL_DEFAULT_VIDEO_EXT
        self.output_video = cv2.VideoWriter(
            self.output_file_name,
            self.fourcc,
            20.0,
            (self.screen_width, self.screen_height),
        )
        self.record_audio = record_audio
        self.audio_filename = out_file_name + ".wav"
        self.is_recording = True
        self.tk_frame = tk_frame

        if self.record_audio:
            self.audio = pyaudio.PyAudio()
            self.audio_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024,
            )
        else:
            self.audio = None
            self.audio_stream = None

    def record_audio_thread(self):
        while self.is_recording and self.record_audio:
            audio_frame = self.audio_stream.read(1024)
            self.audio_frames.append(audio_frame)

    def stop_recording(self):
        self.is_recording = False

    def record(self):
        self.update_tkinter()
        if self.record_audio:
            self.audio_frames = []
            self.audio_stream.start_stream()
            audio_thread = threading.Thread(target=self.record_audio_thread)
            audio_thread.start()
        try:
            while self.is_recording:
                screenshot = pyautogui.screenshot()
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                self.cursor_renderer.render_cursor(frame)
                self.output_video.write(frame)
                self.mouse_event_recorder.process_event_for_current_frame()

                # Convert the OpenCV frame to PIL format
                pil_img = Image.fromarray(frame)
                width, height = pil_img.size
                ratio = min(self.max_size[0] / width, self.max_size[1] / height)
                new_width = int(width * ratio)
                new_height = int(height * ratio)
                pil_img = pil_img.resize((new_width, new_height), Image.BICUBIC)

                # Put the image into the queue
                self.image_queue.put(pil_img)

        finally:
            if self.record_audio:
                audio_thread.join()
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio.terminate()

                wf = wave.open(self.audio_filename, "wb")
                wf.setnchannels(1)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b"".join(self.audio_frames))
                wf.close()

            self.mouse_event_recorder.dump_events(filename=self.output_file_name)
            self.output_video.release()

    def update_tkinter(self):
        try:
            # Get an image from the queue
            pil_img = self.image_queue.get(block=False)
            # imgtk = ImageTk.PhotoImage(image=pil_img)

            # Update the tkinter frame with the new image
            ctkimage = ctk.CTkImage(light_image=pil_img, size=self.max_size)
            self.tk_frame.configure(image=ctkimage)
        except queue.Empty:
            pass

        # Schedule the next update after a short delay
        self.tk_frame.after(10, self.update_tkinter)

    def get_record_audio(self):
        return self.record_audio

    def set_record_audio(self, record_audio: bool):
        self.record_audio = record_audio
        if self.record_audio:
            self.audio = pyaudio.PyAudio()
            self.audio_stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024,
            )
