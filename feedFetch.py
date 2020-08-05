# requests : to request content from feed
import requests

# beautiful soup to parse xml
from bs4 import BeautifulSoup

# to convert published-timestamp
import time
from dateutil.parser import parse

# xml : xml parsing library
import lxml

# cache requests
import requests_cache


class feedToJSON:
    """
    Converts rss feed to dictionary

    channelinfo() - returns info about the source.
    getfeed() - returns news feed.

    """

    # headers for request
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '
                             'AppleWebKit/537.11 (KHTML, like Gecko) '
                             'Chrome/23.0.1271.64 Safari/537.11',
               'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
               'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
               'Accept-Encoding': 'none',
               'Accept-Language': 'en-US,en;q=0.8',
               'Connection': 'keep-alive'}

    # keys for atom feeds
    atomkeys = {
        'channelTitle': 'title',
        'channelDescription': 'subtitle',
        'channelLastUpdate': 'updated',
        'channelLink': 'link',
        'channelImage': 'icon',
        'items': 'entry',
        'postTitle': 'title',
        'postLink': 'link',
        'postPublishedDate': 'published',
        'postCategory': 'category',
        'postDescription': 'summary',
        'postAuthor': 'name',
    }

    # keys for rss feeds
    rsskeys = {
        'channelTitle': 'title',
        'channelDescription': 'description',
        'channelLastUpdate': 'lastBuildDate',
        'channelLink': 'link',
        'channelImage': 'image',
        'items': 'item',
        'postTitle': 'title',
        'postLink': 'link',
        'postPublishedDate': 'pubDate',
        'postCategory': 'category',
        'postDescription': 'description',
        'postAuthor': 'creator',
    }

    def __init__(self, url="", pageNo=-1, noItems=0, offset=0, s="", cacheFlag=True):
        self.url = url
        self.pageNo = pageNo
        self.noItems = noItems
        self.offset = offset
        self.s = s
        self.cacheFlag = cacheFlag
        self.feedtype = feedToJSON.rsskeys

    def checktype(self, content):
        if content.find('entry') is not None:
            self.feedtype = feedToJSON.atomkeys

    def channelinfo(self):
        try:

            sourceinfo = dict()
            channelInfoReq = requests.get(self.url, headers=feedToJSON.headers)

            if channelInfoReq.status_code == 200:
                channelsoup = BeautifulSoup(channelInfoReq.content, "xml")

                # set the type of feed(rss or atom)
                self.checktype(channelsoup)

                channelTitle = channelsoup.find(self.feedtype['channelTitle'])
                channelDesc = channelsoup.find(self.feedtype['channelDescription'])
                channelLink = channelsoup.find(self.feedtype['channelLink'])
                imageFind = channelsoup.find(self.feedtype['channelImage'])
                lastUpdated = channelsoup.find(self.feedtype['channelLastUpdate'])
                sourceinfo['lastUpdated'] = '' if lastUpdated is None else time.strftime("%Y-%m-%dT%H:%M:%SZ", parse(
                    lastUpdated.text.strip()).timetuple())

                try:
                    if channelLink is not None:
                        if self.feedtype == feedToJSON.atomkeys:
                            sourceinfo['link'] = channelLink['href']
                        else:
                            sourceinfo['link'] = channelLink['href'][:-5]
                    else:
                        sourceinfo['link'] = ''
                except:
                    sourceinfo['link'] = ''
                sourceinfo['title'] = '' if channelTitle is None else channelTitle.text.strip()
                if imageFind is None:
                    sourceinfo['image'] = ''
                else:
                    try:
                        if self.feedtype == feedToJSON.rsskeys:
                            sourceinfo['image'] = imageFind.find('url').text.strip()
                        else:
                            sourceinfo['image'] = imageFind.text.strip()
                    except:
                        sourceinfo['image'] = ""
                sourceinfo['desc'] = "" if channelDesc is None else channelDesc.text.strip()
                return sourceinfo

        except Exception as e:
            return {'error': str(e)}

    def getfeed(self):
        params = {}
        feedlist = list()

        if self.pageNo > 0:
            params['paged'] = self.pageNo
        if self.s != "":
            params['s'] = self.s

        try:
            if self.cacheFlag == True:
                feedreq = requests.get(self.url, headers=feedToJSON.headers, params=params)
            else:
                with requests_cache.disabled():
                    feedreq = requests.get(self.url, headers=feedToJSON.headers, params=params)
        except Exception as e:
            return {'error': str(e)}

        feedsoup = BeautifulSoup(feedreq.content, 'xml')
        # set the type of feed(rss or atom)
        self.checktype(feedsoup)

        items = feedsoup.findAll(self.feedtype['items'])
        items = items if self.offset == 0 else items[self.offset - 1:]
        items = items if self.noItems == 0 else items[0:self.noItems]

        for item in items:

            newsd = dict()
            tags = list()

            title = item.find(self.feedtype['postTitle'])
            link = item.find(self.feedtype['postLink'])
            description = item.find(self.feedtype['postDescription'])
            descsoup = BeautifulSoup(description.text, 'lxml')
            categories = item.findAll(self.feedtype['postCategory'])
            publishedDate = item.find(self.feedtype['postPublishedDate'])
            author = item.find(self.feedtype['postAuthor'])
            newsd['title'] = '' if title is None else title.text.strip()

            if link is not None:
                if self.feedtype == feedToJSON.atomkeys:
                    newsd['link'] = link['href'].strip()
                else:
                    newsd['link'] = link.text.strip()
            else:
                newsd['link'] = ''

            imgfind = descsoup.find('img')
            newsd['image'] = '' if imgfind is None else imgfind['src']
            newsd['fulldesc'] = description.text
            newsd['source'] = self.channelinfo()['title']

            for el in ['div', 'img', 'a']:
                for p in descsoup.findAll(el):
                    p.extract()
            newsd['desc'] = '' if description is None else descsoup.text.strip()

            for category in categories:
                if self.feedtype == feedToJSON.atomkeys:
                    tags.append(category['term'].lower())
                else:
                    tags.append(category.text.lower())

            newsd['tags'] = tags
            newsd['published'] = '' if publishedDate is None else time.strftime("%Y-%m-%dT%H:%M:%SZ", parse(
                publishedDate.text.strip()).timetuple())
            newsd['author'] = '' if author is None else author.text.strip()
            feedlist.append(newsd)
        return feedlist
