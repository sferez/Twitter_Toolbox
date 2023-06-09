"""
File inspired from Scweet (https://github.com/Altimis/Scweet.git)
Customized for the purpose of this project
"""

import re
import time
from time import sleep
import random
from hashlib import md5
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
import datetime
import pandas as pd
import requests
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from env import get_username, get_password, get_email, get_chromedriver_path

red = "\033[0;91m"
green = "\033[0;92m"
yellow = "\033[0;93m"
blue = "\033[0;94m"


def check_for_error(driver):
    try:
        driver.find_element(By.XPATH, './/span[contains(text(), "Something went wrong")]')
        return True
    except NoSuchElementException:
        return False


def get_data(card, only_id=False):
    """Extract data from tweet card"""

    # try:
    #     username = card.find_element(by=By.XPATH, value='.//span').text
    # except:
    #     return

    # tweet url
    try:
        element = card.find_element(by=By.XPATH, value='.//a[contains(@href, "/status/")]')
        tweet_url = element.get_attribute('href')
    except:
        tweet_url = ""

    # tweet id
    try:
        tweet_id = int(tweet_url.split("/")[-1])
    except:
        tweet_id = ""

    if only_id:
        return [tweet_id]

    try:
        handle = card.find_element(by=By.XPATH, value='.//span[contains(text(), "@")]').text
    except:
        handle = ""

    try:
        user_id = get_user_id(handle)
    except:
        user_id = ""

    try:
        postdate = card.find_element(by=By.XPATH, value='.//time').get_attribute('datetime')
    except:
        postdate = ""

    try:
        text = card.find_element(by=By.XPATH, value='.//div[2]/div[2]/div[2]').text
        if text.startswith("Replying to"):
            try:
                text = card.find_element(by=By.XPATH, value='.//div[2]/div[2]/div[3]').text
            except:
                return
        # Flatten the text
        text = text.replace('\n', ' ')

    except:
        text = ""

    # try:
    #     reply_cnt = card.find_element(by=By.XPATH, value='.//div[@data-testid="reply"]').text
    # except:
    #     reply_cnt = 0
    #
    # try:
    #     retweet_cnt = card.find_element(by=By.XPATH, value='.//div[@data-testid="retweet"]').text
    # except:
    #     retweet_cnt = 0
    #
    # try:
    #     like_cnt = card.find_element(by=By.XPATH, value='.//div[@data-testid="like"]').text
    # except:
    #     like_cnt = 0

    # get a string of all emojis contained in the tweet
    # try:
    #     emoji_tags = card.find_elements(by=By.XPATH, value='.//img[contains(@src, "emoji")]')
    # except:
    #     emoji_tags = ""
    # emoji_list = []
    # for tag in emoji_tags:
    #     try:
    #         filename = tag.get_attribute('src')
    #         emoji = chr(int(re.search(r'svg\/([a-z0-9]+)\.svg', filename).group(1), base=16))
    #     except AttributeError:
    #         continue
    #     if emoji:
    #         emoji_list.append(emoji)
    # emojis = ' '.join(emoji_list)

    tweet = (tweet_id, user_id, postdate, text)
    return tweet


def init_driver(headless=True, proxy=None, show_images=False, option=None, env=None):
    """ initiate a chromedriver or firefoxdriver instance
        --option : other option to add (str)
    """

    options = ChromeOptions()
    driver_path = get_chromedriver_path(env)

    if headless is True:
        print("Scraping on headless mode.")
        # options.add_argument('--disable-gpu')
        options.headless = True
        options.add_argument(
            'user-agent="MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"')
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-extensions")
        options.add_argument("--proxy-server='direct://'")
        options.add_argument("--proxy-bypass-list=*")
        options.add_argument("--start-maximized")
        options.add_argument("--headless")
    else:
        options.headless = False
    options.add_argument('log-level=3')
    if proxy is not None:
        options.add_argument('--proxy-server=%s' % proxy)
        print("using proxy : ", proxy)
    if show_images == False:
        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)
    if option is not None:
        options.add_argument(option)

    driver = webdriver.Chrome(options=options, executable_path=driver_path)

    driver.set_page_load_timeout(100)
    return driver


