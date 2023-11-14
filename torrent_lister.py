import requests
from bs4 import BeautifulSoup
import re
from dotenv import load_dotenv
import os
import json

load_dotenv()
env = dict(os.environ)
TMDB_API_key = env["TMDBAPI"]

headers = {
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'accept-language': 'en-US,en;q=0.5',
        'upgrade-insecure-requests': '1',
        'te': 'trailers'
        }

TMDBheaders = {
    "accept": "application/json",
    "Authorization": f"Bearer {TMDB_API_key}"
}

class Torrent:
    def __init__(self,torrent) -> None:
        torrent_info = {}
        link = torrent.select('.name')[0]
        link = link.find_all('a')
        link = link[1].get("href")
        torrent_info['title'] = torrent.select('.name')[0].get_text()
        torrent_info['link'] = link
        torrent_info['seeders'] = int(torrent.select('.seeds')[0].get_text())
        torrent_info['leechers'] = torrent.select('.leeches')[0].get_text()
        torrent_info['size'] = torrent.select('.size')[0].contents[0]
        torrent_info['uploader'] = torrent.select('.coll-5')[0].get_text()
        torrent_info['date'] = torrent.select('.coll-5')[0].get_text()
        torrent_info['url'] = "https://1337x.to"
        if re.search("[0-9]?[0-9][0-9][0-9]p",torrent_info["title"]):
                torrent_info["quality"] = (re.findall("[0-9]?[0-9][0-9][0-9]p",torrent_info["title"]))[0]
        else:
            torrent_info["quality"] = "Not In Title"
        self.info = torrent_info
    
    
    def get_data(self,category):
        if category == "movies":
            #Does some regex splitting to try and extract just the title of the movie from the torrent title
            query = self.info.get("title")
            query = query.replace(" ","+").lower()
            #first regex match, attempts to match against a release year. usually immidiately follows the movie title                #parenthesis are optional, and not match at the end keeps it from getting confused with the quality
            query = re.split("[(]?[0-9][0-9][0-9][0-9]",self.info.get("title"))
            
            release_year = re.findall("[(]?[0-9][0-9][0-9][0-9]^p",self.info.get("title"))
            #grabs the title from the previous regex split, and replaces periods with spaces for the api call to tmdb
            sanitized_movie_title = query[0].replace("."," ")                #provides release year to the query if available
            if release_year:
                req = requests.get(f"https://api.themoviedb.org/3/search/movie?query={sanitized_movie_title}&primary_release_year={release_year}", headers=TMDBheaders)
            else:
                req = requests.get(f"https://api.themoviedb.org/3/search/movie?query={sanitized_movie_title}", headers=TMDBheaders)
                #grabs the json from the tmdb call, and appends it to the individual torrent
                data = req.json()
                try:
                    self.data = data["results"][0]
                except IndexError: 
                    self.data = "No Data Found"

        elif category == "tv":
            torrent_title = (self.info["title"])
            #Regex search for release year, since this is generally the first value after the title
            if(re.search("[(]?[0-9][0-9][0-9][0-9][^p]",torrent_title)):
                tv_title = re.split("[(]?[0-9][0-9][0-9][0-9]",torrent_title)
                    
                #regex search for Season and Episode values, and removes them from the show title,this value is usually immidiately after the release year
                if(re.search("[(]?S[0-9][0-9]E?[0-9]?[0-9]?",tv_title[0])):
                    tv_title = re.split("[(]?S[0-9][0-9]E?[0-9]?[0-9]?",torrent_title)
            else:
                #regex split for season and episode values
                tv_title = re.split("[(]?S[0-9][0-9]E?[0-9]?[0-9]?",torrent_title)

            #regex search and split for the string "Season [0-9] in case season is formatted with season spelled out"
            if(re.search("(?i)Season[.]?[ ]?[0-9]",tv_title[0])):
                tv_title = re.split("(?i)Season[.]?[ ]?[0-9]",tv_title[0])
            
            sanitized_tv_title = tv_title[0].replace("."," ")
                
            #regex to check for Season information, stored in season_number variable
            if re.search("S[0-9][0-9]",torrent_title):
                season_number = re.findall("S[0-9][0-9]",torrent_title)
            elif re.search("(?i)Season[.]?[ ]?[0-9]",torrent_title):
                season_number = re.findall("(?i)Season[.]?[ ]?[0-9]",torrent_title)

            #regex to grab episode information, skips if not in title
            try:
                episode_number = re.findall("E[0-9][0-9]",torrent_title)
            except:
                pass
                
            #grabs series data
            req = requests.get(f"https://api.themoviedb.org/3/search/tv?query={sanitized_tv_title}", headers=TMDBheaders)
            series_data = req.json()
                
            #if series data is successfully retrieved, a request is made for the season or episode info, depending on what is provided in the title
            try:
                series_data = series_data.get("results")[0]
            except  IndexError:
                pass
            else:
                self.series_data = (series_data)    
                #checking to see if a series number and an episode number was provided to determine if we need to search for a specific episode or a whole season
                if season_number and episode_number:
                    season_number = season_number[0]
                    season_number = season_number.lower()
                    if season_number.__contains__("season"):
                        season_number.strip()
                        season_number = season_number.strip("season")
                    elif season_number.__contains__("s"):
                        season_number = season_number.strip("s")

                    #strips the e off of the episode number
                    episode_number = episode_number[0][1:]

                        #checks if the season number starts with a 0 and removes it if it does
                    if season_number[0] == "0":
                        season_number = season_number[1:]
                        #same for episode number
                    if episode_number[0] == "0":
                        episode_number = episode_number[1:]
                            
                        
                    req = requests.get(f"https://api.themoviedb.org/3/tv/{series_data['id']}/season/{season_number}/episode/{episode_number}", headers=TMDBheaders)
                    episode_data = req.json()
                    season_data = req.json()
                    self.episode_data = (episode_data)
                    
                elif season_number:
                    season_number = season_number[0]             
                    if season_number.lower().__contains__("season"):
                        season_number = season_number.lower().strip("season")
                    elif season_number.lower().__contains__("s"):
                        season_number = season_number.lower().strip("s")
                        
                    if season_number[0] == "0":
                        season_number = season_number[1:]
                        req = requests.get(f"https://api.themoviedb.org/3/tv/{series_data['id']}/season/{season_number}", headers=TMDBheaders)
                    season_data = req.json()
                    self.season_data = (season_data)
                    
        elif category == "xxx" or category == "xxx-week":
            data = {}
            #regex to split torrent title up based on spacing in torrent title
            torrent_info = re.split("[ |.|-]", self.info["title"])

            #first block is almost always the studio name. may need to look into a way to verify these against a source to help pick out incorrect matches
            studio = torrent_info[0]
            
            #grabs performers based on typical title pattern, if there is an "and" after the first performer it checks for a second
            performers = []
            performers.append(f"{torrent_info[4]} {torrent_info[5]}")
            if torrent_info[6].lower() == "and":
                performers.append(f"{torrent_info[7]} {torrent_info[8]}")
            
            
            #gets title of video from torrent title
            if re.search("[0-9]?[0-9][0-9][0-9]p",self.info["title"].lower()):
                title = re.split("[0-9]?[0-9][0-9][0-9]p",self.info["title"].lower())
            else:
                title = re.split("xxx",self.info["title"].lower())
            
            #title = re.split("[0-9][0-9][ |.][0-9][0-9][ |.][0-9][0-9]",title[0])
            try:
                title[1] = title[0].replace(".", " ")
                data["title"] = title[1].title().strip()
            except IndexError:
                data["title"] = "Not in torrent title"
            data["studio"] = studio
            data["performers"] = performers
            self.category = category
            self.data = data
            
    
