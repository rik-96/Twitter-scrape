import time
import csv
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

browser = webdriver.Firefox()
query = 'geocode%3A35.68501%2C139.7514%2C30km%20since:2016-03-01%20until:2016-03-02&f=tweets'
url = 'https://twitter.com/search?q=' + query
browser.get(url)
time.sleep(1)

body = browser.find_element_by_tag_name('body')
for _ in range(20):
    #body.send_keys(Keys.END)
    browser.execute_script("window.scrollTo(0,document.body.scrollHeight);")
    time.sleep(0.2)
tweets = browser.find_elements_by_class_name('tweet-text')
users = browser.find_elements_by_class_name('username')
times = browser.find_elements_by_class_name('_timestamp')
with open('tweet.csv', 'w') as file:
    fieldnames = ['username', 'time', 'tweet']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    for tweet,user,time in zip(tweets,users,times):
        
        writer.writerow({'username' : user.text, 'time' : time.text, 'tweet' : tweet.text})
