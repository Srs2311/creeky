import curses
import curses.textpad
from curses import wrapper
import os
from dotenv import load_dotenv
import webbrowser
import qbittorrentapi
import torrent_lister as tl

class TorrentDisplay():
    """Creates a list of pages with appropriately long lists of torrents based on screen size"""
    def __init__(self,category:str="movies",time:str="day",mode:str="popular",search_url:str = "") -> None:
        if mode == "popular":
            self.torrentList = tl.get_popular_queue(category,time)
            self.category = category
            self.mode = mode
        elif mode == "search":
            self.torrentList = tl.TorrentList(search_url)
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
        try:
            print(self.pages[0])
        except AttributeError: 
            self.pagination(stdscr)
            self.display_page(stdscr,page_number)
        else:
            for torrent in self.pages[page_number]:
                torrent_index = self.pages[page_number].index(torrent)
                
                if len(torrent["title"]) > max_title_length:
                    torrent["title"] = torrent["title"][0:max_title_length]
                
                stdscr.addstr(torrent_index + 1,2,torrent["title"])
                stdscr.addstr(torrent_index + 1,(max_title_length + 4),"|")
                stdscr.addstr(torrent_index + 1,(max_title_length + 5),torrent["uploader"])
                stdscr.addstr(torrent_index + 1,(max_title_length + 14),"|")
                stdscr.addstr(torrent_index + 1,(max_title_length + 15),torrent["size"])
                stdscr.addstr(torrent_index + 1,(max_title_length + 24),"|")
                stdscr.addstr(torrent_index + 1,(max_title_length + 25),str(torrent["seeders"]))
                stdscr.addstr(torrent_index + 1,(max_title_length + 30),"|")
                stdscr.addstr(torrent_index + 1,(max_title_length + 31),"[ ]")
                stdscr.addstr(torrent_index + 1,(max_title_length + 35),"|")
                stdscr.addstr(torrent_index + 1,(max_title_length + 36),"[ ] ")
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
                    x = max_title_length + 32
                elif x == max_title_length + 32:
                    x = max_title_length + 37
            elif key == "KEY_LEFT":
                if x == max_title_length + 37:
                    x = max_title_length + 32
                elif x == max_title_length + 32:
                    x = 2
            elif key == '\x1b':
                category_menu(stdscr,category=self.category)
            elif key == " ":
                if x == max_title_length + 32:
                    webbrowser.open(self.pages[page_number][y-1].get("url") + self.pages[page_number][y-1].get("link"))
                if x == max_title_length + 37:
                    url = f"{self.pages[page_number][y-1]['url']}{self.pages[page_number][y-1]['link']}"
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
            if y > len(self.pages[page_number]):
                y = 1
                next_page = page_number + 1
                if next_page < len(self.pages):
                    self.display_page(stdscr,next_page,y=y,x=x)
                else:
                    self.display_page(stdscr,0,y=1,x=x)
                
            elif y < 1:
                if page_number != 0:
                    last_page = page_number - 1
                    y = len(self.pages[last_page])
                    self.display_page(stdscr,last_page,y=y,x=x)
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
    if category == "xxx":
        stdscr.addstr(4,2,"[ ]Filter Stars")
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
                torrentList.display_page(stdscr)             
            elif y == 2:
                torrentList = TorrentDisplay(category=category,time="week")
                if uploader_filter:
                    torrentList.torrentList.filter_uploaders()
                torrentList.display_page(stdscr)  
            elif y == 3:
                if uploader_filter == False:
                    uploader_filter = True
                    stdscr.addstr(3,2,"[X]Filter Uploaders")
                elif uploader_filter == True:
                    stdscr.addstr(3,2,"[ ]Filter Uploaders")
                    uploader_filter = False
            
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

def searchMenu(stdscr):
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
        elif key == " ":
            if y == 1:
                query_text = query_textbox.edit()
                query_text.replace(" ","+")
            elif y == 2:
                min_seeds = seeds_textbox.edit()
            elif y == 3:
                min_quality = quality_textbox.edit()
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
                
                
newOptions = [{"position": 1,"text": "Categories"},{"position":2,"text": "Search"}]
def main(stdscr):
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
                    searchMenu(stdscr)
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