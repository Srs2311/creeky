import curses
import curses.textpad
from curses import wrapper
import os
from dotenv import load_dotenv
import webbrowser
import qbittorrentapi
import torrent_lister as tl
import json

class TorrentDisplay():
    """Creates a list of pages with appropriately long lists of torrents based on screen size"""
    def __init__(self,category:str="movies",time:str="day",mode:str="popular",search_url:str = "") -> None:
        if mode == "popular":
            self.torrentList = tl.get_popular_queue(category,time)
            self.category = category
            self.mode = mode
        elif mode == "search":
            self.torrentList = tl.TorrentList(search_url)
            self.category = category
            self.mode = mode
    def pagination(self,stdscr):
        screensize = stdscr.getmaxyx()
        screen_length  = screensize[0]
        #screen_length = 10
        self.pages = []
        if len(self.torrentList.torrents) > screen_length-2:
                        
            for page_number in range(7):
                screen_start = page_number * (screen_length - 2)
                if len(self.torrentList.torrents[screen_start:]) < screen_length:
                    new_page = (self.torrentList.torrents[screen_start:])
                else:
                    screen_end = screen_start + screen_length - 2
                    new_page = self.torrentList.torrents[screen_start:screen_end]
                if new_page:
                    self.pages.append(new_page)
        elif len(self.torrentList.torrents) < screen_length -2:
            new_page = []
            for torrent in self.torrentList.torrents:
                new_page.append(torrent)
            self.pages.append(new_page)

    
    def display_page(self,stdscr,page_number:int=0,y=1,x=2):
        stdscr.clear()
        screensize = stdscr.getmaxyx()
        
        test = screensize[1] - 2
        max_title_length = int(screensize[1]/2)
        if max_title_length > 83:
            max_title_length = 83
        if self.mode == "popular":
            if self.category.lower() == "xxx" or self.category.lower() == "xxx-week":
                stdscr.addstr(0,int(screensize[1]/4),self.category.upper())
            else:
                stdscr.addstr(0,int(screensize[1]/4),self.category.title())
        elif self.mode == "search":
            stdscr.addstr(0,int(screensize[1]/4),self.mode.title())
        stdscr.addstr(screensize[0]-1,test,str(page_number))
        stdscr.addstr(0,int(max_title_length + 4),"|")
        stdscr.addstr(0,int(max_title_length + 5),"Uploader")
        stdscr.addstr(0,int(max_title_length + 14),"|")
        stdscr.addstr(0,int(max_title_length + 15),"Size")
        stdscr.addstr(0,int(max_title_length + 24),"|")
        stdscr.addstr(0,int(max_title_length + 25),"Seeds")
        stdscr.addstr(0,int(max_title_length + 29)," |")  
        stdscr.addstr(0,int(max_title_length + 31),"BWSR")
        stdscr.addstr(0,int(max_title_length + 35),"|")
        stdscr.addstr(0,int(max_title_length + 36),"DL")
        stdscr.addstr(0,int(max_title_length + 39),"|")
        stdscr.addstr(0,int(max_title_length + 40),"SMLR")
        try:
            print(self.pages[0])
        except AttributeError: 
            self.pagination(stdscr)
            self.display_page(stdscr,page_number)
            
        else:
            for torrent in self.pages[page_number]:
                torrent_index = self.pages[page_number].index(torrent)
                
                if len(torrent.info["title"]) > max_title_length:
                    torrent.info["title"] = torrent.info["title"][0:max_title_length]
                
                #menu start
                stdscr.addstr(torrent_index + 1,2,torrent.info["title"])
                stdscr.addstr(torrent_index + 1,(max_title_length + 4),"|")
                #writes the username in green if the user is in the trusted uploader json
                try:
                    with open("./filters/trustedUploaders.json", "r") as trusted_uploaders:
                        trusted_uploaders = json.load(trusted_uploaders)
                except FileNotFoundError:
                    with open("./filters/trustedUploaders.json", "w") as trusted_uploaders:
                        pass  
                else: 
                    if torrent.info["uploader"] in trusted_uploaders:
                        stdscr.addstr(torrent_index + 1,(max_title_length + 5),torrent.info["uploader"],curses.color_pair(1))
                    else:
                        stdscr.addstr(torrent_index + 1,(max_title_length + 5),torrent.info["uploader"])
                #Rest of the menu
                stdscr.addstr(torrent_index + 1,(max_title_length + 14),"|")
                stdscr.addstr(torrent_index + 1,(max_title_length + 15),torrent.info["size"])
                stdscr.addstr(torrent_index + 1,(max_title_length + 24),"|")
                stdscr.addstr(torrent_index + 1,(max_title_length + 25),str(torrent.info["seeders"]))
                stdscr.addstr(torrent_index + 1,(max_title_length + 30),"|")
                stdscr.addstr(torrent_index + 1,(max_title_length + 31),"[ ]")
                stdscr.addstr(torrent_index + 1,(max_title_length + 35),"|")
                stdscr.addstr(torrent_index + 1,(max_title_length + 36),"[ ] ")
                stdscr.addstr(torrent_index + 1,(max_title_length + 39),"|")
                stdscr.addstr(torrent_index + 1,(max_title_length + 40),"[ ]")
        stdscr.refresh()      
        while True:
            stdscr.move(y,x)
            stdscr.refresh()
            key = stdscr.getkey()
            if key == "KEY_UP":
                y-=1
            elif key == "KEY_DOWN":
                y+=1
            elif key == "KEY_RIGHT":
                if x == 2:
                    x = max_title_length + 5
                elif x == max_title_length + 5:
                    x = max_title_length + 32
                elif x == max_title_length + 32:
                    x = max_title_length + 37
                elif x == max_title_length + 37:
                    x = max_title_length + 41
            elif key == "KEY_LEFT":
                if x == max_title_length + 41:
                    x = max_title_length + 37
                elif x == max_title_length + 37:
                    x = max_title_length + 32
                elif x == max_title_length + 32:
                    x = max_title_length + 5
                elif x == max_title_length + 5:
                    x = 2
                    
            elif key == '\x1b':
                break
            elif key == " ":
                #open torrent page function
                if x == 2:
                    self.pages[page_number][y-1].get_data(category=self.category)
                    torrent_menu(stdscr,self.pages[page_number][(y-1)],category=self.category)
                    self.pagination(stdscr)
                    self.display_page(stdscr,page_number=page_number)
                    break 
                elif x == max_title_length + 5:
                    with open ("./filters/trustedUploaders.json","r") as trusted_uploaders:
                        trusted_uploaders = json.load(trusted_uploaders)
                    if self.pages[page_number][y-1].info["uploader"] not in trusted_uploaders:
                        tl.add_to_filter("./filters/trustedUploaders.json",self.pages[page_number][y-1].info["uploader"])
                        
                    elif self.pages[page_number][y-1].info["uploader"] in trusted_uploaders:
                        tl.remove_from_filter("./filters/trustedUploaders.json",self.pages[page_number][y-1].info["uploader"])
                    self.display_page(stdscr,page_number,y,x)
                    break
                #open in browser function    
                elif x == max_title_length + 32:
                    self.pages[page_number][y-1].get_data(category = self.category)
                    webbrowser.open(self.pages[page_number][y-1].info["url"] + self.pages[page_number][y-1].info["link"])
                #qbittorrent download function
                elif x == max_title_length + 37:
                    url = f"{self.pages[page_number][y-1].info['url']}{self.pages[page_number][y-1].info['link']}"
                    magnet = tl.get_magnet(url)
                
                    conn_info = dict(
                    host=os.getenv("QBITTORRENTHOST"),
                    port=os.getenv("QBITTORRENTPORT"),
                    username=os.getenv("QBITTORRENTUSER"),
                    password=os.getenv("QBITTORRENTPASS"),
                                )
                    qbt_client = qbittorrentapi.Client(**conn_info)
                    try:
                        qbt_client.auth_log_in()
                    except qbittorrentapi.LoginFailed as e:
                        print(e)
                    with qbittorrentapi.Client(**conn_info) as qbt_client:
                        if qbt_client.torrents_add(magnet) != "Ok.":
                            raise Exception("Failed to add torrent.")
                #similar torrents function
                elif x == max_title_length + 41:
                    self.pages[page_number][y-1].get_data(category=self.category)
                    url = tl.generate_search_url(query=self.pages[page_number][y-1].data["title"])
                    new_torrent_list = TorrentDisplay(category=self.category,search_url=url,mode="search")
                    new_torrent_list.pagination(stdscr)
                    new_torrent_list.display_page(stdscr)
                    self.display_page(stdscr,page_number=page_number)
                    break
                    
            if y > len(self.pages[page_number]):
                y = 1
                next_page = page_number + 1
                if next_page < len(self.pages):
                    self.display_page(stdscr,next_page,y=y,x=x)
                    break
                else:
                    self.display_page(stdscr,0,y=1,x=x)
                    break
                
            elif y < 1:
                if page_number != 0:
                    last_page = page_number - 1
                    y = len(self.pages[last_page])
                    self.display_page(stdscr,last_page,y=y,x=x)
                    break
                y = 1

