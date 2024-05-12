import cv2
import pyautogui
import numpy as np
import pyaudio
import wave

from src.cursor_renderer import CursorRenderer
from src.mouse_event_recorder import MouseEventRecorder
from src.constants import OREAL_DEFAULT_VIDEO_EXT

class ScreenRecorder:
    def __init__(
        self,
        out_file_name: str,
        cursor_renderer: CursorRenderer,
        mouse_event_recorder: MouseEventRecorder,
        record_audio: bool = False
    ):
        self.cursor_renderer = cursor_renderer
        self.mouse_event_recorder = mouse_event_recorder
        self.screen_width, self.screen_height = pyautogui.size()
        self.output_file_name = out_file_name + "." + OREAL_DEFAULT_VIDEO_EXT
        self.fourcc = cv2.VideoWriter_fourcc(*"XVID")
        self.output_video = cv2.VideoWriter(
            self.output_file_name,
            self.fourcc,
            20.0,
            (self.screen_width, self.screen_height),
        )
        self.record_audio = record_audio
        self.audio_filename = out_file_name + ".wav"
        self.audio_frames = []

        if self.record_audio:
            self.audio = pyaudio.PyAudio()
            self.audio_stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
        else:
            self.audio = None
            self.audio_stream = None


        cv2.namedWindow("Recording", cv2.WINDOW_NORMAL)

    def record_screen(self):
        try:
            while True:
                screenshot = pyautogui.screenshot()
                frame = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                # Render cursor on the frame
                self.cursor_renderer.render_cursor(frame)
                # Write frame to video
                self.output_video.write(frame)
                self.mouse_event_recorder.process_event_for_current_frame()
                
                if self.record_audio:
                    audio_frame = self.audio_stream.read(1024)
                    self.audio_frames.append(audio_frame)

                # Resize and display frame
                cv2.resizeWindow("Recording", 640, 480)
                cv2.imshow("Recording", frame)
                # Break the loop if 'q' is pressed
                if cv2.waitKey(1) == ord("q"):
                    break
        finally:
            if self.record_audio:
                self.audio_stream.stop_stream()
                self.audio_stream.close()
                self.audio.terminate()

                wf = wave.open(self.audio_filename, 'wb')
                wf.setnchannels(1)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(44100)
                wf.writeframes(b''.join(self.audio_frames))
                wf.close()

            self.mouse_event_recorder.dump_events(filename=self.output_file_name)
            # Release video writer and close OpenCV windows
            self.output_video.release()
            cv2.destroyAllWindows()

    def get_record_audio(self):
        return self.record_audio

    def set_record_audio(self, record_audio: bool):
        self.record_audio = record_audio
        if self.record_audio:
            self.audio = pyaudio.PyAudio()
            self.audio_stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)
