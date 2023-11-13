import importlib.util
import sys
spec = importlib.util.spec_from_file_location("torrent_lister", "torrent_lister.py")
tl = importlib.util.module_from_spec(spec)
sys.modules["torrent_lister"] = tl
spec.loader.exec_module(tl)


torrentList = tl.get_popular_queue("xxx",time="week")
torrentList.filter_uploaders()
torrentList.filter_minimum_quality("480p")
torrentList.get_data()
#torrentList.filter_tracked_items("./filters/stars.txt")
for torrent in torrentList.torrents:
    print(torrent.info["title"])
    print(f"{torrent.info['uploader']} {torrent.info['size']}")
    print(torrent.info["seeders"])
    print(f"Studio: {torrent.data['studio']}")
    print("Performers:")
    for performer in torrent.data["performers"]:
        print(performer)
    print(f'Quality: {torrent.info["quality"]}')
    print()
    