def category_menu(stdscr,category:str="movies"):
    stdscr.clear()
    if category == "xxx":
        stdscr.addstr(0,10,category.upper())
    else:
        stdscr.addstr(0,10,category.title())
    stdscr.addstr(1,2,"[ ]Popular Today")
    stdscr.addstr(2,2,"[ ]Popular Week")
    stdscr.addstr(3,2,"[ ]Filter Uploaders")
    if category == "xxx" or category == "xxx-week":
        stdscr.addstr(4,2,"[ ]Filter Stars")
        star_filter = False
    y,x=1,3
    uploader_filter = False
    while True:
        stdscr.move(y,x)
        key = stdscr.getkey()
        if key == "KEY_UP":
            y = y-1
        elif key == "KEY_DOWN":
            y=y+1
        elif key == '\x1b':
            categories_menu(stdscr)
        elif key == " ":
            if y == 1:
                torrentList = TorrentDisplay(category=category)
                if uploader_filter:
                    torrentList.torrentList.filter_uploaders()
                if category == "xxx" or category == "xxx-week":
                    if star_filter:
                        torrentList.torrentList.filter_tracked_items("./filters/stars.json")
                torrentList.pagination(stdscr)
                torrentList.display_page(stdscr)
                category_menu(stdscr,category=category)             
            elif y == 2:
                torrentList = TorrentDisplay(category=category,time="week")
                if uploader_filter:
                    torrentList.torrentList.filter_uploaders()
                if category == "xxx" or category == "xxx-week":
                    if star_filter:
                        torrentList.torrentList.filter_tracked_items("./filters/stars.json")
                torrentList.pagination(stdscr)
                torrentList.display_page(stdscr)
                category_menu(stdscr,category=category)     
            elif y == 3:
                if uploader_filter == False:
                    uploader_filter = True
                    stdscr.addstr(3,2,"[X]Filter Uploaders")
                elif uploader_filter == True:
                    stdscr.addstr(3,2,"[ ]Filter Uploaders")
                    uploader_filter = False
            elif category == "xxx" and y == 4:
                if star_filter == False:
                    stdscr.addstr(4,2,"[X]Filter Stars")
                    star_filter = True
                elif star_filter == True:
                    stdscr.addstr(4,2,"[ ]Filter Stars")
                    star_filter = False
                    
        if category == "xxx":
            if y > 4:
                y = 1
            if y == 0:
                y = 4
        elif category != "xxx":
            if y > 3:
                y = 1
            if y == 0:
                y = 3


