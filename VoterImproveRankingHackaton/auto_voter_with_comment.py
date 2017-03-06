#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import random
import string
import cookielib, Cookie
import time
import csv
import urllib

def random_line(afile):
    line = next(afile)
    for num, aline in enumerate(afile):
        if random.randrange(num + 2): continue
        line = aline
    return line

register_url = "http://www.wonderwomen.paris/register?returnUrl=/video/617/henjoy"
vote_url = "http://www.wonderwomen.paris/videos/vote/617"
comment_url = "http://www.wonderwomen.paris/videos/comment/617"
method = "POST"

#Format: host:port
proxies_filename = "proxies.txt"

#Format: email name surname
names_filename = "extended.txt"

#Headers for request
custom_headers = [('Content-Length', '0')]

#Next request will be done in random time between first and second number (in seconds)
sleep_duration = [10, 60]

while True:
    try:
        f = open(names_filename, "r")
        line = random_line(f).strip().split(" ")
        email = line[0]
        first_name = line[1]
        last_name = line[2]
        f.close()

        password = "".join(random.choice(string.ascii_uppercase) for _ in range(8))

        cookies = cookielib.CookieJar()

        f = open(proxies_filename, "r")
        proxy_string = random_line(f)
        proxy_host = proxy_string.split(":")[0].strip()
        proxy_port = proxy_string.split(":")[1].strip()
        f.close()

        proxy = urllib2.ProxyHandler({'http': '%s:%s' % (proxy_host, proxy_port)})
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies), proxy, urllib2.HTTPHandler)
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies), urllib2.HTTPHandler)

        data = urllib.urlencode({'firstName': first_name,
                                 'lastName': last_name,
                                 'email': email,
                                 'password': password,
                                 'passwordConfirmation': password})

        url = register_url + "&" + data
        request = urllib2.Request(url)
        request.get_method = lambda : method

        try:
            opener.addheaders = custom_headers
            response = opener.open(request)
            if response.code == 200:
                
                request2=urllib2.Request(vote_url)
                request2.get_method = lambda : method
                cookies.add_cookie_header(request2)
                response2 = opener.open(request2)
                print "Got vote with %s:%s (%s %s, %s)" % (proxy_host,
                                                           proxy_port,
                                                           first_name,
                                                           last_name,
                                                           email)
                f = open("comments.txt")
                comment = random_line(f)
                f.close()

                data = urllib.urlencode({'text': comment.strip()})
                
                request3=urllib2.Request(comment_url + '?' + data + '%0A')
                request3.get_method = lambda : method
                cookies.add_cookie_header(request3)
                response3 = opener.open(request3)
                print "Left comment! (%s)" % comment
                time.sleep(random.randrange(sleep_duration[0], sleep_duration[1]))
        except Exception as e:
            if e != KeyboardInterrupt:
                print e
            else:
                raise KeyboardInterrupt
        
        
    except urllib2.URLError, urllib2.BadStatusLine:
        print "Bad proxy %s:%s" % (proxy_host, proxy_port)
