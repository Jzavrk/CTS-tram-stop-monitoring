"""
# Original code found at:
# https://gist.github.com/DenisFromHR/cc863375a6e19dce359d

# Made available under GNU GENERAL PUBLIC LICENSE

References:
    https://www.csus.edu/indiv/p/pangj/class/lcd/instruct.html
    http://www.microcontrollerboard.com/lcd.html
    https://www.circuitbasics.com/raspberry-pi-i2c-lcd-set-up-and-programming/

"""

from time import sleep
import smbus

# i2c bus (0 -- original Pi, 1 -- Rev 2 Pi)
DEVICE_BUS = 1

# LCD Address
DEVICE_ADDR = 0x3f

# commands
CLEARDISPLAY = 0x01         #0b00000001
RETURNHOME = 0x02           #0b0000001X
ENTRYMODESET = 0x04         #0b000001IS
DISPLAYCONTROL = 0x08       #0b00001DCB
CURSORSHIFT = 0x10          #0b0001SRXX
FUNCTIONSET = 0x20          #0b001DNFXX
SETCGRAMADDR = 0x40         #0b01XXXXXX # 6bit address
SETDDRAMADDR = 0x80         #0b1XXXXXXX # 7bit address

# flags for display entry mode
ENTRYINC = 0x02             #0b000000I0
ENTRYDEC = 0x00             #0b00000000
ENTRYMOVEOFF = 0x01         #0b0000000S
ENTRYMOVEON = 0x00          #0b00000000

# flags for display on/off control
DISPLAYON = 0x04            #0b00000D00
DISPLAYOFF = 0x00           #0b00000000
CURSORON = 0x02             #0b000000C0
CURSOROFF = 0x00            #0b00000000
BLINKON = 0x01              #0b0000000B
BLINKOFF = 0x00             #0b00000000

# flags for display/cursor shift
DISPLAYMOVE = 0x08          #0b0000S000
CURSORMOVE = 0x00           #0b00000000
MOVERIGHT = 0x04            #0b00000R00
MOVELEFT = 0x00             #0b00000000

# flags for function set
MODE8BIT = 0x10             #0b000D0000
MODE4BIT = 0x00             #0b00000000
MODE2LINE = 0x08            #0b0000N000
MODE1LINE = 0x00            #0b00000000
MODE5X10DOTS = 0x04         #0b00000F00
MODE5X8DOTS = 0x00          #0b00000000

# flags for backlight control
BACKLIGHT = 0x08            #0b00001000
NOBACKLIGHT = 0x00          #0b00000000

EN = 0b00000100 # Enable bit
RW = 0b00000010 # Read/Write bit
RS = 0b00000001 # Register select bit

