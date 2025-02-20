
import time
import board
import json
import displayio
import terminalio
import digitalio
import adafruit_esp32spi.adafruit_esp32spi_socket as socket
import adafruit_esp32spi.adafruit_esp32spi_wsgiserver as server
import adafruit_requests as requests
from adafruit_matrixportal.matrixportal import MatrixPortal
from adafruit_wsgi.wsgi_app import WSGIApp

# Setup Default colors

red    = "0xff0000"
green  = "0x00f900"
blue   = "0x0433ff"
purple = "0x942192"
orange = "0xff9300"
yellow = "0xfffb00"
white  = "0xffffff"
black  = "0x000000"

# --- import Secrets for Wifi and such ---

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise

# -- Clear any previous display ---
displayio.release_displays()

# --- Display setup ---
matrixportal = MatrixPortal(status_neopixel=board.NEOPIXEL, debug=False, bit_depth=5)

# Display ID = 0  - Center of the Screen
matrixportal.add_text(
    text_font=terminalio.FONT, #"fonts/Arial-12.bdf", #
    text_position=((matrixportal.graphics.display.width // 2), (matrixportal.graphics.display.height // 2) - 1),
    text_scale=1,
    scrolling=False,
    text_anchor_point=(.5,.5) # This centers the text (approximately)

)

# Display ID = 1 - Center of the Screen for Scrolling
matrixportal.add_text(
    text_font=terminalio.FONT, #"fonts/Arial-12.bdf", #
    text_position=((matrixportal.graphics.display.width // 2), (matrixportal.graphics.display.height // 3) - 1),
    text_scale=1,
    scrolling=False,
    text_anchor_point=(.5,.5) # This centers the text (approximately)

)

# Display ID = 2 - Lower 1/3 of Screen w/ Scrolling
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

matrixportal.set_text_color(purple)
matrixportal.set_text("Connecting", 0)
esp = network._wifi.esp
esp.reset()
network.connect()


# --- Display IP Address and set ipaddr variable to IP address ---
ip = esp.ip_address
print('gateway ip: {}.{}.{}.{}'.format(ip[0],ip[1],ip[2],ip[3]))
ipaddr = ('{}.{}.{}.{}'.format(ip[0],ip[1],ip[2],ip[3]))
print(ipaddr)


def network():
    matrixportal.set_text(ipaddr)

def clear():
    matrixportal.set_text("")
    matrixportal.set_background(0)
    matrixportal.set_text_color(0x000000)
    matrixportal.set_text("", 1)
    matrixportal.set_background(0, 1)
    matrixportal.set_text_color(0x000000, 1)
    matrixportal.set_text("", 2)
    matrixportal.set_background(0, 2)
    matrixportal.set_text_color(0x000000, 2)
def load_image(bmp):
    matrixportal.set_background(bmp)

def load_text(msg, text_color="0x000000", bg="0x10BA08"):
    matrixportal.set_background(int(bg))
    matrixportal.set_text(msg, 0)
    matrixportal.set_text_color(int(text_color,16), 0)

def load_stext(msg, text_color="0x000000", bg="0x10BA08"):
    matrixportal.set_background(int(bg))
    matrixportal.set_text(msg, 2)
    matrixportal.set_text_color(int(text_color,16), 2)
#    matrixportal.scroll_text(SCROLL_DELAY)

def motion(msg):
    clear()
    matrixportal.set_background(int(black))
    matrixportal.set_text_color(int(purple,16), 1)
    matrixportal.set_text(msg, 1)
    matrixportal.set_text('Motion       Motion', 2)
    matrixportal.set_text_color(int(red,16), 2)
    matrixportal.scroll_text(SCROLL_DELAY)

# Setup Web URL
web_app = WSGIApp()

@web_app.route("/")
def simple_app(request):
 #   c = {billboard.cur: billboard.content[billboard.keys[billboard.cur]]}
    network()
    return ['200 OK', [], "json.dumps(c)"]

# Display Text sent to /text
#   --- Example ---  curl 10.0.15.39/text/"Front_Door_Motion"/"0xDA0202"/"0x000000"
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

# Scroll Text sent to /stext
#   --- Example ---  curl 10.0.15.39/stext/"Front_Door_Motion"/"0xDA0202"/"0x000000"
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

# Display Text with Red scrolling 'Motion' below
@web_app.route("/image/<text>")
def plain_text(request, image_name):  # pylint: disable=unused-argument
    image = 'images/' + image_name + '.bmp'
    print(image)
    load_image(image)
    return ("200 OK", [], "Load image")

@web_app.route("/test")
def plain_text(request):  # pylint: disable=unused-argument
#   load_text('In a \nMeeting', text_color=green, bg=red)
    matrixportal.set_background('images/rancher.bmp')
    return ("200 OK", [], "test")

# Display Text with Red scrolling 'Motion' below
@web_app.route("/motion/<text>")
def plain_text(request, text):  # pylint: disable=unused-argument
#   load_text('In a \nMeeting', text_color=green, bg=red)
    msg=text.replace('_', ' ')
    motion(msg)
    return ("200 OK", [], "Motion")

# Clears the forground and background for IDX 0
@web_app.route("/clear")
def plain_text(request):  # pylint: disable=unused-argument
# Display 0
    clear()
    return ("200 OK", [], "Cleared all Dispalys")
# Enter Meeting Mode
@web_app.route("/meeting")
def plain_text(request):  # pylint: disable=unused-argument
    load_text('In a \nMeeting', text_color='0x10BA08', bg='0')
    return ("200 OK", [], "In Meeting")

# Enter Rancher Mode
@web_app.route("/rancher")
def plain_text(request):  # pylint: disable=unused-argument
    clear()
    load_image('images/rancher.bmp')
    return ("200 OK", [], "Rancher")

# Enter Rancher Mode
@web_app.route("/on-air")
def plain_text(request):  # pylint: disable=unused-argument
    clear()
    load_image('images/on-air.bmp')
    return ("200 OK", [], "On Air")


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

matrixportal.set_text_color(blue)
matrixportal.set_text(ipaddr)


# Start the Webserver
server.set_interface(esp)
wsgiServer = server.WSGIServer(80, application=web_app)
wsgiServer.start()

#load_stext('Farking Hell', text_color=green, bg=red)
#matrixportal.scroll_text(.1)

while True:
    try:
        wsgiServer.update_poll()
    except (ValueError, RuntimeError) as e:
        print("Failed to update, retrying\n", e)
        continue
