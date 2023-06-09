"""
Scrape covid data from github https://github.com/thepanacealab/covid19_twitter
Scrape the dailies and rehydrate them
"""

LANGUAGES = ['en', 'fr', 'es', 'de', 'it']

# ------------------------------------------- IMPORTS -------------------------------------------

# General imports
import datetime
import wget
import gzip
import shutil
import os
import pandas as pd
import twarc
import csv
from tqdm import tqdm
import argparse

# Local imports
from utils import get_metadata
from env import get_consumer_key, get_consumer_secret, get_access_token, get_access_token_secret


# ------------------------------------------- SCRIPT -------------------------------------------

def main():
    for date in range((end_date - start_date).days):
        date = (start_date + datetime.timedelta(days=date)).strftime("%Y-%m-%d")

        url = f'https://github.com/thepanacealab/covid19_twitter/blob/master/dailies/{date}/{date}_clean-dataset.tsv.gz?raw=true'
        wget.download(url, out='temp.tsv.gz')

        with gzip.open('temp.tsv.gz', 'rb') as f_in:
            with open(f'temp.tsv', 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove('temp.tsv.gz')

        df = pd.read_csv('temp.tsv', sep='\t')
        os.remove('temp.tsv')

        if 'lang' in df.columns:
            # Filter by language with english, french, spanish, german and italian
            df = df[df['lang'].isin(languages)]
            print("Data filtered by language")

        if len(df) > max_:
            df = df.sample(max_)
        print(f'Getting data for {date} with {len(df)} tweets')

        if not os.path.exists(f'../../data/covid-github'):
            os.makedirs(f'../../data/covid-github')
        csv_file = open(f'../../data/covid-github/{date}.csv', 'w+', encoding='utf-8')
        csv_writer = csv.writer(csv_file)

        csv_writer.writerow(['tweet_id', 'user_id', 'timestamp', 'text', 'lang'])

        iter = 0
        for batchs in tqdm(range(0, len(df), 100)):
            for tweet in get_metadata(df['tweet_id'].tolist()[batchs:batchs + 100], t):
                if tweet['lang'] in languages:
                    csv_writer.writerow(
                        [tweet['id'], tweet['author_id'], tweet['created_at'], tweet['text'].replace('\n', ''),
                         tweet['lang']])
                    iter += 1

        csv_file.close()
        print(f'Got {iter} tweets\n'
              f'------------------------------------------')


# ------------------------------------------- MAIN -------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Scrape covid data from github repo https://github.com/thepanacealab/covid19_twitter and '
                    'rehydrate it')

    parser.add_argument('--start', '--s', type=str, default='2020-03-22',
                        help='Start date for scraping, format YYYY-MM-DD, min 2020-03-22')
    parser.add_argument('--end', '--e', type=str, default='2023-04-12',
                        help='End date for scraping, format YYYY-MM-DD, max 2023-04-12')
    parser.add_argument('--env', type=str, help='Environment file to get twitter credentials, '
                                                'consumer_key, consumer_secret, access_token, access_token_secret',
                        required=True)
    parser.add_argument('--max', type=int, default=500_000, help='Max number of tweets to get (Default: 500_000)')
    parser.add_argument('--languages', '--l', type=str, nargs='+', help='Languages to keep', default=LANGUAGES,
                        required=False)

    args = parser.parse_args()

    # Set up twarc
    consumer_key = get_consumer_key(args.env)
    consumer_secret = get_consumer_secret(args.env)
    acces_token = get_access_token(args.env)
    acces_token_secret = get_access_token_secret(args.env)
    max_ = args.max
    languages = args.languages
    t = twarc.Twarc2(consumer_key, consumer_secret, acces_token, acces_token_secret)

    # Set up dates
    start_date = datetime.datetime.strptime(args.start, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(args.end, "%Y-%m-%d")

    # Scrape data
    main()
