#!/usr/bin/env python
# -*- coding: utf-8 -*-

#28 September 2015
#UPDATED April 2017
#Richard Shanahan
#this code scrapes fb group pages using the mobile format for fb ie, 'm' rather than 'www'
#it can handle login, collapsible section pages and dynamic scroll/load pages
#NOTE: this code uses Chrome WebDriver with Selenium

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import re
import time
import csv
import pprint as pp
from collections import OrderedDict

#input login credentials
facebookusername = 'YOUR USER NAME'
facebookpassword = 'YOUR PASSWORD'

path_to_chromedriver = '/PATH/TO/chromedriver'            # change path as needed
browser = webdriver.Chrome(executable_path = path_to_chromedriver)

url = raw_input(['Enter your facebook group or page URL: ']).replace('www', 'm') + '/'    


#function to handle browser login - using Selenium
def fb_html(u):
    
    browser.get(u)
    
    try: 
        #fb mobile site login steps 
        browser.find_element_by_xpath('//*[@id="m_loginbar_login_button"]').send_keys(Keys.RETURN)
        browser.find_element_by_xpath('//*[@id="u_0_1"]/div[1]/div/input').send_keys(facebookusername)
        browser.find_element_by_xpath('//*[@id="u_0_1"]/div[1]/div/input').send_keys(Keys.TAB, facebookpassword)
        browser.find_element_by_xpath('//*[@id="u_0_1"]/div[1]/div/input').send_keys(Keys.TAB, Keys.TAB, Keys.TAB, Keys.RETURN)
    
    except NoSuchElementException:
        #alernative facebook_m login
        
        try: 
            browser.find_element_by_xpath('//*[@id="login_form"]/ul/li[1]/input').send_keys(facebookusername)
            browser.find_element_by_xpath('//*[@id="login_form"]/ul/li[2]/div/input').send_keys(facebookpassword)
            browser.find_element_by_xpath('//*[@id="login_form"]/ul/li[3]/input').send_keys(Keys.RETURN)
           
        except NoSuchElementException:
            browser.find_element_by_xpath('//*[@id="u_0_1"]/div[1]/div/input').send_keys(facebookusername)
            browser.find_element_by_xpath('//*[@id="u_0_2"]').send_keys(facebookpassword)
            browser.find_element_by_xpath('//*[@id="u_0_6"]').send_keys(Keys.RETURN)


    #call fb page handling functions - collapsibles + dynamic page scrolling function    
    fb_expander(browser)
    
    #source HTML for scraping
    html = browser.page_source
    
    return html



#function to handle dynamic page content loading - using Selenium
def fb_scroller(browser):
    
    #define initial page height for 'while' loop
    lastHeight = browser.execute_script("return document.body.scrollHeight")
    
    while True:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        #define how many seconds to wait while dynamic page content loads
        time.sleep(3)
        newHeight = browser.execute_script("return document.body.scrollHeight")
        
        if newHeight == lastHeight:
            break
        else:
            lastHeight = newHeight
    
    return browser


#function to handle collapsible section pages - expands the 2015 pages only
def fb_expander(browser):
    
    #define initial page height for 'while' loop
    lastHeight = browser.execute_script("return document.body.scrollHeight")
    
    time.sleep(3)
    
    try:
        #click the '2015' section expander
        browser.find_element_by_xpath('//*[@id="u_0_e"]/div[2]/div[2]/a/div[1]/div/h3/div/div').click()
        
    except NoSuchElementException:
        fb_scroller(browser)
    
    try:
        while True:
            time.sleep(3)
            #click the 'see more' expander for 2015 entries
            browser.find_element_by_xpath('//*[starts-with(@id, "u_")]/div[1]/div/h1/div/div').click()
        
            #capture new page height
            newHeight = browser.execute_script("return document.body.scrollHeight")
  
            if lastHeight == newHeight:
                #break
                fb_scroller(browser)
            else:
                lastHeight = newHeight
                
    except:
        fb_scroller(browser)
    
    return browser


    
