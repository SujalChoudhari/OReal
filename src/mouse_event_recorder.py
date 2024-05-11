from pynput import mouse
from src.constants import OREAL_MOUSE_EVENT_EXT

class MouseEventRecorder:
    def __init__(self):
        self.mouse_positions = []  # modified by screen_recorder
        self.click_events = []  # should be modified by self.

        mouse_listener = mouse.Listener(
            on_click=self.on_click,
            on_move=self.on_move,
        )
        mouse_listener.start()

        self.__current_unprocessed_event = {
            "pos": (-1, -1),
            "click": False,
        }

    def on_move(self, x, y):
        self.__current_unprocessed_event = {
            "pos": (x, y),
            "click": (
                self.__current_unprocessed_event.get("click", False)
                if self.__current_unprocessed_event
                else False
            ),
        }

    def on_click(self, x, y, button, pressed):
        if pressed:
            self.__current_unprocessed_event = {
                "pos": (x, y),
                "click": True,
            }

    def process_event_for_current_frame(self):
        if self.__current_unprocessed_event is None:
            return
        self.mouse_positions.append(self.__current_unprocessed_event["pos"])
        self.click_events.append(self.__current_unprocessed_event["click"])
        self.__current_unprocessed_event["click"] = False

    def dump_events(self,filename:str):
        # Dump mouse positions and events to a file
        filename = filename.split(".")[0] + "." + OREAL_MOUSE_EVENT_EXT
        num_frames = len(self.mouse_positions)
        assert num_frames == len(
            self.click_events
        ), "Mismatch between number of frames and events"
        with open(filename, "w") as f:
            for i in range(num_frames):
                f.write(
                    f"{i+1} {self.mouse_positions[i][0]} {self.mouse_positions[i][1]} {self.click_events[i]}\n"
                )
