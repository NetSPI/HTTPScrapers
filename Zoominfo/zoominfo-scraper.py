#!/usr/bin/env python3
import argparse
import sys
import textwrap
import cloudscraper # pip3 install cloudscraper
import re
from time import sleep
import random

'''
Scrapes zoominfo.com for employee names and turns them into email addresses automagically
'''

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=textwrap.dedent('''\
##########################################################
Scrapes zoominfo.com for employee names and turns them
into email addresses automagically

Getting started -

Google dork your target "domain.tld" like so:

site:zoominfo.com domain.tld

Pick the correct instance (usually the first) and give
everything after "https://www.zoominfo.com/c/" as -z
e.g., -z 'netspi-inc/36078304'

The -g switch with a domain (-d) will automatically
take the first Google search result and proceed
e.g., -d netspi.com -g

There are four format (-f) options:
    1. flast@domain.tld (e.g., jdoe@netspi.com) (default)
    2. first.last@domain.tld (e.g., john.doe@netspi.com)
    3. lastf@domain.tld (e.g., doej@netspi.com)
    4. Full name (e.g., John Marie Doe)

CloudFlare is a bear, so random breaks are added for each
request to not poke the bear too much. If there are more
than 10 pages, a 60 second break is taken every 10 pages.

If you get multiple 429's returned, it's likely that you
are being rate limited by CloudFlare. You can try
changing your IP and continuing with 'y'.
##########################################################
                                 '''))
parser.add_argument('-z', metavar='zoominfo/path', help='zoominfo.com path after /c/')
parser.add_argument('-d', metavar='domain.tld', help='The domain.tld to append to addresses')
parser.add_argument('-f', metavar='format', help='1:flast(default), 2:first.last, 3:lastf, 4:full', type=int, default=1)
parser.add_argument('-g', help='switch. automatically grab first google.com result for -d', action='store_true')
parser.add_argument('-o', metavar='outputfile', help='output filename')
parser.add_argument('-p', metavar='page', help='Page number to start on, default 1', type=int, default=1)
args = vars(parser.parse_args())

if not args['z'] and not (args['g'] and args['d']):
    parser.print_help(sys.stderr)
    sys.exit()

if args['f'] > 4:
    print("[-] Please double check your format option before we start. Exiting..")
    sys.exit()
else:
    format_option = args['f']

if args['d']:
    domain_tld = "@" + args['d']
else:
    domain_tld = ""

starting_page = args['p']
zoom_url = ""

if args['z']:
    zoom_url = "https://www.zoominfo.com/pic/{0}".format(args['z'])
else:
    print('[+] Using Google search')
    import googlesearch # pip3 install google
    for googleurl in googlesearch.search('site:zoominfo.com {0}'.format(args['d']), stop=1):
        print('[+] Using URL: {0}'.format(googleurl))
        zoom_url = "https://www.zoominfo.com/pic/{0}".format(googleurl.split("/c/",1)[1])

if not zoom_url:
    print('[-] No URL found. Try giving the correct path manually with -z.')
    print('[-] Exiting')
    sys.exit()

random_header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}


def zoomscrape(zoomurl, randomheader, startpage):
    pageno = startpage
    counter = 0
    status_code = 200
    companynamelist = []
    # Using the cloudflarescraper to bypass CloudFlare checks:
    s = cloudscraper.create_scraper()  # returns a CloudflareScraper instance
    while status_code == 200 or status_code == 429:
        nexturl = zoomurl+'?pageNum={0}'.format(pageno)
        print("[*] Requesting page {0}".format(pageno))
        r = s.get(nexturl, headers=randomheader)
        status_code = r.status_code
        if status_code == 200:
            print("[+] Found! Parsing page {0}".format(pageno))
            # This will break if they update their site at all :)
            companynamelist += re.findall(r'class="link amplitudeElement">(.*?)</a>', r.text)
            pageno += 1
            counter += 1
        elif status_code == 429:
            print("[-] Site returned status code: ", status_code)
            print("[-] Likely rate-limited by CloudFlare :/ Pausing")
            answer = input("[*] Maybe change your IP address. Continue? (y/N)")
            if not answer == 'y' and not answer == 'Y':
                break
        elif status_code == 410:
            print("[+] Site returned status code: ", status_code)
            print("[+] We seem to be at the end! Yay!")
            break
        else:
            print("[-] Site returned status code: ", status_code)
            print("[-] Status code not 200. Not sure why.. Quitting!")
            break
        print("[*] Random sleep break to appease CloudFlare")
        sleep(random.randint(1, 8))
        if not counter % 50:
            print("[*] Taking a 5 minute break after 50 pages!")
            sleep(300 + random.randint(1, 10))
        elif not counter % 10:
            print("[*] Taking a 60 second break after 10 pages!")
            sleep(60 + random.randint(1, 10))
    return companynamelist
# End def zoomscrape()


def printlist(emaillist, domaintld, formatoption, outputfile):
    # Print out the company name list
    if not emaillist:
        print("[-] List appears to be empty")
    else:
        print("[+] Printing email address list")
        z = []
        if formatoption == 1:
            for y in emaillist:
                first, *middle, last = y.split()
                z.append(first[0] + last + domaintld)
            z = list(map(str.lower, z))
            z = set(z)
            z = sorted(z)
        elif formatoption == 2:
            for y in emaillist:
                first, *middle, last = y.split()
                z.append(first + "." + last + domaintld)
            z = list(map(str.lower, z))
            z = set(z)
            z = sorted(z)
        elif formatoption == 3:
            for y in emaillist:
                first, *middle, last = y.split()
                z.append(last + first[0] + domaintld)
            z = list(map(str.lower, z))
            z = set(z)
            z = sorted(z)
        else:
            z = emaillist
            z = set(z)
            z = sorted(z)
        if outputfile:
            try:
                print("[*] Writing to file {0}".format(outputfile))
                with open(outputfile, 'w') as f:
                    for x in z:
                        f.write("{0}\n".format(x))
            except:
                print("[-] Write to file failed! Printing here instead:")
                for x in z:
                    print(x)
        else:
            for x in z:
                print(x)
        print("[+] Found " + str(len(z)) + " names!")
# End def printlist()

email_list = zoomscrape(zoom_url, random_header, starting_page)
email_list = set(email_list)
email_list = sorted(email_list)
printlist(email_list, domain_tld, format_option, args['o'])