def categories_menu(stdscr):
    stdscr.clear()
    stdscr.addstr(1,2,"[ ]Movies")
    stdscr.addstr(2,2,"[ ]Television")
    stdscr.addstr(3,2,"[ ]Games")
    stdscr.addstr(4,2,"[ ]Music")
    stdscr.addstr(5,2,"[ ]Applications")
    stdscr.addstr(6,2,"[ ]Anime")
    stdscr.addstr(7,2,"[ ]Documentaries")
    stdscr.addstr(8,2,"[ ]Other")
    stdscr.addstr(9,2,"[ ]XXX")
    y,x=1,3
    stdscr.refresh()
    while True:
        stdscr.move(y,x)
        key = stdscr.getkey()
        if key == "KEY_UP":
                y-=1
        elif key == "KEY_DOWN":
                y+=1
        elif key == '\x1b':
                main(stdscr)
        elif key == " ":
            if y == 9:
                category_menu(stdscr,"xxx")
            elif y == 8:
                category_menu(stdscr,"other")
            elif y == 7:
                category_menu(stdscr,"documentaries")
            elif y == 6:
                category_menu(stdscr,"anime")
            elif y == 5:
                category_menu(stdscr,"apps")
            elif y == 4:
                category_menu(stdscr,"music")
            elif y == 3:
                category_menu(stdscr,"games")
            elif y == 2:
                category_menu(stdscr,"tv")    
            elif y == 1:
                category_menu(stdscr,"movies")
        if y > 9:
            y=1
        if y == 0:
            y = 9


