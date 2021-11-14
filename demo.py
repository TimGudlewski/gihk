import time
from datetime import timedelta
from core import Collector


def main(**kwargs):
    start_time = time.monotonic()
    collector = Collector(**kwargs)
    collector.save_images()
    collector.save_collection()
    end_time = time.monotonic()
    delta = timedelta(seconds=end_time - start_time)
    print(f'Program Execution Time for n={len(collector.films)}: {delta.total_seconds()} seconds')


queries = ["Rififi 1955"]
am_films = [('caged', 'scene'), ('la nuit du carrefour', 'scene')]
am = dict.fromkeys(am_films, 2)  # In case you want to skip the first 'scene' or 'main' image for certain films
main(queries_range=2, rand=True, alt_map=am)
