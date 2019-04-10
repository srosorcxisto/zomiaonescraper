import os
import string
import time
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil.parser import parse

import PyRSS2Gen
import boto3
import http.cookiejar
import mechanize

# globals
podbean_feed_url = 'https://zomia.podbean.com/'
outfile = 'zomia_' + time.strftime("%Y%m%d-%H%M%S") + '.xml'


br = mechanize.Browser()

# Enable cookie support for urllib2
cookiejar = http.cookiejar.LWPCookieJar()
br.set_cookiejar(cookiejar)

# browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)
br.addheaders = [('User-agent',
                  'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

res = br.open(podbean_feed_url)
soup = BeautifulSoup(res.read(), features='html5lib')

posts = soup.find_all('div', attrs={'class': 'post'})

podcast_feed = []

for post in posts:
    if post.find('div', attrs={'class': 'premium-btn-block'}):
        post_title = filter(lambda x: x in string.printable, ''.join(post.find('h2').string))
        post_date = post.find('span').get_text()
        post_date = parse(post_date)
        post_description = filter(lambda x: x in string.printable, post.find_all('p')[1].get_text())[:-13]
        post_audio = post.find('div', attrs={'class': 'pbplayerBox theme13'})['data-uri']
        post_guid = post['id']
        podcast_feed.append((post_title, post_audio, post_description, post_date, post_guid))

rss = PyRSS2Gen.RSS2(
    title='Unofficial Zomia ONE Premium Feed',
    link='https://zomia.podbean.com/',
    image=PyRSS2Gen.Image('https://pbcdn1.podbean.com/imglogo/ep-logo/pbblog4172212/zomiaoneunderground.jpg',
                          'ZomiaONE',
                          'https://zomia.podbean.com',
                          '144',
                          '144',
                          'Zomia ONE Underground'),

    description='This is an unofficial RSS feed for zomia.podbean.com which, unlike the Official RSS feed, '
                'only includes Premium content. To use this feed you must use a Podcaster that supports HTTP '
                'Authentication like PodcastAddict and be a Zomia ONE Patron. Enter your PodBean account credentials '
                'in your Podcast App to access content. This script is maintained by a SovrynTech fan and relies on '
                'scraping the Podbean site, so it may break at any time. Please send bugs to '
                'srosorcxisto@protonmail.ch. This feed is completely unofficial and not connected in any way to the '
                'ZomiaONE network.',
    lastBuildDate=datetime.now())

rss_post = []
for post in podcast_feed:
    rss.items.append(PyRSS2Gen.RSSItem(
        title=post[0],
        link=post[1],
        description=post[2],
        guid=post[4],
        pubDate=post[3]))
rss.write_xml(open(outfile, 'w'))

# save to public S3 bucket using AI credentials from environment
s3 = boto3.resource('s3')
s3.meta.client.upload_file(outfile, 'zomiaoneunofficialfeed', 'zomiaoneunofficialpatron.xml')