def search_menu(stdscr):
    stdscr.clear()
    stdscr.addstr(0,10,"Search Menu")
    stdscr.addstr(1,2,"[ ]Query")
    stdscr.addstr(2,2,"[ ]Minimum Seeders")
    stdscr.addstr(3,2,"[ ]Minimum Quality")
    stdscr.addstr(4,2,"[ ]Filter Uploaders")
    stdscr.addstr(5,2,"[ ]Search")
    query_window = curses.newwin(1,100,1,25)
    query_textbox = curses.textpad.Textbox(query_window)
    seeds_window = curses.newwin(1,10,2,25)
    seeds_textbox = curses.textpad.Textbox(seeds_window)
    quality_window = curses.newwin(1,10,3,25)
    quality_textbox = curses.textpad.Textbox(quality_window)
    pages_window = curses.newwin(1,100,5,15)
    pagesTextbox = curses.textpad.Textbox(pages_window)
    
    y,x = 1,3
    uploader_filter = False
    min_seeds = 0
    min_quality = "480p"
    while True:
        stdscr.refresh()
        stdscr.move(y,x)
        key = stdscr.getkey()
        if key == "KEY_UP":
            y-=1
        elif key == "KEY_DOWN":
            y+=1
        elif key == '\x1b':
            main(stdscr)
        elif key == " ":
            if y == 1:
                query_text = query_textbox.edit()
                query_text.replace(" ","+")
            elif y == 2:
                min_seeds = seeds_textbox.edit()
            elif y == 3:
                min_quality = quality_textbox.edit()
                min_quality = min_quality.strip()
            elif y == 4:
                if uploader_filter == False:
                    uploader_filter = True
                    stdscr.addstr(4,2,"[X]Filter Uploaders")
                elif uploader_filter:
                    uploader_filter = False
                    stdscr.addstr(4,2,"[ ]Filter Uploaders")
                
            elif y == 5:
                url = tl.generate_search_url(query_text)
                torrentList = TorrentDisplay(mode="search",search_url=url)
                
                torrentList.torrentList.filter_minimum_seeders(min_seeds)
                torrentList.torrentList.filter_minimum_quality(min_quality)
                if uploader_filter:
                    torrentList.torrentList.filter_uploaders()
                torrentList.display_page(stdscr)
                
def torrent_menu(stdscr,torrent,category:str="movies"):
    stdscr.clear()
    stdscr.addstr(1,2,torrent.info["title"])
    stdscr.addstr(2,2,torrent.info["uploader"])
    #draws the series data for tv shows on the screen
    if category == "tv" or category == "tv-week":
        try:
            stdscr.addstr(4,2,torrent.series_data["overview"])
        except AttributeError:
            stdscr.addstr(3,2,"Could not Find Series Data")
        else:
            stdscr.addstr(3,2,torrent.series_data["name"])
    
    if category == "movies" or category == "movies-week":
        stdscr.addstr(4,2,torrent.data["overview"])
    if category == "xxx" or category == "xxx-week":
        stdscr.addstr(3,2,torrent.series_data["title"])
        i = 3
        for performer in torrent.data["performers"]:    
            i = i + 1
            stdscr.addstr(i,2,performer)
    stdscr.refresh()
    y,x = 1,2
    while True:
            stdscr.move(y,x)
            key = stdscr.getkey()
            if key == "KEY_UP":
                y-=1
            elif key == "KEY_DOWN":
                y+=1
            elif key == '\x1b':
                break
            
newOptions = [{"position": 1,"text": "Categories"},{"position":2,"text": "Search"}]
def main(stdscr):
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    while True:
        stdscr.clear()
        for option in newOptions:
            stdscr.addstr(option.get("position"), 1, "[ ]" + option.get("text"))
        x,y = 1,0
        while True:
            key = stdscr.getkey()
            if key == "KEY_UP":
                y-=1
            elif key == "KEY_DOWN":
                y+=1
            elif key == '\x1b':
                exit()
            elif key == " ":
                if y == 1:
                    categories_menu(stdscr)
                elif y == 2:
                    search_menu(stdscr)
            if y > len(newOptions):
                y = 1
            elif y <= 0:
                y=len(newOptions)
            stdscr.move(y,2)
            stdscr.refresh()

load_dotenv("./.env")

#torrentList = TorrentDisplay()
#torrentList.pagination()
wrapper(main)