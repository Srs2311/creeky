from torrent_lister import *

torrentList = get_popular_queue("movies",time="week")
#torrentList.filter_uploaders()
torrentList.filter_minimum_seeders(1000)
torrentList.filter_minimum_quality("1080p")
torrentList.get_tmbdb_data()

for torrent in torrentList.torrents:
    print(torrent.get("title"))
    print(f"Seeders: {torrent['seeders']}")
    print(torrent.get("size"))
    try:
        print(torrent.get("data")["original_title"])
        print(torrent["data"]["overview"])
    except TypeError:
        print("No Data Found")
    print()
