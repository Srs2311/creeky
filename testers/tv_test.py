from torrent_lister import *

torrentList = get_popular_queue("tv",time="week")
#torrentList.filter_uploaders()
torrentList.filter_minimum_seeders(1000)
torrentList.filter_minimum_quality("1080p")
torrentList.get_tmbdb_data(category="tv")

for torrent in torrentList.torrents:
    print(torrentList.torrents.index(torrent))
    print(torrent["title"])
    print(f"Seeders: {torrent['seeders']}")
    print(torrent["size"])
    try:
        print(torrent["series_data"]["original_name"])
        print(torrent["series_data"]["overview"])
    except (TypeError, KeyError):
        print("No Series Data Found Found")
    try:
        print(torrent["data"]["name"])
        print(torrent["data"]["overview"])
    except(TypeError,KeyError):
        print("No Season/Episode Data Found")
    print()
