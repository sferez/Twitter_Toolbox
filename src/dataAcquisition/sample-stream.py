"""
Script to get a sample of the Twitter stream, using the Twitter API v2.
Gather 1% of the real-time stream of Tweets based on a sample of all Tweets.
Filter by language and save the data in a csv file.
"""

# ------------------------------------------- IMPORTS ----------------------------------------------------- #

# External
import requests
import os
import json
import csv
import datetime
import sys
import argparse
import time

# Internal
from env import get_bearer_token

# ------------------------------------------- CONSTANTS --------------------------------------------------- #

LANGUAGES = ['en', 'fr', 'es', 'de', 'it']


# ------------------------------------------- FUNCTIONS ------------------------------------------------------ #

def create_url():
    # Add the parameters you want to the URL
    tweet_fields = "tweet.fields=lang,created_at"
    expansions = "expansions=author_id"
    user_fields = "user.fields="
    place_fields = "place.fields="
    media_fields = "media.fields="
    url = f"https://api.twitter.com/2/tweets/sample/stream?{tweet_fields}&{expansions}&{user_fields}&{place_fields}&{media_fields}"
    return url


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2SampledStreamPython"
    return r


def check_date():
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    global date, csv_file, csv_writer, iter_
    if current_date != date:
        csv_file.close()
        date = current_date
        filename = '../../data/sample-stream/' + date + '.csv'
        csv_file = open(filename, 'a+', encoding='utf-8')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['tweet_id', 'user_id', 'timestamp', 'text', 'lang'])
        iter_ = {l: 0 for l in languages}
        print(f'New date: {date}, reseting iter_')


def connect_to_endpoint(url):
    global iter_
    response = requests.request("GET", url, auth=bearer_oauth, stream=True)
    if response.status_code != 200:
        raise Exception(
            "Request returned an error: {} {}".format(
                response.status_code, response.text
            )
        )

    if languages[0] == 'all':
        for response_line in response.iter_lines():
            if response_line:
                json_response = json.loads(response_line)
                tweet_data = json_response.get('data', {})
                if tweet_data:
                    if iter_['all'] >= iter_max:
                        continue
                    iter_['all'] += 1

                lang = tweet_data.get('lang')
                tweet_id = tweet_data.get('id')
                author_id = tweet_data.get('author_id')
                timestamp = tweet_data.get('created_at')
                text = tweet_data.get('text', "").replace('\n', ' ')
                location = tweet_data.get('location', "")
                print(location)

                check_date()
                csv_writer.writerow([tweet_id, author_id, timestamp, text, lang])
                sys.stdout.write('\r')
                sys.stdout.write(f'Gathered {iter_["all"]} tweets')

    else:
        for response_line in response.iter_lines():
            if response_line:
                json_response = json.loads(response_line)
                tweet_data = json_response.get('data', {})
                if tweet_data:
                    lang = tweet_data.get('lang')
                    if lang not in languages or iter_[lang] >= iter_max:
                        continue
                    iter_[lang] += 1

                    tweet_id = tweet_data.get('id')
                    author_id = tweet_data.get('author_id')
                    timestamp = tweet_data.get('created_at')
                    text = tweet_data.get('text', "").replace('\n', ' ')

                    check_date()
                    csv_writer.writerow([tweet_id, author_id, timestamp, text, lang])
                    sys.stdout.write('\r')
                    msg = f'{" ".join([f"{l}: {iter_[l]}" for l in iter_])}'
                    sys.stdout.write(msg)


# ------------------------------------------- MAIN ----------------------------------------------------------- #

def main():
    url = create_url()
    timeout = 0
    while True:
        try:
            connect_to_endpoint(url)
        except KeyboardInterrupt:
            print("\nReceived interrupt, stopping...")
            csv_file.close()
            sys.exit(0)
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            timeout += 1
            print(f'\nTimeout: {timeout}, restarting stream...')
            time.sleep(5)  # adjust this value according to your needs


# ------------------------------------------- RUN ----------------------------------------------------------- #


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sample Twitter Stream, get 1% of current tweets')

    parser.add_argument('--iter_max', type=int, default=1_000_000, help='Maximum number of tweets to get per language')
    parser.add_argument('--languages', '--l', type=str, nargs='+', help='Languages to keep', default=LANGUAGES,
                        required=False)
    parser.add_argument('--env', type=str, required=True, help='Path to env file, containing bearer token')

    args = parser.parse_args()

    iter_max = args.iter_max
    languages = args.languages
    env = args.env
    bearer_token = get_bearer_token(env)

    iter_ = {k: 0 for k in languages}

    date = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = '../../data/sample-stream/' + date + '.csv'

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    if not os.path.exists('../../data/sample-stream'):
        os.makedirs('../../data/sample-stream')

    if not os.path.exists(filename):
        csv_file = open(filename, 'w+', encoding='utf-8')
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['tweet_id', 'user_id', 'timestamp', 'text', 'lang'])
    else:
        csv_file = open(filename, 'a+', encoding='utf-8')
        csv_writer = csv.writer(csv_file)

    main()
