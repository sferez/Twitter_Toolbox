# Twitter Toolbox

Welcome to the Twitter Toolbox, a comprehensive suite designed to simplify data acquisition, preprocessing, and analysis
from Twitter. This project is an up-to-date solution built in response to the recent changes in Twitter's API and front
end. Given that several existing libraries are no longer maintained or updated, this Twitter Toolbox ensures a seamless
data extraction process for data analysts, researchers, marketers, and developers alike.

## Features

The Twitter Toolbox offers a broad spectrum of functionalities, including:

**Data Acquisition**: Our toolbox equips you with everything you need to extract a variety of data from Twitter, from
streaming and scraping real-time data to making API calls and hydrating or dehydrating tweets.

**Preprocessing**: Our tools offer data cleaning, language filtering, data labeling, and group generation features to
refine
your dataset for accurate and reliable analyses.

**Natural Language Processing** (NLP): The toolbox is equipped with sentiment analysis, emotion analysis, topic
analysis,
and named entity recognition to provide you with meaningful insights from the content of tweets.

Each of these capabilities is designed to help you make the most out of Twitter data, whether you're exploring public
sentiment, detecting emotional trends, identifying key themes, or recognizing named entities such as organizations or
individuals.

## Data Acquisition

Collect data from Twitter using scraping, streaming and Twitter API.

Learn more about the data
collection [here](https://github.com/sferez/Noisy_Entropy_Estimation/tree/main/src/dataAcquisition).

## Preprocessing

In progress...

## NLP

In progress...

## Future Developments
The Twitter Toolbox is an evolving project. We plan to continue adding new features as they are developed. Stay tuned
for regular updates and improvements!

## Contributions and Feedback
This toolbox is designed to grow with the contributions and feedback from the community. You are welcome to suggest new
features, report any issues, or even submit pull requests. Let's collaborate to create the most valuable Twitter Toolbox
possible!

## Disclaimer
Please note that the use of the Twitter API and all data retrieved through this toolbox should comply with the Twitter
Terms of Service, Developer Agreement, and Developer Policy, including Twitter's privacy policy. This project includes a
dehydration script to comply with Twitter's terms of service, allowing for sharing only the tweet_id. Always de-identify
the information and respect user privacy when sharing or publishing data.

## Structure

Project is structured as follows:

```
├── data (Data is not stored in the repository)
├── src
│   ├── dataAcquisition
│   ├── preprocessing
│   ├── nlp
├── docs 
└──
```

Data is stored in the following structure:

```
├── data
│   ├── <scraping> (Scrape from user, hashtag or keyword)
│   │   ├── <user>
│   │   │   ├── <user>_<start>_<end>.csv
│   │   │   ├── <user>_<start>_<end>.csv
│   │   │   └── ...
│   │   ├── <user>
│   │   │   ├── <user>_<start>_<end>.csv
│   │   │   ├── <user>_<start>_<end>.csv
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

