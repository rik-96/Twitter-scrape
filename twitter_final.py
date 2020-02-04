import pandas as pd
import time
import csv
from selenium import webdriver
import numpy as np
from datetime import datetime,timedelta

# set chromedriver path
chromedriver_path = 'D:\\Setups\\ChromeDriver\\chromedriver.exe' 

# set url
radius= '30km'

start_date= '2016-03-01'  #set start date
end_date= '2016-03-02'  #set start date

# set sleep delay in seconds according to your internet connection speed
sleep_delay = 4

#locations file
locations = 'loc2.csv'
# locations = '00_all_location_India.csv'

# set hard limit on number of tweets per day per location, set to 0 for infinite tweets per day
tweets_limit = 30

# open chrome driver window
browser = webdriver.Firefox()
# navigate to url
time.sleep(sleep_delay)


start = datetime.strptime(start_date, "%Y-%m-%d")
end = datetime.strptime(end_date, "%Y-%m-%d")

while start < end:
    current = str(start.date())
    nxt = start + timedelta(days=1)  # increase day one by one
    nxts = str(nxt.date())
    print(current)
    start = nxt
    
    with open(locations) as location_file:

        reader =  csv.DictReader(location_file)

        for row in reader:

            longitude = row['longitude']
            latitude = row['latitude']
            print(longitude,latitude)

            url = "https://twitter.com/search?q=geocode%3A"+latitude+"%2C"+longitude+"%2C"+radius+"%20since:"+current+"%20until:"+nxts+"&f=tweets"
            print(url)
            browser.get(url)
            time.sleep(sleep_delay)

            browser_tweet_count = len(browser.find_elements_by_class_name('tweet-text'))
            
            df = pd.DataFrame()
            
            if(browser_tweet_count>0):
                prev = browser_tweet_count
                while(tweets_limit!=0 and browser_tweet_count<tweets_limit):
                    time.sleep(sleep_delay)
                        
                    print(browser_tweet_count , 'tweets, fetching next 20')
                    browser.execute_script("window.scrollTo(0,document.body.scrollHeight);")
                    time.sleep(sleep_delay)

                    browser_tweet_count = len(browser.find_elements_by_class_name('tweet-text'))
                
                    if(browser_tweet_count == prev):
                        break
                        
                    prev = browser_tweet_count

                print(browser_tweet_count , 'tweets')
                

                #operate on tweets
                tweets = browser.find_elements_by_class_name('tweet-text')
                tn = len(tweets)
#                     print(tn)
                dates = browser.find_elements_by_class_name('_timestamp')
                counts = browser.find_elements_by_class_name('ProfileTweet-actionCountForPresentation')
                user = browser.find_elements_by_css_selector('.tweet.js-stream-tweet.js-actionable-tweet.js-profile-popup-actionable.dismissible-content.original-tweet.js-original-tweet')
                timestamp = browser.find_elements_by_css_selector('.tweet-timestamp.js-permalink.js-nav.js-tooltip')
                lang = browser.find_elements_by_css_selector('.TweetTextSize.js-tweet-text.tweet-text')

                tweet_text = [t.text for t in tweets]
                date_text = [t.text for t in dates]
                comments_count = [counts[i*5].text for i in range(tn)]
                comments_count = [t if t!='' else 0 for t in comments_count]
                retweet_count = [counts[i*5+1].text for i in range(tn)]
                retweet_count = [t if t!='' else 0 for t in retweet_count]
                like_count = [counts[i*5+3].text for i in range(tn)]
                like_count = [t if t!='' else 0 for t in like_count]
                tweet_id = [t.get_attribute('data-tweet-id') for t in user]
                item_id = [t.get_attribute('data-item-id') for t in user]
                screen_name = [t.get_attribute('data-screen-name') for t in user]
                name = [t.get_attribute('data-name') for t in user]
                user_id = [t.get_attribute('data-user-id') for t in user]
                time_text = [ t.get_attribute('data-original-title') if(t.get_attribute('data-original-title')) else t.get_attribute('title') for t in timestamp ]
                time_text = [t.split('-')[0].strip() for t in time_text]
                lang_text = [t.get_attribute('lang') for t in lang]


                user_tweets = []
                user_following = []
                user_followers = []
                for i in range(tn):
                    browser.execute_script("document.getElementsByClassName('tweet')["+ str(i) +"].children[1].firstElementChild.firstElementChild.dispatchEvent(new MouseEvent('mouseover',{'bubbles':true}));")
                    time.sleep(sleep_delay)

                    browser.execute_script("x = document.getElementById('profile-hover-container').firstElementChild.children[5].firstElementChild;")

                    user_tweets.append(browser.execute_script("return x.children[0].firstElementChild.children[1].innerText"))
                    user_following.append(browser.execute_script("return x.children[1].firstElementChild.children[1].innerText"))
                    user_followers.append(browser.execute_script("return x.children[2].firstElementChild.children[1].innerText"))



                    browser.execute_script("document.getElementsByClassName('tweet')["+ str(i) +"].children[1].firstElementChild.firstElementChild.dispatchEvent(new MouseEvent('mouseout',{'bubbles':true}));")
                    time.sleep(sleep_delay)

                df['index'] = [i for i in range(tn)] 
                df['date_text'] = date_text
                df['longitude'] = [longitude for i in range(tn)] 
                df['latitude'] = [latitude for i in range(tn)] 
                df['tweet_text'] = tweet_text
                df['comments_count'] = comments_count
                df['retweet_count'] = retweet_count
                df['like_count'] = like_count
                df['tweet_id'] = tweet_id
                df['item_id'] = item_id
                df['screen_name'] = screen_name
                df['name'] = name
                df['user_id'] = user_id
                df['time_text'] = time_text
                df['lang_text'] = lang_text
                df['user_tweets'] = user_tweets
                df['user_following'] = user_following
                df['user_followers'] = user_followers

                #end operate on tweets
        
            with open(current+'_'+longitude+'_'+latitude+'.csv', 'w',encoding='UTF-16') as f:
                df.to_csv(f, index=False)
