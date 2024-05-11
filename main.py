from src.cursor_renderer import CursorRenderer
from src.mouse_event_recorder import MouseEventRecorder
from src.screen_recorder import ScreenRecorder
from src.encoder import Encoder

OUT_DIR = "output/"

# cursor_renderer = CursorRenderer("assets/cursor.png")
# mouse_event_recorder = MouseEventRecorder()
# screen_recorder = ScreenRecorder(
#     OUT_DIR + "new_file", cursor_renderer, mouse_event_recorder
# )
# screen_recorder.record_screen()

compressor = Encoder(OUT_DIR + "new_file")
# compressor.encode()
compressor.decode()
