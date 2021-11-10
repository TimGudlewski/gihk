import time, os, pyperclip, helpers, wget, random, pytesseract
from ahk import AHK
from requests import HTTPError
from urllib.error import URLError
from PIL import ImageGrab

ahk = AHK()
image_types = {'main': "\"poster\"", 'scene': "\"scene\" -youtube -poster"}
bad_sources = ['shutterstock', 'alamy', 'agefotostock', 'gettyimages', 'granger']
images_dir = os.path.join(helpers.gihk_dir, 'images')


def get_filename(img_url, dir_name):
    try:
        return wget.download(img_url, out=f'images\\{dir_name}\\')
    except (HTTPError, URLError) as _:
        pass


def get_clipimg():
    try:
        return ImageGrab.grabclipboard()
    except OSError:
        pass


class FilmRecord:
    def __init__(self, title=None, year=None, query=None) -> None:
        if query:
            year_re = helpers.get_year_re(query[-4:])
            if year_re:
                year = year_re.group()
                title = query[:-4].strip()
        self.title = title
        self.year = year
        self.images = []


    def get_query(self, image_type) -> str:
        return f"{self.title} {self.year} film {image_types[image_type]}"


class ImageRecord:
    def __init__(self, imgtype, url, imgpath, text, conf) -> None:
        self.imgtype = imgtype
        self.url = url
        self.imgpath = imgpath
        self.text = text
        self.conf = conf
    

    def check_sums(self):
        sum_text = sum(1 for t in self.text if t)
        sum_conf = sum(1 for c in self.conf if float(c) > 95)
        return sum_text > 0 and sum_conf > 0


class Collector:
    def __init__(self, queries=None, queries_range=None, rand=False):
        self.films = []
        if queries:
            for i in range(queries_range or len(queries)):
                self.films.append(FilmRecord(query=queries[i]))
        else:
            file_path = os.path.join(helpers.gihk_dir, 'films_artblog.json')
            file_films = helpers.read_json_file(file_path)
            indices_used = []
            for i in range(queries_range or len(file_films)):
                if rand:
                    file_film_idx = random.choice(range(len(file_films)))
                    while file_film_idx in indices_used:
                        file_film_idx = random.choice(range(len(file_films)))
                    indices_used.append(file_film_idx)
                else:
                    file_film_idx = i
                self.films.append(FilmRecord(title=file_films[file_film_idx]['name'], year=file_films[file_film_idx]['year']))


    def save_images(self, alt_map=None):
        for x, film in enumerate(self.films):
            output_dirname = film.title.replace(' ', '_')
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

                ahk.type(film.get_query(it))
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
                saved_images_counter = 0
                while True:
                    ahk.key_press('AppsKey')
                    time.sleep(1)
                    for i in range(4):
                        ahk.key_press('Up')
                    ahk.key_press('Enter')
                    time.sleep(0.5)
                    imgurl = pyperclip.paste()
                    print(film.title, imgurl)
                    if not imgurl.startswith('data'):
                        if not any(bad_source in imgurl for bad_source in bad_sources):
                            filename = get_filename(imgurl, output_dirname)
                            if filename:
                                saved_images_counter += 1
                                imgpath = os.path.join(output_dir, f'{it + str(saved_images_counter)}.jpg')
                                ahk.key_press('AppsKey')
                                time.sleep(1)
                                for k in range(5):
                                    ahk.key_press('Up')
                                ahk.key_press('Enter')
                                clipimg = None
                                clipimg_tries = 0
                                while not clipimg and clipimg_tries < 5:
                                    clipimg_tries += 1
                                    time.sleep(clipimg_tries)
                                    clipimg = get_clipimg()
                                imgdata = {}
                                if clipimg:
                                    imgdata.update(pytesseract.image_to_data(clipimg, output_type=pytesseract.Output.DICT))
                                image = ImageRecord(it, imgurl, imgpath, imgdata.get('text'), imgdata.get('conf'))
                                film.images.append(image)
                                os.replace(filename, imgpath)
                                if not (it == 'scene' and image.check_sums()):
                                    break
                        ahk.key_press('Right')
                    time.sleep(0.5)  # For some reason, if you keep copying the image address, eventually it gives you the unmasked version that doesn't start with 'data'.
                win.kill()
                time.sleep(0.5)
                pyperclip.copy('')


    def save_collection(self):
        file_path = os.path.join(helpers.gihk_dir, 'collection.json')
        helpers.write_json_file(file_path, self.films)


test_queries = ["T-Men 1947"]
test_collector = Collector(queries_range=7, rand=True)
test_alt_map = {'0,1': 2}
test_collector.save_images()
test_collector.save_collection()
