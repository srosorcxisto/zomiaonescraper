import string
import time
from datetime import datetime

import PyRSS2Gen
import bleach
import boto3
import mechanize
from bs4 import BeautifulSoup
from dateutil.parser import parse

# globals
podbean_feed_url = 'https://zomia.podbean.com/'
s3_bucket = 'zomiaoneunofficialfeed'
feed_name = 'zomiaoneunofficialpatron.xml'
outfile = 'zomia_' + time.strftime("%Y%m%d-%H%M%S") + '.xml'  # Save each .xml file revision for debugging.

br = mechanize.Browser()

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
        post_date = post.find('p', attrs={'class': 'post-info'}).get_text()
        post_date = parse(post_date, fuzzy=True)
        post_audio = PyRSS2Gen.Enclosure(post.find('div', attrs={'class': 'pbplayerBox theme13'})['data-uri'],
                                         '300000000', 'audio/mpeg')
        post_permlink = post.find_all('a', href=True)[0]['href']

        post_soup = BeautifulSoup(br.open(post_permlink).read(), features='html5lib')
        post_description_html = post_soup.find('div', attrs={'class': 'entry'})

        post_description_html.find(('div'), attrs={'class': 'podPress_content'}).decompose()
        post_description = bleach.clean(str(post_description_html),
                                        tags=['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                                              'em', 'i', 'li', 'ol', 'strong', 'ul', 'p'],
                                        strip=True).strip()

        podcast_feed.append((post_title, post_audio, post_description, post_date, post_permlink))

rss = PyRSS2Gen.RSS2(
    title='Unofficial Zomia ONE Premium Feed',
    link='https://zomia.podbean.com/',
    image=PyRSS2Gen.Image('https://pbcdn1.podbean.com/imglogo/ep-logo/pbblog4172212/zomiaoneunderground.jpg',
                          'Unofficial Zomia ONE Premium Feed',
                          'https://zomia.podbean.com/',
                          '144',
                          '144',
                          'Unofficial Zomia ONE Premium Feed'),

    description='This is an unofficial RSS feed for zomia.podbean.com which, unlike the Official RSS feed, only '
                'includes premium content. For more information, visit https://github.com/srosorcxisto/zomiaonescraper ' 
                'This feedis completely unofficial and not connected in any way to the Zomia ONE network.',
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

# save to public S3 bucket using AMI credentials from environment
s3 = boto3.resource('s3')
s3.meta.client.upload_file(outfile, s3_bucket, feed_name, ExtraArgs={'ContentType': 'text/xml'})
