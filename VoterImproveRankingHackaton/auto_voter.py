#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import random
import string
import cookielib, Cookie
import time
import csv
import urllib
from lxml import etree
import json

def random_line(afile):
    line = next(afile)
    for num, aline in enumerate(afile):
        if random.randrange(num + 2): continue
        line = aline
    return line

def get_proxies():
    response = urllib2.urlopen(proxy_url)
    tree = etree.HTML(response.read())
    plist = []
    for xp in tree.xpath("//tr"):
        if xp.xpath("td[2]/a/text()") and xp.xpath("td[1]/span/text()"):
            plist.append(xp.xpath("td[1]/span/text()")[0] + ":" + xp.xpath("td[2]/a/text()")[0].strip())

    print "Got %s proxies. Ready to work." % len(plist)
    return plist
    

start_url = "http://www.wonderwomen.paris/login?returnUrl=%2Fvideo%2F617%2Fhenjoy"
register_url = "http://www.wonderwomen.paris/register?returnUrl=/video/617/henjoy"
vote_url = "http://www.wonderwomen.paris/videos/vote/617"
proxy_url = "http://www.proxynova.com/proxy-server-list/country-fr/"
method = "POST"

#Format: email name surname
names_filename = "extended.txt"

#Format: each string is a User-agent
user_agent_filename = "user-agents.txt"

#Format: email password
registered_users_filename = "registered_users.txt"

#Headers for request
custom_headers = [('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
                  ('Accept-Encoding', 'gzip, deflate, sdch'),
                  ('Accept-Language', 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4'),
                  ('Connection', 'keep-alive'),
                  ('Cookie', 'returnUrl=/videos/register'),
                  ('DNT', '1'),
                  ('Content-Length', '0'),
                  ('Host', 'www.wonderwomen.paris'),
                  ('Upgrade-Insecure-Requests', '1')]

#Next request will be done in random time between first and second number (in seconds)
sleep_duration = [10, 60]

proxies = get_proxies()

while True:
    try:
        #Setting cookie jar
        cookies = cookielib.CookieJar()

        #Getting random proxy host and port
        if proxies:
            proxy_string = random.choice(proxies)
            print "Trying proxy: %s" % proxy_string
            proxy_host = proxy_string.split(":")[0].strip()
            proxy_port = proxy_string.split(":")[1].strip()
        else:
            print "Proxies are out. Fetching new ones."
            proxies = get_proxies()
            continue

        #Setting up proxy and building opener with it and cookie jar
        proxy = urllib2.ProxyHandler({'http': '%s:%s' % (proxy_host, proxy_port)})
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies), proxy, urllib2.HTTPHandler)

        #Forming request to get captcha and hidden check
        request = urllib2.Request(start_url)
        response = opener.open(request)
        content = unicode(response.read(), errors='ignore')
        tree = etree.HTML(content)
        captcha_dirty = tree.xpath("//div[@class=\"col-xs-12 captcha\"]/div/span/text()")[0]
        captcha_cleaned = ""

        #Cleaning captcha, leaving numbers and operation signs
        for letter in captcha_dirty:
            if letter.isdigit() or letter in "+":
                captcha_cleaned += letter

        #Getting random user from extended.txt    
        f = open(names_filename, "r")
        line = random_line(f).strip().split(" ")
        f.close()

        #Forming data to request
        email = line[0]
        first_name = line[1]
        last_name = line[2]
        password = "".join(random.choice(random.choice(string.ascii_letters+string.digits)) for _ in range(random.randrange(5,12)))
        captcha = str(eval(captcha_cleaned))
        check = tree.xpath("//div[@class=\"col-xs-12 captcha\"]/div/input[@name=\"check\"]/@value")[0]
        data = urllib.urlencode({'firstName': first_name,
                         'lastName': last_name,
                         'email': email,
                         'password': password,
                         'passwordConfirmation': password,
                         'newsletter': 'false',
                         'captcha': captcha,
                         'check': check})

        #Forming URL to request registration form
        url = register_url + "&" + data
        initial_register_request = urllib2.Request(url)
        initial_register_request.get_method = lambda : method

        #Adding headers to request
        headers = custom_headers[:]
        f = open(user_agent_filename, "r")
        headers.append(('User-Agent', random_line(f).strip()))
        f.close()
        opener.addheaders = custom_headers

        #Adding cookies from initial request
        cookies.add_cookie_header(initial_register_request)
        
        try:
            #Trying to register    
            response = opener.open(initial_register_request)
			
            #Random delay for user-like behaviour
            time.sleep(random.randrange(1, 5))
			
            #If got the HTTP 200
            if response.code == 200:
                #Then proceed
                pass
            #Otherwise
            else:
                #Start new iteration
                continue
            
            #Write registered user credentials to file
            with open(registered_users_filename, "a") as myfile:
                myfile.write("%s %s\n" % (email, password))

            #Forming URL to request vote modal
            vote_modal_request=urllib2.Request(vote_url)
            vote_modal_request.get_method = lambda : method

            #Adding cookies
            cookies.add_cookie_header(vote_modal_request)

            #Trying to get modal data
            vote_modal_response = opener.open(vote_modal_request)

            #Random delay for user-like behaviour
            time.sleep(random.randrange(1, 5))
			
            #If got the HTTP 200
            if vote_modal_response.code == 200:
                #Then proceed
                pass
            #Otherwise
            else:
                #Start new iteration
                continue

            #Converting recieved data from JSON to Python dictionary
            modal = dict(json.loads(vote_modal_response.read()))["modal"]

            #Bulding tree with nodes for XPATH selections
            tree = etree.HTML(modal)

            #Cleaning captcha
            captcha_dirty = tree.xpath("//div[@class=\"modal-body\"]/p[1]/text()")[0].strip()
            captcha_cleaned = ""
            for letter in captcha_dirty:
                if letter.isdigit() or letter in "+":
                    captcha_cleaned += letter
            captcha = str(eval(captcha_cleaned))

            #Getting hidden check value
            check = tree.xpath("//button[@class=\"btn btn-primary\"]/@onclick")[0].split(",")[-1][1:-1]

            #For logging purposes
            print "Got captcha \"%s\", answer: %s. Hidden check is %s" % (captcha_dirty, captcha, check)

            #Forming data based on received modal window
            data = urllib.urlencode({'captcha': captcha,
                                     'check': check})
            vote_with_captcha_url = vote_url + "?" + data

            #Setting up request to vote
            vote_request=urllib2.Request(vote_with_captcha_url)
            vote_request.get_method = lambda : method

            #Adding cookies
            cookies.add_cookie_header(vote_request)

            #And send request
            vote_response = opener.open(vote_request)

            #If got the HTTP 200
            if vote_modal_response.code == 200:
                #Then proceed
                pass
            #Otherwise
            else:
                #Start new iteration
                continue

            print "Got vote with %s:%s (%s %s, %s)" % (proxy_host,
                                                       proxy_port,
                                                       first_name,
                                                       last_name,
                                                       email)
           
            time.sleep(random.randrange(sleep_duration[0], sleep_duration[1]))
        except Exception as e:
            if e != KeyboardInterrupt:
                print e
            else:
                raise KeyboardInterrupt
        
        
    except urllib2.URLError, urllib2.BadStatusLine:
        print "Bad proxy %s:%s" % (proxy_host, proxy_port)
        proxies.remove(proxy_string)
        print "Removed it from the list"
