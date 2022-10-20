"""
Animations sur écran lcd 16x2.
"""
from time import sleep

waves = [
        [
        0x03,
        0x04,
        0x08,
        0x10,
        0x00,
        0x00,
        0x00,
        0x00
        ],
        [
        0x18,
        0x04,
        0x02,
        0x01,
        0x00,
        0x00,
        0x00,
        0x00
        ],
        [
        0x00,
        0x00,
        0x00,
        0x00,
        0x10,
        0x08,
        0x04,
        0x03
        ],
        [
        0x00,
        0x00,
        0x00,
        0x00,
        0x01,
        0x02,
        0x04,
        0x18
        ]
    ]

static_dinosaure = [
        [
        0x00,
        0x00,
        0x00,
        0x00,
        0x10,
        0x18,
        0x1C,
        0x1F
        ],
        [
        0x00,
        0x01,
        0x01,
        0x01,
        0x01,
        0x03,
        0x0F,
        0x1F
        ],
        [
        0x1F,
        0x17,
        0x1F,
        0x1F,
        0x1C,
        0x1F,
        0x1C,
        0x1C
        ],
        [
        0x10,
        0x18,
        0x18,
        0x18,
        0x00,
        0x10,
        0x00,
        0x00
        ],
        [   # Patte gauche
        0x1F,
        0x0F,
        0x07,
        0x03,
        0x03,
        0x03,
        0x02,
        0x03
        ],
        [   # Patte droite
        0x1F,
        0x1F,
        0x1F,
        0x1F,
        0x17,
        0x03,
        0x02,
        0x03
        ],
        [
        0x1F,
        0x19,
        0x10,
        0x00,
        0x00,
        0x00,
        0x00,
        0x00,
        ]
    ]

dinosaure_left_foot = [
        [
        0x1F,
        0x0F,
        0x07,
        0x03,
        0x02,
        0x03,
        0x00,
        0x00
        ],
        [
        0x1F,
        0x0F,
        0x07,
        0x03,
        0x03,
        0x03,
        0x02,
        0x03
        ],
    ]

dinosaure_right_foot = [
        [
        0x1F,
        0x1F,
        0x1F,
        0x17,
        0x03,
        0x02,
        0x03
        ],
        [
        0x1F,
        0x1F,
        0x1F,
        0x1F,
        0x16,
        0x03,
        0x00,
        0x00
        ]
    ]

class DinoAnimation:

    def __init__(self, display) -> None:
        self.display = display
        self.frame_index = 0
        self.column_position = 0
        self.MAX_COL_POSITION = 21

        display.load_custom_chars(static_dinosaure)

    def step(self) -> None:
        self.display.entry_mode_set(cursor_inc=True)
        self.display.load_single_custom_char(4, dinosaure_left_foot[self.frame_index])
        self.display.load_single_custom_char(5, dinosaure_right_foot[self.frame_index])
        self.display.entry_mode_set(cursor_inc=False)

        self.frame_index ^= 1
        self.column_position = (self.column_position + 1) % self.MAX_COL_POSITION

    def draw_cells(self):
        self.display.set_cursor_at(self.column_position + 4)
        for i in range(3, -1, -1):
            self.display.write_char(i)

        self.display.write_char(ord(' '))

        self.display.set_cursor_at(0x40 + self.column_position + 3)
        for i in range(6, 3, -1):
            self.display.write_char(i)

        self.display.write_char(ord(' '))

    def prepare(self):
        for i in range(5):
            self.display.move_display_left()

        self.display.entry_mode_set(cursor_inc=False)

    def play(self, delay):
        self.prepare()
        for i in range(self.MAX_COL_POSITION):
            self.step()
            self.draw_cells()
            sleep(delay)

        self.finish()

    def finish(self):
        self.display.entry_mode_set(cursor_inc=True)
        self.display.return_home()

