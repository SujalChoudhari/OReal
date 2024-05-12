from src.cursor_renderer import CursorRenderer
from src.mouse_event_recorder import MouseEventRecorder
from src.screen_recorder import ScreenRecorder
from src.encoder import Encoder
from src.gui.recorder import ScreenRecorderGUI
import threading
import customtkinter as ctk

OUT_DIR = "output/"

cursor_renderer = CursorRenderer("assets/cursor.png")
mouse_event_recorder = MouseEventRecorder()

# # compressor = Encoder(OUT_DIR + "new_file")
# # # compressor.encode()
# # compressor.decode()

master = ctk.CTk()
recorder = ScreenRecorderGUI(master, ScreenRecorder(CursorRenderer("assets/cursor.png"), MouseEventRecorder()))

master.mainloop()