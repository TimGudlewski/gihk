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


def rightclick_menu(ups):
    ahk.key_press('AppsKey')
    time.sleep(1)
    for _ in range(ups):
        ahk.key_press('Up')
        time.sleep(0.2)
    ahk.key_press('Enter')
    time.sleep(0.5)


def load_chrome_get_win():
    ahk.run_script('Run Chrome')
    time.sleep(0.5)
    win = ahk.find_window(title=b'New Tab')
    win.activate()
    win.maximize()
    time.sleep(0.5)
    ahk.type("https://images.google.com/")
    ahk.key_press('Enter')
    time.sleep(1.5)
    win.activate()
    time.sleep(0.5)
    return win


def submit_query(query):
    ahk.type(query)
    ahk.key_press('Enter')
    time.sleep(3)
    ahk.mouse_move(0, 0, relative=False)
    time.sleep(0.5)


def select_first_img(img_pos):
    for _ in range(img_pos):
        ahk.key_press('Right')
        time.sleep(0.5)
    time.sleep(0.5)
    ahk.key_press('Enter')
    time.sleep(1)


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
    def __init__(self, width=None, height=None, imgtype=None, url=None, imgpath=None, text=None, conf=None) -> None:
        self.width = width
        self.height = height
        self.imgtype = imgtype
        self.url = url
        self.imgpath = imgpath
        self.text = text
        self.conf = conf
    

    def check_size(self):
        if self.width and self.height:
            a = self.width * self.height
            return a < 100000


    def check_sums(self):
        if self.text and self.conf:
            sum_text = sum(1 for t in self.text if t)
            sum_conf = sum(1 for c in self.conf if float(c) > 95)
            return sum_text > 0 and sum_conf > 0


class Collector:
    def __init__(self, queries=None, queries_range=0, rand=False, alt_map=None):
        self.films = []
        self.alt_map = alt_map
        self.qr = queries_range or 0  # In case None is passed in
        if queries:
            self.update_qr(len(queries))
            for i in range(self.qr):
                self.films.append(FilmRecord(query=queries[i]))
        else:
            file_path = os.path.join(helpers.gihk_dir, 'films_artblog.json')
            file_films = helpers.read_json_file(file_path)
            self.update_qr(len(file_films))
            indices = [i for i in range(self.qr)]
            if rand:
                random.shuffle(indices)
            for j in indices:
                self.films.append(FilmRecord(title=file_films[j]['name'], year=file_films[j]['year']))


    def update_qr(self, max_qr):
        if not self.qr or self.qr > max_qr:
            self.qr = max_qr


    def get_first_img(self, x, j):
        if self.alt_map:
            alt_first = self.alt_map.get(f'{x},{j}')
        else:
            alt_first = None
        return alt_first or 1


    def save_images(self):
        for x, film in enumerate(self.films):
            output_dirname = film.title.replace(' ', '_')
            output_dir = os.path.join(images_dir, output_dirname)
            if not os.path.exists(output_dir):
                os.mkdir(output_dir)
            for j, it in enumerate([*image_types]):
                first_img = self.get_first_img(x, j)
                win = load_chrome_get_win()
                submit_query(film.get_query(it))
                select_first_img(first_img)
                saved_images_counter = small_images = text_scenes = gf_fails = bs_fails = 0
                while True:
                    rightclick_menu(4)  # Copy img url
                    imgurl = pyperclip.paste()
                    if not imgurl.startswith('data'):
                        print(film.title, imgurl)
                        if not any(bad_source in imgurl for bad_source in bad_sources):
                            filename = get_filename(imgurl, output_dirname)  # Attempt to download image
                            if not filename:
                                gf_fails += 1
                                rightclick_menu(7)  # For some reason, opening the image in a new tab after the image download fails sometimes stops 403 errors occurring
                                time.sleep(1)
                                filename = get_filename(imgurl, output_dirname)  # Try one more time
                            if filename:
                                saved_images_counter += 1
                                rightclick_menu(5)  # Copy img
                                clipimg = None
                                clipimg_tries = 0
                                while not clipimg and clipimg_tries < 5:
                                    clipimg_tries += 1
                                    print(f'waiting {clipimg_tries} seconds before trying to access copied {it} image for {film.title}')
                                    time.sleep(clipimg_tries)
                                    clipimg = get_clipimg()
                                imgdata = {}
                                if clipimg:
                                    width, height = clipimg.size
                                    imgdata.update(w=width, h=height)
                                    imgdata.update(pytesseract.image_to_data(clipimg, output_type=pytesseract.Output.DICT))
                                image = ImageRecord(width=imgdata.get('w'), height=imgdata.get('h'), imgtype=it, url=imgurl, text=imgdata.get('text'), conf=imgdata.get('conf'))
                                new_filename = it + str(saved_images_counter)
                                if image.check_size():
                                    new_filename += '_small'
                                if image.check_sums():
                                    new_filename += '_text'
                                new_filename += '.jpg'
                                imgpath = os.path.join(output_dir, new_filename)
                                image.imgpath = imgpath
                                film.images.append(image)
                                os.replace(filename, imgpath)
                                if not (it == 'scene' and image.check_sums()) and not image.check_size():
                                    break
                                else:
                                    if not image.check_size():
                                        small_images += 1
                                        print(film.title, it, f'small images: {small_images}')
                                    if not (it == 'scene' and image.check_sums()):
                                        text_scenes += 1
                                        print(film.title, f'text scenes: {text_scenes}')
                            else:
                                gf_fails += 1
                                print(film.title, it, f'get_filename fails: {gf_fails}')
                        else:
                            bs_fails += 1
                            print(film.title, it, f'bad source fails: {bs_fails}')
                        ahk.key_press('Right')
                    else:
                        print(film.title, 'data:image')
                    time.sleep(0.5)  # For some reason, if you keep copying the image address, eventually it gives you the unmasked version that doesn't start with 'data'.
                win.kill()
                time.sleep(0.5)
                pyperclip.copy('')


    def save_collection(self):
        file_path = os.path.join(helpers.gihk_dir, 'collection.json')
        helpers.write_json_file(file_path, self.films)


test_queries = ["Rififi 1955"]
test_alt_map = {'0,1': 2}  # To skip La Nuit du Carrefour's nsfw first scene img
test_collector = Collector(queries_range=2, rand=True)
test_collector.save_images()
test_collector.save_collection()
