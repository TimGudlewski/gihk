import time, os, pyperclip, helpers, wget, random, pytesseract
from ahk import AHK
from requests import HTTPError
from urllib.error import URLError
from PIL import Image, ImageGrab

ahk = AHK()
image_types = {'main': "\"poster\"", 'scene': "\"scene\" -youtube -poster"}
bad_sources = ['shutterstock', 'alamy', 'agefotostock', 'gettyimages', 'granger']
images_dir = os.path.join(helpers.gihk_dir, 'images')


def get_filename(img_url, dir_name):
    try:
        return wget.download(img_url, out=f'images\\{dir_name}\\')
    except (HTTPError, URLError) as _:
        pass


class Record:
    def __init__(self, title=None, year=None, query=None) -> None:
        if query:
            year_re = helpers.get_year_re(query[-4:])
            if year_re:
                year = year_re.group()
                title = query[:-4].strip()
        self.title = title
        self.year = year


    def get_query(self, image_type) -> str:
        return f"{self.title} {self.year} film {image_types[image_type]}"
    

    def set_image(self, image_type, image_url):
        setattr(self, image_type, image_url)


class Collector:
    def __init__(self, queries=None, queries_range=None, rand=False):
        self.records = []
        if queries:
            for i in range(queries_range or len(queries)):
                self.records.append(Record(query=queries[i]))
        else:
            file_path = os.path.join(helpers.gihk_dir, 'films_artblog.json')
            file_records = helpers.read_json_file(file_path)
            for i in range(queries_range or len(file_records)):
                if rand:
                    file_record = random.choice(file_records)
                else:
                    file_record = file_records[i]
                self.records.append(Record(title=file_record['name'], year=file_record['year']))


    def find_image_urls(self, alt_map=None):
        for x, record in enumerate(self.records):
            output_dirname = record.title.replace(' ', '_')
            output_dir = os.path.join(images_dir, output_dirname)
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
            for j, it in enumerate([*image_types]):
                ahk.run_script('Run Chrome')
                time.sleep(0.5)
                win = ahk.find_window(title=b'New Tab')
                win.activate()
                win.maximize()
                time.sleep(0.5)
                ahk.type("https://images.google.com/")
                ahk.key_press('Enter')
                time.sleep(1)

                if alt_map:
                    alt_first = alt_map.get(f'{x},{j}')
                else:
                    alt_first = None
                first_img = alt_first or 1

                ahk.type(record.get_query(it))
                ahk.key_press('Enter')
                time.sleep(3)
                ahk.mouse_move(0, 0, relative=False)
                time.sleep(0.5)
                for h in range(first_img):
                    ahk.key_press('Right')
                    time.sleep(0.5)
                time.sleep(0.5)
                ahk.key_press('Enter')
                time.sleep(1)

                while True:
                    ahk.key_press('AppsKey')
                    time.sleep(1)
                    for i in range(4):
                        ahk.key_press('Up')
                    ahk.key_press('Enter')
                    time.sleep(0.5)
                    image_url = pyperclip.paste()
                    if not image_url.startswith('data'):
                        if any(bad_source in image_url for bad_source in bad_sources):
                            ahk.key_press('Right')
                        else:
                            filename = get_filename(image_url, output_dirname)
                            if filename:
                                if it == 'scene':
                                    ahk.key_press('AppsKey')
                                    time.sleep(1)
                                    for k in range(5):
                                        ahk.key_press('Up')
                                    ahk.key_press('Enter')
                                    time.sleep(0.5)
                                    data = pytesseract.image_to_data(ImageGrab.grabclipboard(), output_type=pytesseract.Output.DICT)
                                    print(f'\nbegin {record.title} imgtxt:\n{data["text"]}\n{data["conf"]}\nend {record.title} imgtxt\n')
                                os.rename(filename, os.path.join(output_dir, f'{it}.jpg'))
                                break
                            else:
                                ahk.key_press('Right')
                    time.sleep(0.5)
                print(image_url)
                record.set_image(it, image_url)
                win.kill()
                time.sleep(0.5)
                pyperclip.copy('')


    def img_switch_experiment(self, alt_map=None):
        for x, record in enumerate(self.records):
            for j, it in enumerate([*image_types]):
                ahk.run_script('Run Chrome')
                time.sleep(0.5)
                win = ahk.find_window(title=b'New Tab')
                win.activate()
                win.maximize()
                time.sleep(0.5)
                ahk.type("https://images.google.com/")
                ahk.key_press('Enter')
                time.sleep(1)

                if alt_map:
                    alt_first = alt_map.get(f'{x},{j}')
                else:
                    alt_first = None
                first_img = alt_first or 1

                ahk.type(record.get_query(it))
                ahk.key_press('Enter')
                time.sleep(2)
                for h in range(first_img):
                    ahk.mouse_move(0, 0, relative=False)
                    ahk.key_press('Right')
                    time.sleep(2)
                ahk.key_press('Enter')
                time.sleep(1)
                win.kill()
    

    def tesseract_experiment(self):
        for record in self.records:
            output_dirname = record.title.replace(' ', '_')
            output_dir = os.path.join(images_dir, output_dirname)
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
            for it in [*image_types]:
                ahk.run_script('Run Chrome')
                time.sleep(0.5)
                win = ahk.find_window(title=b'New Tab')
                win.activate()
                win.maximize()
                time.sleep(0.5)
                ahk.type("https://images.google.com/")
                ahk.key_press('Enter')
                time.sleep(1)

                ahk.type(record.get_query(it))
                ahk.key_press('Enter')
                time.sleep(3)
                ahk.mouse_move(0, 0, relative=False)
                time.sleep(0.5)
                ahk.key_press('Right')
                time.sleep(1)
                ahk.key_press('Enter')
                time.sleep(1)

                while True:
                    ahk.key_press('AppsKey')
                    time.sleep(1)
                    for i in range(4):
                        ahk.key_press('Up')
                    ahk.key_press('Enter')
                    time.sleep(0.5)
                    image_url = pyperclip.paste()
                    if not image_url.startswith('data'):
                        if any(bad_source in image_url for bad_source in bad_sources):
                            ahk.key_press('Right')
                        else:
                            filename = get_filename(image_url, output_dirname)
                            if filename:
                                if it == 'scene':
                                    ahk.key_press('AppsKey')
                                    time.sleep(1)
                                    for k in range(5):
                                        ahk.key_press('Up')
                                    ahk.key_press('Enter')
                                    time.sleep(0.5)
                                    data = pytesseract.image_to_data(ImageGrab.grabclipboard(), output_type=pytesseract.Output.DICT)
                                    print(f'\nbegin {record.title} imgtxt:\n{data}\nend {record.title} imgtxt\n')
                                os.rename(filename, os.path.join(output_dir, f'{it}.jpg'))
                                break
                            else:
                                ahk.key_press('Right')
                    time.sleep(0.5)
                print(image_url)
                record.set_image(it, image_url)
                win.kill()
                time.sleep(0.5)
                pyperclip.copy('')


    def save_collection(self):
        file_path = os.path.join(helpers.gihk_dir, 'collection.json')
        helpers.write_json_file(file_path, self.records)


test_queries = ["I wake up screaming 1941", "Christmas Holiday 1944"]
test_collector = Collector(queries_range=7, rand=True)
test_alt_map = {'0,1': 2}
test_collector.find_image_urls()
test_collector.save_collection()
