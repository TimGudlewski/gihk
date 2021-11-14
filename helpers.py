import json, re, os, inspect, wget
from requests import HTTPError
from urllib.error import URLError
from PIL import ImageGrab
anchor = r'\Z'

gihk_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


class RecordEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


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


def read_json_file(path: str):
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def write_json_file(output_file: str, data):
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, cls=RecordEncoder)


def get_year_re(line: str, as_line=True):
    ex = r'\d{4,4}'
    if as_line:
        return re.match(ex + anchor, line)
    else:
        return re.search(ex, line)