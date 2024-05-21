import os
from src.constants import OREAL_MOUSE_EVENT_EXT, OREAL_WORKING_DIR


class MouseInputProcessor:

    MAX_ZOOM_AMOUNT = 2.0
    ZOOM_INCREMENTER = 0.1

    def get_mouse_event_file_contents(self):
        filename = [
            x
            for x in os.listdir(OREAL_WORKING_DIR)
            if x.endswith(OREAL_MOUSE_EVENT_EXT)
        ][0]

        with open(os.path.join(OREAL_WORKING_DIR, filename), "r") as f:
            return f.read()

    def parse_mouse_event_file(self):
        content = self.get_mouse_event_file_contents()

        lines = content.split("\n")
        parts = [x.strip().split(" ") for x in lines if len(x) > 0]
        return parts

    def clear_file(self):
        filename = [
            x
            for x in os.listdir(OREAL_WORKING_DIR)
            if x.endswith(OREAL_MOUSE_EVENT_EXT)
        ][0]

        with open(os.path.join(OREAL_WORKING_DIR, filename), "w") as f:
            return f.write("")

    def append_to_file(self, line: str):
        filename = [
            x
            for x in os.listdir(OREAL_WORKING_DIR)
            if x.endswith(OREAL_MOUSE_EVENT_EXT)
        ][0]

        with open(os.path.join(OREAL_WORKING_DIR, filename), "a") as f:
            return f.write(line)

    def process_mouse_events(self):
        parts = self.parse_mouse_event_file()
        self.process_zoom_level(parts)
        self.process_mouse_size(parts)

        self.clear_file()

        for line in parts:
            #                     Frame No   Mouse X   Mouse Y   Click  ScreenZoom  MouseZoom
            self.append_to_file(
                f"{line[0]} {line[1]} {line[2]} {line[3]} {line[4]} {line[5]}\n"
            )

    def process_zoom_level(self, parts):
        for i in range(0, len(parts)):
            if parts[i][3] == "True":
                parts[i].append(self.MAX_ZOOM_AMOUNT)
            else:
                parts[i].append(1)

        # Take running average of value at [4]
        n = 4
        for j in range(0, len(parts)):
            new_sum = 0
            for k in range(j - n, j + n + 1):
                new_sum += float(parts[k][4]) if k >= 0 and k < len(parts) else 1
                if k == j:
                    new_sum += 2 * float(parts[k][4])
            parts[j][4] = new_sum / (n * 2 + 1)

    def process_mouse_size(self, parts):
        # based on velocity of mouse the size of the cursor should be calcuated,
        # it can me at max be MaxZoomAmount times larger than the size of the cursor
        for i, line in enumerate(parts):
            velocity_x = float(line[1]) - (float(parts[i - 1][1]) if i > 0 else 0)
            velocity_y = float(line[2]) - (float(parts[i - 1][2]) if i > 0 else 0)
            velocity = (velocity_x**2 + velocity_y**2) ** 0.5
            # normalize the velocity btw 0 and 1
            if velocity > 0:
                velocity = 1 / velocity
            else:
                velocity = 0

            size = 1 + velocity * self.MAX_ZOOM_AMOUNT
            parts[i].append(size)

        n = 4
        for j in range(0, len(parts)):
            new_sum = 0
            for k in range(j - n, j + n + 1):
                new_sum += float(parts[k][5]) if k >= 0 and k < len(parts) else 1
                if k == j:
                    new_sum += 2 * float(parts[k][5])
            parts[j][5] = new_sum / (n * 2 + 1)
