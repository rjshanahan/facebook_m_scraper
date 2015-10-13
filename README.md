## fb webscraper for groups and pages  
  
#### Python web scraper using Selenium and BeautifulSoup modules to extract text from various fb groups and pages.
  
The program uses *<a href="http://www.seleniumhq.org/" target="_blank">Selenium</a>* (and ChromeDriver) to automate user behaviour within a browser session to login to the facebook mobile site, expand collapsible sections for 2015 or load data from dynamic scrolling. Once the pages are rendered the HTML is extracted and sieved through *<a href="http://www.crummy.com/software/BeautifulSoup/bs4/doc/" target="_blank">BeautifulSoup</a>*. Note: fb are smart so this may be a little flaky, but seems to work ok for now.
  
This program will extract the following and output to a CSV file with punctuation and other non-text characters removed:
- full post text from each page of facebook entries
- date
- header
- url
- user name 
- popularity metrics (a string containing likes/comments/shares)
- like_fave: integer value for number of likes
- share_rtwt: integer value for number of shares


![facebook.mobile](https://www.facebook.com/images/fb_icon_325x325.png)

![Selenium Browser Automation](http://www.seleniumhq.org/images/big-logo.png)
