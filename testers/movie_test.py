import importlib.util
import sys
spec = importlib.util.spec_from_file_location("torrent_lister", "torrent_lister.py")
tl = importlib.util.module_from_spec(spec)
sys.modules["torrent_lister"] = tl
spec.loader.exec_module(tl)




torrentList = tl.get_popular_queue("movies",time="week")
#torrentList.filter_uploaders()
torrentList.filter_minimum_seeders(1000)
torrentList.filter_minimum_quality("1080p")
torrentList.get_tmbdb_data()

for torrent in torrentList.torrents:
    print(torrent.info.get("title"))
    print(f"Seeders: {torrent.info['seeders']}")
    print(torrent.info.get("size"))
    try:
        print(torrent.data["original_title"])
        print(torrent.data["overview"])
    except AttributeError:
        print("No Data Found")
    print()
