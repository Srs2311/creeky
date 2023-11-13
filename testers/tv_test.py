import importlib.util
import sys
spec = importlib.util.spec_from_file_location("torrent_lister", "torrent_lister.py")
tl = importlib.util.module_from_spec(spec)
sys.modules["torrent_lister"] = tl
spec.loader.exec_module(tl)


torrentList = tl.get_popular_queue("tv",time="week")
#torrentList.filter_uploaders()
torrentList.filter_minimum_seeders(1000)
torrentList.filter_minimum_quality("1080p")
torrentList.get_tmbdb_data(category="tv")

for torrent in torrentList.torrents:
    print(torrentList.torrents.index(torrent))
    print(torrent.info["title"])
    print(f"Seeders: {torrent.info['seeders']}")
    print(torrent.info["size"])
    try:
        print(torrent.series_data["original_name"])
        print(torrent.series_data["overview"])
    except (TypeError, KeyError,AttributeError):
        print("No Series Data Found")
    try:
        print(torrent.episode_data["name"])
        print(torrent.episode_data["overview"])
    except(TypeError,KeyError,AttributeError):
        print("No Episode Data Found")
    print()