def get_page(driver, path, retries=3, wait_time=10):
    for _ in range(retries):
        try:
            driver.get(path)
            return path
        except TimeoutException:
            print(f"Timeout exception, waiting for {wait_time} seconds before retrying.")
            time.sleep(wait_time)
    raise TimeoutException(f"Failed to load page after {retries} attempts.")


def log_search_page(driver, since, until_local, lang, display_type, words, to_account, from_account, mention_account,
                    hashtag, filter_replies, proximity,
                    geocode, minreplies, minlikes, minretweets):
    """ Search for this query between since and until_local"""
    # format the <from_account>, <to_account> and <hash_tags>
    from_account = "(from%3A" + from_account + ")%20" if from_account is not None else ""
    to_account = "(to%3A" + to_account + ")%20" if to_account is not None else ""
    mention_account = "(%40" + mention_account + ")%20" if mention_account is not None else ""
    hash_tags = "(%23" + hashtag + ")%20" if hashtag is not None else ""

    if words is not None:
        if len(words) == 1:
            words = "(" + str(''.join(words)) + ")%20"
        else:
            words = "(" + str('%20OR%20'.join(words)) + ")%20"
    else:
        words = ""

    if lang is not None:
        lang = 'lang%3A' + lang
    else:
        lang = ""

    until_local = "until%3A" + until_local + "%20"
    since = "since%3A" + since + "%20"

    if display_type == "Latest" or display_type == "latest":
        display_type = "&f=live"
    elif display_type == "Image" or display_type == "image":
        display_type = "&f=image"
    else:
        display_type = ""

    # filter replies
    if filter_replies == True:
        filter_replies = "%20-filter%3Areplies"
    else:
        filter_replies = ""
    # geo
    if geocode is not None:
        geocode = "%20geocode%3A" + geocode
    else:
        geocode = ""
    # min number of replies
    if minreplies is not None:
        minreplies = "%20min_replies%3A" + str(minreplies)
    else:
        minreplies = ""
    # min number of likes
    if minlikes is not None:
        minlikes = "%20min_faves%3A" + str(minlikes)
    else:
        minlikes = ""
    # min number of retweets
    if minretweets is not None:
        minretweets = "%20min_retweets%3A" + str(minretweets)
    else:
        minretweets = ""

    # proximity
    if proximity == True:
        proximity = "&lf=on"  # at the end
    else:
        proximity = ""

    path = 'https://twitter.com/search?q=' + words + from_account + to_account + mention_account + hash_tags + until_local + since + lang + filter_replies + geocode + minreplies + minlikes + minretweets + '&src=typed_query' + display_type + proximity
    get_page(driver, path)
    return path


def get_last_date_from_csv(path):
    df = pd.read_csv(path)
    r = datetime.datetime.strftime(max(pd.to_datetime(df["timestamp"])), '%Y-%m-%dT%H:%M:%S.000Z')
    del df
    return r


def log_in(driver, env, timeout=20, wait=4):
    email = get_email(env)  # const.EMAIL
    password = get_password(env)  # const.PASSWORD
    username = get_username(env)  # const.USERNAME
    print(f'Logging in with {username}')

    driver.get('https://twitter.com/i/flow/login')

    email_xpath = '//input[@autocomplete="username"]'
    password_xpath = '//input[@autocomplete="current-password"]'
    username_xpath = '//input[@data-testid="ocfEnterTextTextInput"]'

    sleep(random.uniform(15, 15 + 1))

    # enter email
    email_el = driver.find_element(by=By.XPATH, value=email_xpath)
    sleep(random.uniform(wait, wait + 1))
    email_el.send_keys(email)
    sleep(random.uniform(wait, wait + 1))
    email_el.send_keys(Keys.RETURN)
    sleep(random.uniform(wait, wait + 1))
    # in case twitter spotted unusual login activity : enter your username
    if check_exists_by_xpath(username_xpath, driver):
        username_el = driver.find_element(by=By.XPATH, value=username_xpath)
        sleep(random.uniform(wait, wait + 1))
        username_el.send_keys(username)
        sleep(random.uniform(wait, wait + 1))
        username_el.send_keys(Keys.RETURN)
        sleep(random.uniform(wait, wait + 1))
    # enter password
    password_el = driver.find_element(by=By.XPATH, value=password_xpath)
    password_el.send_keys(password)
    sleep(random.uniform(wait, wait + 1))
    password_el.send_keys(Keys.RETURN)
    sleep(random.uniform(wait, wait + 1))