class TorrentList:
    """Class to create lists of torrents based on a query"""
    def __init__(self,url:str) -> None:
        """Webscrapes site and then passes a list of torrent info to self.torrents"""
        #web scrapes and pulls all the tr elements, which are the individual torrents. then grabs all the info provided in the normal torrent menu
        req = requests.get(url,headers=headers)
        soup = BeautifulSoup(req.text, 'html.parser')
        self.torrents = []
        for torrent in soup.select('tr')[1:]:
            #gets the link to the torrent by selecting the link on the torrent name, and grabbing the href value
            new_torrent = Torrent(torrent)
            self.torrents.append(new_torrent)

    def filter_uploaders(self):
        """Removes torrents from self.torrents if not uploaded by a trusted uploader"""
        #opens the trusted uploaders file, and creates a list of the uploaders on the list
        #if the file does not exist, it is created.
        try:
            with open("./filters/trustedUploaders.json", "r") as trusted_uploaders:
                trusted_uploaders = json.load(trusted_uploaders)
        except FileNotFoundError:
            with open("./filters/trustedUploaders.json", "w") as trusted_uploaders:
                pass  
        else:
            for uploader in trusted_uploaders:
                #removes empty uploaders since those will match anything
                if uploader.strip() == "":
                    trusted_uploaders.remove(uploader)
                    
        
        #creates empty list of torrents 
        trusted_torrents_list = []
        #only runs the check if there is any uploaders in the trusted uploaders list
        if len(trusted_uploaders) > 0:
            for torrent in self.torrents:
                if torrent.info["uploader"] in trusted_uploaders:
                    trusted_torrents_list.append(torrent)
        else:
            print("There are no trusted uploaders, try adding some")
        self.torrents = trusted_torrents_list
    
    def filter_tracked_items(self,file:str):
        """Filters self.torrents based on a list of items in a provided file, Matches against the torrent title."""
        try: 
            with open(file, "r") as items:
                item_list = json.load(items)
        except FileNotFoundError:
            with open(file, "w") as items:
                pass      
        else:
            filtered_torrent_list = []
            for torrent in self.torrents: 
                for item in item_list:
                    #makes sure the item is not empty first
                    if item.strip() != "":
                        #then converts both the item and the torrent title to the same naming scheme, converting everything to lower, and replacing spaces with periods
                        #if there is a match in the torrent title, the item is added to the new torrent list
                        item = item.replace(" ",".")
                        if torrent.info["title"].lower().replace(" ",".").__contains__(item.lower().replace(" ",".")):
                            filtered_torrent_list.append(torrent)
            self.torrents = filtered_torrent_list

    def filter_minimum_seeders(self,min:int):
        """Checks the seeders on a torrent list, and removes if it is below a certain value"""
        new_list = []
        for torrent in self.torrents:

            if int(torrent.info["seeders"]) > int(min):
                new_list.append(torrent)
        self.torrents = new_list

    def filter_minimum_quality(self,min:str):
        """Checks the quality of a torrent and removes it if it is below a certain value"""
        #converts min quality from a string, to a properly formated int
        min = min.strip("p")
        min = int(min)
        new_list = []
        for torrent in self.torrents:
            #then converts the torrent quality to a properly formated int
            try:
                torrent_quality = int(torrent.info["quality"].strip("p"))
            #if the torrent quality is not found, it is set to 0
            except ValueError:
                torrent_quality = 0
            #then if the torrent meets the quality requirements, it is added to the new torrent list
            else:    
                if torrent_quality >= min:
                    new_list.append(torrent)
            self.torrents = new_list
    
