### About
One of my favorite Podcast, SovryTech just moved from Patreon to PodBean. Unfortunately, the PodBean RSS Feed does not 
include premium content, requiring the PodBean App to listen. luckily, PodBean DOES allow access to http content
using HTTP authentication if you have the url for the mp3 file and a premium subscription.

This script scrapes the zomia.podbean.com site for premium content and creates an RSS feed for it. When loaded into a 
podcatcher, this allows you listen to premium content if you are a Zomia ONE Underground subscriber.

It should go without saying that this is a fan created script and is in no way connected with or endorsed by Zomia ONE
or Podbean.

### Linux quickstart:
```bash
$ git clone https://github.com/wkelly19/zomiaonescraper.git
$ cd zomiascraper
$ nano src/zomiascraper.py 
     --> Change s3_bucket to whater you want 
$ virtualenv env
$ source env/bin/activate
$ pip install -r requirements.txt
$ python src/zomiascraper.py

```

This assumes that your AMI credentials are stored in the environment. 

If you just want to use the feed without running the script or setting up s3, you can
 access my feed at:

> https://zomiaoneunofficialfeed.s3.amazonaws.com/zomiaoneunofficialpatron.xml

In your favorite Podcatcher just add this feed and use your PodBean credentials
for the authentication. Depending on your podcatcher, you may have to check a box for 
“Authentication required” (or similar) to see these fields. If you are not a Premium 
subscriber you will receive an 403 error.

This feed is updated every two hours.

### Help

This was created primarily for my own use and is not very full featured. If you would like to improve this script, 
feel free to submit a pull request. If you have any issues, feel free to reach out to me on GitHub.