def keep_scroling(driver, data, writer, tweet_ids, scrolling, tweet_parsed, limit, scroll, last_position,
                  only_id=False):
    """ scrolling function for tweets crawling"""

    while scrolling and tweet_parsed < limit:
        sleep(random.uniform(0.5, 1.5))
        # get the card of tweets
        while check_for_error(driver):
            print("Rate limit exceeded, waiting ...")
            time.sleep(60)
            driver.refresh()
            sleep(random.uniform(0.5, 1.5))
        page_cards = driver.find_elements(by=By.XPATH,
                                          value='//article[@data-testid="tweet"]')  # changed div by article
        for card in page_cards:
            tweet = get_data(card, only_id=only_id)
            if tweet:
                # check if the tweet is unique
                tweet_id = tweet[0]
                if tweet_id not in tweet_ids:
                    tweet_ids.add(tweet_id)
                    data.append(tweet)
                    writer.writerow(tweet)
                    tweet_parsed += 1
                    if tweet_parsed >= limit:
                        break
        scroll_attempt = 0
        while tweet_parsed < limit:
            # check scroll position
            scroll += 1
            sleep(random.uniform(0.5, 1.5))
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            curr_position = driver.execute_script("return window.pageYOffset;")
            if last_position == curr_position:
                scroll_attempt += 1
                # end of scroll region
                if scroll_attempt >= 2:
                    scrolling = False
                    break
                else:
                    sleep(random.uniform(0.5, 1.5))  # attempt another scroll
            else:
                last_position = curr_position
                break
    return driver, data, writer, tweet_ids, scrolling, tweet_parsed, scroll, last_position


def get_users_follow(users, headless, env, follow=None, verbose=1, wait=2, limit=float('inf')):
    """ get the following or followers of a list of users """

    # initiate the driver
    driver = init_driver(headless=headless, env=env, firefox=True)
    sleep(wait)
    # log in (the env.env file should contain the username and password)
    # driver.get('https://www.twitter.com/login')
    log_in(driver, env, wait=wait)
    sleep(wait)
    # followers and following dict of each user
    follows_users = {}

    for user in users:
        # if the login fails, find the new log in button and log in again.
        if check_exists_by_link_text("Log in", driver):
            print("Login failed. Retry...")
            login = driver.find_element_by_link_text("Log in")
            sleep(random.uniform(wait - 0.5, wait + 0.5))
            driver.execute_script("arguments[0].click();", login)
            sleep(random.uniform(wait - 0.5, wait + 0.5))
            sleep(wait)
            log_in(driver, env)
            sleep(wait)
        # case 2
        if check_exists_by_xpath('//input[@name="session[username_or_email]"]', driver):
            print("Login failed. Retry...")
            sleep(wait)
            log_in(driver, env)
            sleep(wait)
        print("Crawling " + user + " " + follow)
        driver.get('https://twitter.com/' + user + '/' + follow)
        sleep(random.uniform(wait - 0.5, wait + 0.5))
        # check if we must keep scrolling
        scrolling = True
        last_position = driver.execute_script("return window.pageYOffset;")
        follows_elem = []
        follow_ids = set()
        is_limit = False
        while scrolling and not is_limit:
            # get the card of following or followers
            # this is the primaryColumn attribute that contains both followings and followers
            primaryColumn = driver.find_element(by=By.XPATH, value='//div[contains(@data-testid,"primaryColumn")]')
            # extract only the Usercell
            page_cards = primaryColumn.find_elements(by=By.XPATH, value='//div[contains(@data-testid,"UserCell")]')
            for card in page_cards:
                # get the following or followers element
                element = card.find_element(by=By.XPATH, value='.//div[1]/div[1]/div[1]//a[1]')
                follow_elem = element.get_attribute('href')
                # append to the list
                follow_id = str(follow_elem)
                follow_elem = '@' + str(follow_elem).split('/')[-1]
                if follow_id not in follow_ids:
                    follow_ids.add(follow_id)
                    follows_elem.append(follow_elem)
                if len(follows_elem) >= limit:
                    is_limit = True
                    break
                if verbose:
                    print(follow_elem)
            print("Found " + str(len(follows_elem)) + " " + follow)
            scroll_attempt = 0
            while not is_limit:
                sleep(random.uniform(wait - 0.5, wait + 0.5))
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                sleep(random.uniform(wait - 0.5, wait + 0.5))
                curr_position = driver.execute_script("return window.pageYOffset;")
                if last_position == curr_position:
                    scroll_attempt += 1
                    # end of scroll region
                    if scroll_attempt >= 2:
                        scrolling = False
                        break
                    else:
                        sleep(random.uniform(wait - 0.5, wait + 0.5))  # attempt another scroll
                else:
                    last_position = curr_position
                    break

        follows_users[user] = follows_elem

    return follows_users


