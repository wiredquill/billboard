
import time
import board
import json
import displayio
import terminalio
import digitalio
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_esp32spi.adafruit_esp32spi_wsgiserver as server
import adafruit_requests as requests
import adafruit_minimqtt
from adafruit_matrixportal.matrixportal import MatrixPortal
from adafruit_wsgi.wsgi_app import WSGIApp

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

displayio.release_displays()

# --- Display setup ---
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=False, bit_depth=5)

# Display ID = 0
matrixportal.add_text(
    text_font=terminalio.FONT, #"fonts/Arial-12.bdf", #
    text_position=((matrixportal.graphics.display.width // 2), (matrixportal.graphics.display.height // 2) - 1),
    text_scale=1,
    scrolling=False,
    text_anchor_point=(.5,.5) # This centers the text (approximately)

)

# Display ID = 1
matrixportal.add_text(
    text_font=terminalio.FONT, #"fonts/Arial-12.bdf", #
    text_position=((matrixportal.graphics.display.width // 2), (matrixportal.graphics.display.height // 2) - 1),
    text_scale=1,
    scrolling=True,
    text_anchor_point=(.5,.5) # This centers the text (approximately)

)

# Learn guide title (ID = 2)
matrixportal.add_text(
    text_font=terminalio.FONT,
    text_position=(2, 25),
    text_color=0x000080,
    scrolling = True
)

# Delay for scrolling the text
SCROLL_DELAY = 0.1

# --- Network setup ---
network = matrixportal.network


esp = network._wifi.esp
esp.reset()
network.connect()
matrixportal.set_text("Connection...", 0)

# --- Display IP Address and set ipaddr variable to IP address ---
ip = esp.ip_address
print('gateway ip: {}.{}.{}.{}'.format(ip[0],ip[1],ip[2],ip[3]))
ipaddr = ('{}.{}.{}.{}'.format(ip[0],ip[1],ip[2],ip[3]))
print(ipaddr)

def meeting():
    matrixportal.set_text("Meeting")

def network():
    matrixportal.set_text(ipaddr)

def clear():
    matrixportal.set_text("")
    matrixportal.set_background(0)
    matrixportal.set_text_color(0x000000)

def load_image(self, bmp):
    matrixportal.set_background(bmp)

def load_text(self, msg, *, text_color="0x000000", bg="0x10BA08"):
    matrixportal.set_background(bg)
    matrixportal.set_text(msg, self.text_index)
    matrixportal.set_text_color(int(text_color,16), 0)

def load_stext(self, msg, *, text_color="0x000000", bg="0x10BA08"):
    matrixportal.set_background(bg)
    matrixportal.set_text(msg, self.stext_index)
    matrixportal.set_text_color(int(text_color,16), 1)

# Setup Web URL
web_app = WSGIApp()

@web_app.route("/")
def simple_app(request):
 #   c = {billboard.cur: billboard.content[billboard.keys[billboard.cur]]}
    return ['200 OK', [], "json.dumps(c)"]


@web_app.route("/text/<text>/<fg>/<bg>")
def plain_text(request, text, fg, bg):  # pylint: disable=unused-argument
    print("text received")
    c = parse_content(text,fg,bg)
    space_text=text.replace('_', ' ')
    print(text,fg,bg)
    matrixportal.set_background(int(bg))
    matrixportal.set_text(space_text)
    matrixportal.set_text_color(int(fg))
    return ("200 OK", ["POST"], json.dumps(c))

@web_app.route("/stext/<text>/<fg>/<bg>")
def plain_text(request, text, fg, bg):  # pylint: disable=unused-argument
    print("text received")
    c = parse_content(text,fg,bg)
    space_text=text.replace('_', ' ')
    print(text,fg,bg)
    matrixportal.set_background(int(bg))
    matrixportal.set_text(space_text)
    matrixportal.set_text_color(int(fg))
    matrixportal.set_text_scroll_rate = .1
    matrixportal.set_scrolling=True
    return ("200 OK", ["POST"], json.dumps(c))

@web_app.route("/test")
def plain_text(request):  # pylint: disable=unused-argument
    matrixportal.set_text("In a Meeting")
    return ("200 OK", [], "In Meeting")
    matrixportal.set_text_scroll_rate = .1
    matrixportal.set_scrolling=True
    return ("200 OK", [], "test")

@web_app.route("/clear")
def plain_text(request):  # pylint: disable=unused-argument
    matrixportal.set_background(0)
    matrixportal.set_text_color(0x000000)
    matrixportal.set_scrolling=False
    matrixportal.set_text("")
    return ("200 OK", [], "On Air")


@web_app.route("/meeting")
def plain_text(request):  # pylint: disable=unused-argument
    matrixportal.set_text("In a \nMeeting")
    return ("200 OK", [], "In Meeting")


def parse_content(text=None,fg=None,bg=None,*):
    if text is None or fg is None or bg is None:
        content = "{}"#default_content
    content = (
        '{' +
        '"text": "' + text + '", ' +
        '"fg": "' +   fg + '", ' +
        '"bg": "' +   bg +
        '"}')
    return json.loads(content)



# Display IP Address

#matrixportal.set_text_color('0x10BA08')
matrixportal.set_text(ipaddr)

# Start the Webserver
server.set_interface(esp)
wsgiServer = server.WSGIServer(80, application=web_app)
wsgiServer.start()


while True:
    try:
        wsgiServer.update_poll()
    except (ValueError, RuntimeError) as e:
        print("Failed to update, retrying\n", e)
        continue