class LiquidCrystalI2C:
    """LCD display coupled with an I2C module.

    Attributes:
        addr: I2C module address
        bus: I2C/smbus object using port
        bkl: state of backlight
        disp: state of display
        cusr: state of cursor
        blnk: state of blink
        curs_inc: state defining cursor behaviour
        disp_move: state defining input behaviour
    """

    def __init__(self, addr=DEVICE_ADDR, port=DEVICE_BUS):
        self.addr = addr
        self.bus = smbus.SMBus(port)
        self.bkl = True
        self.disp = True
        self.curs = False
        self.blnk = False
        self.curs_inc = True
        self.disp_move = False

        # Black magic initialization
        self.write_byte(BACKLIGHT)
        self.write_cmd(CLEARDISPLAY | RETURNHOME)
        self.write_cmd(RETURNHOME)

        self.write_cmd(FUNCTIONSET | MODE2LINE | MODE5X8DOTS | MODE4BIT)
        self.write_cmd(DISPLAYCONTROL | DISPLAYON)
        self.write_cmd(CLEARDISPLAY)
        self.write_cmd(ENTRYMODESET | ENTRYINC)
        sleep(0.2)

    def write_byte(self, data):
        """Write 8 bits of data to i2c module."""
        self.bus.write_byte(self.addr, data)
        sleep(0.0001)

    def write_nibble(self, data):
        """Input 4 bits to lcd."""
        self.write_byte(data | (BACKLIGHT if self.bkl else NOBACKLIGHT))
        self.strobe(data)

   # clocks EN to latch command
    def strobe(self, data):
        """Confirm data input to lcd."""
        self.write_byte(data | EN | (BACKLIGHT if self.bkl else NOBACKLIGHT))
        sleep(.0005)
        self.write_byte((data & ~EN) | (BACKLIGHT if self.bkl else NOBACKLIGHT))
        sleep(.0001)

    def write_cmd(self, cmd, flags=0x0):
        """Write a command to lcd."""
        self.write_nibble(flags | (cmd & 0xF0))
        self.write_nibble(flags | ((cmd << 4) & 0xF0))

    def write_char(self, charvalue, flags=RS):
        """Write a character to lcd.

        charvalue represents the numerical value of the given character
        obtained either manually or by the ord built-in function.
        Custom characters are called 0 through 7.
        """
        self.write_nibble(flags | (charvalue & 0xF0))
        self.write_nibble(flags | ((charvalue << 4) & 0xF0))

    def display_string(self, string, line=1, pos=0):
        """Put string function with optional char positioning."""
        if line == 1:
            pos_new = pos
        elif line == 2:
            pos_new = 0x40 + pos
        elif line == 3:
            pos_new = 0x14 + pos
        elif line == 4:
            pos_new = 0x54 + pos

        self.write_cmd(SETDDRAMADDR | pos_new)

        for char in string:
            self.write_char(ord(char))

    def set_cursor_at(self, new_pos):
        self.write_cmd(SETDDRAMADDR | new_pos)

    def clear(self):
        """Clear display and return home."""
        self.write_cmd(CLEARDISPLAY)

    def return_home(self):
        """Put cursor home and shift back display."""
        self.write_cmd(RETURNHOME)

    def move_cursor_right(self):
        self.write_cmd(CURSORSHIFT | CURSORMOVE | MOVERIGHT)

    def move_cursor_left(self):
        self.write_cmd(CURSORSHIFT | CURSORMOVE | MOVELEFT)

    def move_display_right(self):
        self.write_cmd(CURSORSHIFT | DISPLAYMOVE | MOVERIGHT)

    def move_display_left(self):
        self.write_cmd(CURSORSHIFT | DISPLAYMOVE | MOVELEFT)

    def display_control(self, display=None, cursor=None, blink=None):
        """Turn on/off display options.
        Arguments:
            display: bool, display characters or not
            cursor: bool, display cursor
            blink: bool, display blink cursor
        """
        if display is not None:
            self.disp = display
        if cursor is not None:
            self.curs = cursor
        if blink is not None:
            self.blnk = blink
        self.write_cmd(DISPLAYCONTROL
                | (DISPLAYON if self.disp else DISPLAYOFF)
                | (CURSORON if self.curs else CURSOROFF)
                | (BLINKON if self.blnk else BLINKOFF))

    def entry_mode_set(self, cursor_inc=None, display_move=None):
        """Control entry behaviour.
        Arguments:
            cursor_inc: bool, increment cursor after printing character
            display_move: bool, make display move instead of cursor
        """
        if cursor_inc is not None:
            self.curs_inc = cursor_inc
        if display_move is not None:
            self.disp_move = display_move
        self.write_cmd(ENTRYMODESET
                | (ENTRYINC if self.curs_inc else ENTRYDEC)
                | (ENTRYMOVEOFF if self.disp_move else ENTRYMOVEON))

    def backlight(self, state=None):
        """Control backlight."""
        if state is None:
            self.bkl = not self.bkl
        else:
            self.bkl = state
        self.write_byte(BACKLIGHT if self.bkl else NOBACKLIGHT)

    def load_custom_chars(self, fontdata):
        """Load custom characters to CGRAM (0 - 7).
        fontdata: 2 dimensional array

        Example:
            font = [[0b00000,
                     0b00100,
                     0b01110,
                     0b11111,
                     0b01110,
                     0b00100,
                     0b00000,
                     0b00000]]

            char printed with write_char(0)
        """
        self.write_cmd(SETCGRAMADDR | 0x0)
        for char in fontdata:
            for line in char:
                self.write_char(line)