def check_exists_by_link_text(text, driver):
    try:
        driver.find_element_by_link_text(text)
    except NoSuchElementException:
        return False
    return True


def check_exists_by_xpath(xpath, driver):
    timeout = 3
    try:
        driver.find_element(by=By.XPATH, value=xpath)
    except NoSuchElementException:
        return False
    return True


def memoize(func):
    """
    :Function: Memoize the function to avoid recomputing the same value, leverage the cache
    :param func: Function to memoize
    :type func: function
    :return: Wrapper function
    :rtype: function
    """
    cache = {}

    def wrapper(*args, **kwargs):
        """
        :Function: Wrapper function for the memoization
        :param args: arguments
        :type args: list
        :param kwargs: keyword arguments
        :type kwargs: dict
        :return: Result of the function
        :rtype: any
        """
        if len(cache) > 0 and len(cache) % 100 == 0:
            cache.clear()
            # print(f"{red}CACHE: Cleared cache")

        key = (func, args, tuple(sorted(kwargs.items())))
        key_hash = md5(str(key).encode('utf-8')).hexdigest()
        if key_hash in cache:
            # print(f"{green}CACHE: Using cache for {func.__name__}, hash: {yellow}{key_hash}")
            return cache[key_hash]
        # print(f"{blue}CACHE: Computing value for {func.__name__}, hash: {yellow}{key_hash} ")
        result = func(*args, **kwargs)
        cache[key_hash] = result
        return result

    return wrapper


@memoize
def get_user_id(username):
    url = "https://tweeterid.com/ajax.php"

    payload = f'input={username}'
    headers = {
        'authority': 'tweeterid.com',
        'accept': '*/*',
        'accept-language': 'fr-FR,fr;q=0.9',
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'origin': 'https://tweeterid.com',
        'referer': 'https://tweeterid.com/',
        'sec-ch-ua': '"Brave";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'sec-gpc': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
    }
    response = requests.request("POST", url, headers=headers, data=payload)

    return int(response.text)


def get_metadata(ids, twarc_session):
    """
    :Function: Get the metadata of the tweets
    :param ids:  List of tweet ids
    :param twarc_session: Twarc session
    :return: List of tweets
    """
    tweet_fields = "lang,created_at,geo"
    expansions = "author_id,geo.place_id"
    place_fields = "country_code,geo,id"
    result = []
    if len(ids) <= 100:
        r = twarc_session.tweet_lookup(ids,
                                       tweet_fields=tweet_fields,
                                       expansions=expansions,
                                       place_fields=place_fields
                                       )
        tweets = list(r)
        for batch in tweets:
            for tweet in batch['data']:
                result.append(tweet)
        return result
    else:
        raise Exception("Too many ids, max 100")
