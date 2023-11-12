from torrent_lister import *


torrentList = get_popular_queue("xxx",time="week")
torrentList.filter_uploaders()
torrentList.filter_minimum_quality("480p")
torrentList.get_data()
#torrentList.filter_tracked_items("./filters/stars.txt")
for torrent in torrentList.torrents:
    print(torrent["title"])
    print(f'torrent title length: {len(torrent["title"])}')
    print(torrent["data"]["title"])
    print(f"{torrent['uploader']} {torrent['size']}")
    print(torrent["seeders"])
    print(f"Studio: {torrent['data']['studio']}")
    print("Performers:")
    for performer in torrent["data"]["performers"]:
        print(performer)
    print(f'Quality: {torrent["quality"]}')
    print()
    