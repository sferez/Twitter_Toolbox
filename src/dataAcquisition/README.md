# Data Acquisition

Collect data from Twitter using scraping, streaming and Twitter API.

## OVERVIEW

This folder contains the following functionalities:

- [Scraping](#scraping) - Collect data from Twitter using scraping
- [Streaming](#streaming) - Collect data from Twitter using streaming (1% of current tweets)
- [Covid-19](#covid-19) - Collect data from the covid-19 github repository and rehydrate the tweets
- [Hydrate Tweets](#hydrate-tweets) - Hydrate a csv file containing tweet_id
- [Dehydrate Tweets](#dehydrate-tweets) - Dehydrate a csv file containing tweet_id

## Setup

Have a .env file with the following variables:

For scraping:

```
USERNAME=<username>
PASSWORD=<password>
EMAIL=<email>
CHROME_DRIVER_PATH=<path to chrome driver>
```

For Streaming

```
BEARER_TOKEN=<bearer token>
```

For Twitter API (Hydrate, Dehydrate, Covid-19)

```
CONSUMER_KEY=<consumer key>
CONSUMER_SECRET=<consumer secret>
ACCESS_TOKEN=<access token>
ACCESS_TOKEN_SECRET=<access token secret>
```


## Scraping

To scrape data from Twitter, run the following file:

```
src/dataAcquisition/run-scraping.py
```

With the following arguments:

```
# Seach type (Only one of the following):
--from_account, --a: Account to monitor
--hashtag, --h: Hashtag to monitor
--word, --w: Word to monitor

# Other arguments Mandatory:
--env: Environment to use with username, password and email
--start, --s: Start date of the scraping

# Other arguments Optional:
--end, --e: End date of the scraping (Default: Today)
--interval, --i: Interval of the scraping (Default: 1 day)
--headless: Run the scraping in headless mode 
--only_id: Flag to indicate if only the tweet id should be scraped
```

The data will be saved in the following path:

```
data/<user>/<user>_<start>_<end>.csv
```

The data will be saved in the following format:

```
tweet_id,user_id,timestamp,text
```

Command example:

```
python3 src/dataAcquisition/run-scraping.py --from_account elonmusk --env .env --start 2020-01-01 --end 2023-01-01  --headless
```

Note: Languages are not collected by scraping. You can add the language by hydrating the tweets (see below), or by applying a nlp model to the text.

## Streaming

To stream data from Twitter (gather data in real time, 1% of current tweet), run the following file:

```
src/dataAcquisition/sample-stream.py
```

With the following arguments:

```
# Arguments Mandatory:
--env: Environment to use with bearer token

# Arguments Optional:
--languages, --l: Languages to stream (Default: en, fr, es, de, it)
--iter_max: Maximum number of iterations for each language (Default: 1_000_000)
```

The data will be saved in the following path:

```
data/sample_stream/<date>.csv
```

The data will be saved in the following format:

```
tweet_id,user_id,timestamp,text,lang
```

Command example:

```
python3 src/dataAcquisition/sample-stream.py --env .env 
```

Note: For keeping all the languages, you can use the following argument:

```
--languages all
```

## Covid-19

Gather data from the covid-19 github repository and rehydrate the tweets, run the following file:

```
src/dataAcquisition/scrape-covid-github.py
```

With the following arguments:

```
# Arguments Mandatory:
--env: Environment to use with credentials (access_token, access_token_secret, consumer_key, consumer_secret)

# Arguments Optional:
--start: Start date of the scraping (Default: 2020-03-22)
--end: End date of the scraping (Default: 2023-04-12)
```

The data will be saved in the following path:

```
data/covid_github/<date>.csv
```

The data will be saved in the following format:

```
tweet_id,user_id,timestamp,text,lang
```

Command example:

```
python3 src/dataAcquisition/scrape-covid-github.py --env .env --start 2020-03-22 --end 2021-01-01
```

Note: Only LANGUAGES = ['en', 'fr', 'es', 'de', 'it'] are kept. You can change the languages in the code.

## Hydrate Tweets

To hydrate a csv file containing tweet_id, run the following file:

```
src/dataAcquisition/hydrate-tweets.py
```

With the following arguments:

```
# Arguments Mandatory:
--env: Environment to use with credentials (access_token, access_token_secret, consumer_key, consumer_secret)
--file, --f: File to hydrate (CSV with a column named tweet_id)
```

The data will be saved in the following path:

```
<file>_hydrated.csv
```

The data will be saved in the following format:

```
tweet_id,user_id,timestamp,text,lang
```

Command example:

```
python3 src/dataAcquisition/hydrate-tweets.py --env .env --file data/elonmusk/elonmusk_2020-01-01_2023-01-01.csv
```

## Dehydrate Tweets

To dehydrate a csv file containing tweet_id, run the following file:

```
src/dataAcquisition/dehydrate-tweets.py
```

With the following arguments:

```
# Arguments Mandatory:
--input_dir, --i: Directory containing the files to dehydrate
--output_dir, --o: Directory to save the dehydrated files
```

The data will be saved in the following path (sub-structure folders included):

```
<output_dir>/<file>_dehydrated.csv
```

The data will be saved in the following format:

```
tweet_id
```

Command example:

```
python3 src/dataAcquisition/dehydrate-tweets.py --input_dir data/scraping --output_dir data/scraping_dehydrated
```


## Class:

1 - Personalities
2 - News and Media
3 - Stream
4 - Covid-19

## Data Storage

Data is stored in the following structure:

```
├── data
│   ├── <scraping> (Scrape from user, hashtag or keyword)
│   │   ├── <user>
│   │   │   ├── <user>_<start>_<end>.csv
│   │   │   ├── <user>_<start>_<end>.csv
│   │   │   └── ...
│   │   ├── <hashtag>
│   │   │   ├── <hashtag>_<start>_<end>.csv
│   │   │   ├── <hashtag>_<start>_<end>.csv
│   │   │   └── ...
│   │   └── ...
│   ├── <sample-stream> (Stream 1% of tweets)
│   │   ├── <date>.csv
│   │   ├── <date>.csv
│   │   └── ...
│   ├── <covid-github> (Scrape from Github and rehydrate)
│   │   ├── <date>.csv
│   │   ├── <date>.csv
│   │   └── ...
│   └──
└──
```