class MovieTVTorrentList(TorrentList):
    """Torrent List For Movie and TV Section"""
    def __init__(self,url:str) -> None:
        super().__init__(url)
    
    def get_data(self,category:str="movies"):
        """Calls to TMDB to get torrent data"""
        for torrent in self.torrents:
            torrent.get_data(category=category)

class AnimeTorrentList(TorrentList):
    """Torrent List for Anime Section"""
    def __init__(self,url) -> None:
        super().__init__(url)

class XXXTorrentList(TorrentList):
    """Torrent List for xxx Section"""
    def __init__(self,url) -> None:
        super().__init__(url)

    def get_data(self):
        for torrent in self.torrents:
            torrent.get_data(category="xxx")
        
def generate_search_url(query,sort="seeders/desc",tpage:int=1,baseurl="https://1337x.to/"):
    """Generates a properly formated search URL"""
    query = query.replace(" ","+").lower()
    url = f"{baseurl}sort-search/{query}/{sort}/{tpage}/"

    return url

def get_magnet(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    anchors = soup.find_all('a')
    magnet = anchors[30].get('href')
    return magnet


def get_popular_queue(queue,time:str="day"):
    """Makes an object based from a popular queue"""
    #base 1337x url for the popular queues
    url = 'https://1337x.to/popular-'
    #allows for user to specify the popular-week queue or just the popular queue
    if time == "week":
        queue = f"{queue}-week"
    if queue == "xxx" or queue == "xxx-week":
        popularTorrents = XXXTorrentList(f"{url}{queue}")
    elif queue == "movies" or queue =="tv" or queue == "movies-week" or queue == "tv-week" or queue == "documentaries" or queue == "documentaires-week" \
        or  queue == "anime" or queue == "anime-week":
        popularTorrents = MovieTVTorrentList(f"{url}{queue}")
    elif queue == "games" or queue == "games-week" or queue == "music" or queue == "music-week" or queue == "apps" or queue == "apps-week" or queue == "other" or\
        queue == "other-week":
        popularTorrents = TorrentList(f"{url}{queue}")
    try:
        return popularTorrents
    except UnboundLocalError:
        return None

#filter management
#maybe move this to its own module
def add_to_filter(filter:str,item:str):
    with open(filter, "r") as item_list:
        items = json.load(item_list)
        if item not in items:
            items.append(item)
        with open(filter, "w") as item_list:
            item_list.write(json.dumps(items))

def remove_from_filter(filter:str,item:str):
    with open(filter, "r") as item_list:
        items = json.load(item_list)
        if item in items:
            items.remove(item)
        with open(filter, "w") as item_list:
            item_list.write(json.dumps(items))
            