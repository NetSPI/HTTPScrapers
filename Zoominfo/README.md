# zoominfo-scraper

## Purpose
Scrapes zoominfo.com for employee names and turns them
into email addresses automagically.

## Disclaimer
This isn't using any fancy APIs or anything, so if zoominfo.com updates their site at all this script will fail hilariously.

## A Word on CloudFlare
The random sleep breaks within the script are in an attempt to avoid CloudFlare rate-limiting.

CloudFlare DDoS protection is really the biggest hurdle for scraping zoominfo.com. CloudFlare has a browser Javascript challenge every so often that cloudscraper attempts to solve. Then if CloudFlare decides you have solved its challenges too quickly or too often, it may randomly decide to completely block you from accessing the site. The only option at that point would be to wait until the rate-limiting subsides or connect via a different IP address. Both the Javascript challenge and the full-blown rate-limiting are 429 responses, so if you see a 429 from the script and cloudscraper isn't broken (also possible) you are likely being rate-limited :). VPNs are a quick and easy way around the issue if it comes up, and the script will also pause automatically at any 429 responses.


## Getting started

Google dork your target "domain.tld" like so:

    site:zoominfo.com domain.tld

Pick the correct instance (usually the first) and give the script everything after "https://www.zoominfo.com/c/" as **-z**, e.g.,

    -z 'netspi-inc/36078304' -d netspi.com

To have the script automatically search and select the first Google dork result and proceed, use the **-g** switch with **-d**, e.g.,

    -d netspi.com -g

There are four format (-f) options:
   1. flast@domain.tld (e.g., jdoe@netspi.com) (default)
   2. first.last@domain.tld (e.g., john.doe@netspi.com)
   3. lastf@domain.tld (e.g., doej@netspi.com)
   4. Full name (e.g., John Marie Doe)

CloudFlare is a bear, so random sleeps are added for each
request to not poke the bear too much. If there are more
than 10 pages, a ~60 second break is taken every 10 pages.

If you get multiple 429's returned, it's likely that you
are being rate limited by CloudFlare. You can try
changing your IP and continuing with 'y'.

## Install
The tool needs the following package to run:

    pip3 install cloudscraper

Optional: 

    pip3 install google

## Run instructions
Requires python3. (-z) or (-g **and** -d) are required. (-z) is the zoominfo.com path described above. (-d) appends whatever domain.tld you want to the employee names. The (-f) format options are also described above. An output file (-o) option will write to a given filename. Run the script with no options or (-h) to see the help menu.
    
    python3 zoominfo-scraper.py -z zoominfo/path [-d domain.tld] [-f 1] [-o outputfile.txt] [-g]

## References
- https://pypi.org/project/cloudscraper/
