from feedFetch import feedToJSON
import requests_cache
import time
import concurrent.futures
from dateutil.parser import parse
import threading
import configs as cf


# to use configs.json from external source
# import requests

requests_cache.install_cache('feedscache', backend='sqlite', expire_after=1200)

# using configs from configs.py
configs = cf.configs


###########
# using configs.json from external source
# r = requests.get("CONFIGS.JSON URL")
# configs = r.json()

urllist = configs['sources'].values()


#feedList refreshed every 660 seconds
newlist = []

#final feed List (updates with newlist)
finallist = []

def getTimestamp(pubdate):
    parsedDate = parse(pubdate)
    return time.mktime(parsedDate.timetuple())


def newListInit(urll):
    global newlist
    a = feedToJSON(urll)
    b = a.getfeed()
    newlist += b


def getData():
    global newlist,finallist
    newlist = []
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(newListInit, urllist)
    newlist = sorted(newlist, key=lambda k: getTimestamp(k['published']), reverse=True)
    finallist = newlist
    t = threading.Timer(660, getData)
    t.start()


def searchFilter(listFeed, query):
    filteredList = []
    for feed in listFeed:
        for elem in feed['tags']:
            if query.lower() in elem:
                filteredList.append(feed)
                break
    return filteredList


def specSource(urll, pageno, ss, cacheflag):
    x = feedToJSON(url=urll, pageNo=pageno, s=ss, cacheFlag=cacheflag)
    r = x.getfeed()
    return r


def channelinfo(urll):
    y = feedToJSON(url=urll)
    return y.channelinfo()
