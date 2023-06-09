"""
File inspired from Scweet (https://github.com/Altimis/Scweet.git)
Customized for the purpose of this project
"""

# -------------------------------------------- IMPORTS --------------------------------------------------------------- #

# External
import csv
import os
import datetime
import argparse
from time import sleep
import random
import pandas as pd

# Internal
from utils import get_last_date_from_csv, log_search_page, keep_scroling, log_in


# -------------------------------------------- FUNCTIONS ------------------------------------------------------------- #


def scraping(since, until=None, words=None, to_account=None, from_account=None, mention_account=None, interval=5,
             lang=None,
             headless=True, limit=float("inf"), display_type="Top", resume=False, proxy=None, hashtag=None,
             save_dir="outputs", filter_replies=False, proximity=False,
             geocode=None, minreplies=None, minlikes=None, minretweets=None, driver=None, env=None, only_id=False):
    """
    scrape data from twitter using requests, starting from <since> until <until>. The program make a search between each <since> and <until_local>
    until it reaches the <until> date if it's given, else it stops at the actual date.

    return:
    data : df containing all tweets scraped with the associated features.
    save a csv file containing all tweets scraped with the associated features.
    """

    # ------------------------- Variables :
    # header of csv
    if only_id:
        header = ['tweet_id']
    else:
        header = ['tweet_id', "user_id", 'timestamp', 'text']
    # list that contains all data
    data = []
    # unique tweet ids
    tweet_ids = set()
    # write mode
    write_mode = 'w'
    # start scraping from <since> until <until>
    # add the <interval> to <since> to get <until_local> for the first refresh
    # if <until>=None, set it to the actual date
    if until is None:
        until = datetime.date.today().strftime("%Y-%m-%d")
    # set refresh at 0. we refresh the page for each <interval> of time.
    refresh = 0

    # ------------------------- settings :
    # file path
    if words:
        if type(words) == str:
            words = words.split("//")
        path = save_dir + "/" + '_'.join(words) + '_' + str(since).split(' ')[0] + '_' + \
               str(until).split(' ')[0] + '.csv'
    elif from_account:
        path = save_dir + "/" + from_account + '_' + str(since).split(' ')[0] + '_' + str(until).split(' ')[
            0] + '.csv'
    elif to_account:
        path = save_dir + "/" + to_account + '_' + str(since).split(' ')[0] + '_' + str(until).split(' ')[
            0] + '.csv'
    elif mention_account:
        path = save_dir + "/" + mention_account + '_' + str(since).split(' ')[0] + '_' + str(until).split(' ')[
            0] + '.csv'
    elif hashtag:
        path = save_dir + "/" + hashtag + '_' + str(since).split(' ')[0] + '_' + str(until).split(' ')[
            0] + '.csv'
    # create the <save_dir>
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # init the driver
    t = 0
    while t < 5:
        try:
            log_in(driver, env, wait=10)
            break
        except:
            print(f'Error while logging in. Retrying... ({t + 1}/5)')
            sleep(2)
            t += 1
            if t == 5:
                print('Failed to log in. Exiting...')
                raise Exception('Failed to log in.')
            continue

    # resume scraping from previous work
    if os.path.exists(path) and resume and not only_id:
        since = str(get_last_date_from_csv(path))[:10]
        write_mode = 'a'
        print(f'Resuming scraping from {since}...')
    until_local = datetime.datetime.strptime(since, '%Y-%m-%d') + datetime.timedelta(days=interval)

    # start scraping
    with open(path, write_mode, newline='', encoding='utf-8') as f:
        writer = csv.writer(f, escapechar='\\')
        if write_mode == 'w':
            writer.writerow(header)

        # log search page for a specific <interval> of time and keep scrolling unltil scrolling stops or reach the <until>
        while until_local <= datetime.datetime.strptime(until, '%Y-%m-%d'):
            # number of scrolls
            sleep(random.uniform(1, 3))
            scroll = 0
            # convert <since> and <until_local> to str
            if type(since) != str:
                since = datetime.datetime.strftime(since, '%Y-%m-%d')
            if type(until_local) != str:
                until_local = datetime.datetime.strftime(until_local, '%Y-%m-%d')
            # log search page between <since> and <until_local>
            path = log_search_page(driver=driver, words=words, since=since,
                                   until_local=until_local, to_account=to_account,
                                   from_account=from_account, mention_account=mention_account, hashtag=hashtag,
                                   lang=lang,
                                   display_type=display_type, filter_replies=filter_replies, proximity=proximity,
                                   geocode=geocode, minreplies=minreplies, minlikes=minlikes, minretweets=minretweets)
            # number of logged pages (refresh each <interval>)
            refresh += 1
            # number of days crossed
            # days_passed = refresh * interval
            # last position of the page : the purpose for this is to know if we reached the end of the page or not so
            # that we refresh for another <since> and <until_local>
            last_position = driver.execute_script("return window.pageYOffset;")
            # should we keep scrolling ?
            scrolling = True
            print("looking for tweets between " + str(since) + " and " + str(until_local) + " ...")
            # number of tweets parsed
            tweet_parsed = 0
            # sleep 
            sleep(random.uniform(0.5, 1.5))
            # start scrolling and get tweets
            driver, data, writer, tweet_ids, scrolling, tweet_parsed, scroll, last_position = \
                keep_scroling(driver, data, writer, tweet_ids, scrolling, tweet_parsed, limit, scroll, last_position,
                              only_id=only_id)

            # keep updating <start date> and <end date> for every search
            if type(since) == str:
                since = datetime.datetime.strptime(since, '%Y-%m-%d') + datetime.timedelta(days=interval)
            else:
                since = since + datetime.timedelta(days=interval)
            if type(since) != str:
                until_local = datetime.datetime.strptime(until_local, '%Y-%m-%d') + datetime.timedelta(days=interval)
            else:
                until_local = until_local + datetime.timedelta(days=interval)

            print(f'Nb of Tweets : {tweet_parsed}')

    if only_id:
        data = pd.DataFrame(data, columns=['tweet_id'])
    else:
        data = pd.DataFrame(data, columns=['tweet_id', "user_id", 'timestamp', 'text'])

    # close the web driver
    driver.close()

    return data
