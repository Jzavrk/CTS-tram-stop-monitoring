"""
Animations sur écran lcd 16x2.
"""

waves = [ [ 0x03, 0x04, 0x08, 0x10, 0x00, 0x00, 0x00, 0x00 ],
        [ 0x18, 0x04, 0x02, 0x01, 0x00, 0x00, 0x00, 0x00 ],
        [ 0x00, 0x00, 0x00, 0x00, 0x10, 0x08, 0x04, 0x03 ],
        [ 0x00, 0x00, 0x00, 0x00, 0x01, 0x02, 0x04, 0x18 ]
    ]

static_dinosaure = [ [ 0x00, 0x00, 0x00, 0x00, 0x10, 0x18, 0x1C, 0x1F ],
        [ 0x00, 0x01, 0x01, 0x01, 0x01, 0x03, 0x0F, 0x1F ],
        [ 0x1F, 0x17, 0x1F, 0x1F, 0x1C, 0x1F, 0x1C, 0x1C ],
        [ 0x10, 0x18, 0x18, 0x18, 0x00, 0x10, 0x00, 0x00 ],
        [ 0x1F, 0x0F, 0x07, 0x03, 0x03, 0x03, 0x02, 0x03 ],  # Patte gauche
        [ 0x1F, 0x1F, 0x1F, 0x1F, 0x17, 0x03, 0x02, 0x03 ],  # Patte droite
        [ 0x1F, 0x19, 0x10, 0x00, 0x00, 0x00, 0x00, 0x00, ]
    ]

dinosaure_left_foot = [
        [ 0x1F, 0x0F, 0x07, 0x03, 0x02, 0x03, 0x00, 0x00 ],
        [ 0x1F, 0x0F, 0x07, 0x03, 0x03, 0x03, 0x02, 0x03 ],
    ]

dinosaure_right_foot = [
        [ 0x1F, 0x1F, 0x1F, 0x07, 0x03, 0x02, 0x03, 0x00 ],
        [ 0x1F, 0x1F, 0x1F, 0x1F, 0x16, 0x03, 0x00, 0x00 ]
    ]

class DinoAnimation:

    def __init__(self, display) -> None:
        self.display = display
        self.frame_index = 0
        self.cur_position = 0
        self.MAX_COL_POSITION = 20
        display.load_custom_chars(static_dinosaure)

    def __iter__(self):
        return self

    def __next__(self):
        if self.cur_position == self.MAX_COL_POSITION:
            self.display.entry_mode_set(cursor_inc=True)
            self.cur_position = 0
            raise StopIteration

        self.display.entry_mode_set(cursor_inc=False)
        self._step()
        self._draw_cells()
        self.display.entry_mode_set(cursor_inc=True)
        self.cur_position += 1

    def _step(self) -> None:
        self.display.entry_mode_set(cursor_inc=True)
        self.display.load_single_custom_char(4, dinosaure_left_foot[self.frame_index])
        self.display.load_single_custom_char(5, dinosaure_right_foot[self.frame_index])
        self.display.entry_mode_set(cursor_inc=False)
        self.frame_index ^= 1

    def _draw_cells(self):
        self.display.set_cursor_at(self.cur_position)
        for i in range(3, -1, -1):
            self.display.write_char(i)

        self.display.write_char(ord(' '))

        self.display.set_cursor_at(0x40 + self.cur_position - 1)
        for i in range(6, 3, -1):
            self.display.write_char(i)

        self.display.write_char(ord(' '))

