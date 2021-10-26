import time
from ahk import AHK
import pyperclip

ahk = AHK()
image_types = ["", "\"scene\"  -youtube -poster"]


def prepare_window():
    ahk.run_script('Run Chrome')
    time.sleep(0.5)
    win = ahk.find_window(title=b'New Tab')
    win.activate()
    win.maximize()


def find_file_urls(image_queries):
    prepare_window()
    ahk.type("https://images.google.com/")
    ahk.key_press('Enter')
    time.sleep(1)
    for iq in image_queries:
        for it in image_types:
            search_string = iq + " film " + it
            ahk.type(search_string)
            ahk.key_press('Enter')
            time.sleep(2)
            ahk.click(62, 499, relative=False)
            time.sleep(1)
            ahk.right_click(1607, 371, relative=False)
            for i in range(4):
                ahk.key_press('Up')
            ahk.key_press('Enter')
            print(pyperclip.paste())
            ahk.click(271, 198, relative=False)
            time.sleep(2)
            ahk.run_script('Send {Shift down}{End}{Shift up}')
            time.sleep(0.5)


test_image_queries = ["Odd Man Out 1947", "T-Men 1947"]
find_file_urls(test_image_queries)