#function to handle/parse HTML and extract data - using BeautifulSoup    
def blogxtract(url):
    
    problemchars = re.compile(r'[\[=\+/&<>;:!\\|*^\'"\?%#$@)(_\,\.\t\r\n0-9-—\]]')
    prochar = '[(=\-\+\:/&<>;|\'"\?%#$@\,\._)]'
    like = re.compile(r'(.*)(?= L)')
    comment = re.compile(r'(.*)(?= C)')
    share = re.compile(r'(?<=Comments )(.*)(?= S)')
    
    global blog_list 
    blog_list = []
        
    global soup    
    
    soup = BeautifulSoup(fb_html(url), "html.parser")
    
    try:
        for i in soup.find_all('div', {"class": "_3w7e"}):

            text_list = []
            text_list_final = []

            #metadata builder
            user = (i.find(re.compile('h1|h3')).text[0:50].lower().encode('ascii', 'ignore').strip() if i.find(re.compile('h1|h3')) is not None else "")
            #link = ("https://m.facebook.com" + i.strong.a['href'] if i.strong is not None else "")
            link = ("https://m.facebook.com/" + url.rsplit('/',2)[1])
            date = (time.strftime("%d/%m/%Y") if 'hr' in (i.find('abbr').get_text() if i.find('abbr') is not None else "") else (i.parent.find('abbr').get_text() if i.parent.find('abbr') is not None else ""))         
            popular = (re.findall(r"[^\W\d_]+|\d+", i.find('div', {"class": "_1fnt"}).get_text()))
            popular_text = ' '.join(popular).replace('LikeCommentShare','')
            react = (re.findall(r"[^\W\d_]+|\d+", i.find('div', {"class": "_1g06"}).get_text()))

            #blog text builder
            for k in i.find_all('p'):
                text_list.append(k.get_text().lower().replace('\n',' ').replace("'", "").encode('ascii', 'ignore').strip() if k is not None else "")


            #replace bad characters in blog text
            for ch in prochar:
                for l in text_list:
                    if ch in l:
                        l = problemchars.sub(' ', l).strip()
                        text_list_final.append(l)

            #build dictionary
            blog_dict = {
            "header": "facebook_group_" + url.rsplit('/',2)[1],
            "url": link,
            "user": user,
            "date": date,
            "popular": popular_text,
            "blog_text": ' '.join(list(OrderedDict.fromkeys(text_list_final))).replace('likes      likes   comments likes      likes likes',''),
            "comment": (int(''.join((comment.findall(str(popular_text)))).replace(' ','')) if len(comment.findall(str(popular_text))) > 0 else ''),
            "share": (int(''.join((share.findall(str(popular_text)))).replace(' ','')) if len(share.findall(str(popular_text))) > 0 else ''),
            "reaction": (int(''.join(react)))
                    }

            blog_list.append(blog_dict)


    #error handling  
    except (AttributeError, TypeError, ValueError):
        print "missing_value"
        
            
    #call csv writer function and output file
    writer_csv_3(blog_list)
    
    return pp.pprint(blog_list[0:2])

    
    
#function to write CSV file
def writer_csv_3(blog_list):
    
    #uses group name from URL to construct output file name
    file_out = "facebook_group_{page}.csv".format(page = url.rsplit('/',2)[1])
    
    with open(file_out, 'w') as csvfile:

        writer = csv.writer(csvfile, lineterminator='\n', delimiter=',', quotechar='"')
        
        writer.writerow(["header", "url", "user", "date", "popualar", "blog_text", "comment", "share", "reaction"])
    
        for i in blog_list:
            if len(i['blog_text']) > 0:
                newrow = i['header'], i['url'], i['user'], i['date'], i['popular'], i['blog_text'], i["comment"], i["share"], i["reaction"]
                writer.writerow(newrow)                     
            #else:
            #    pass
    
    
#tip the domino
if __name__ == "__main__":
    blogxtract(url)