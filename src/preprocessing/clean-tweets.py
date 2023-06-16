"""
Perform data cleaning on the raw linguistic data (tweets).
"""

# -------------------------------------------------- IMPORTS -------------------------------------------------- #

# External
import pandas as pd
import os
import re
import emoji
from emot.emo_unicode import EMOTICONS_EMO
import argparse
import string
from unidecode import unidecode
from tqdm import tqdm
from pandas.errors import ParserError


# ------------------------------------------------- FUNCTIONS ------------------------------------------------- #

def remove_emoticons(text):
    emoticon_pattern = re.compile(u'(' + u'|'.join(k for k in EMOTICONS_EMO) + u')')
    return emoticon_pattern.sub(r'', text)


def remove_emoji(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)


def remove_urls(text):
    result = re.sub(r"http\S+", "", text)
    return (result)


def remove_twitter_urls(text):
    clean = re.sub(r"pic.twitter\S+", "", text)
    return (clean)


def give_emoji_free_text(text):
    return emoji.replace_emoji(text, replace="")


def remove_mentions(text):
    return re.sub(r'@\w+', '', text)


def to_lowercase(text):
    return text.lower()


def remove_punctuation(text):
    special_chars = "«»"
    return text.translate(str.maketrans('', '', string.punctuation + special_chars))


def remove_extra_spaces(text):
    text = text.replace('  ', ' ')  # 2 spaces
    text = text.replace('   ', ' ')  # 3 spaces
    text = text.replace('    ', ' ')  # 4 spaces
    text = text.replace('     ', ' ')  # 5 spaces
    text = text.replace('      ', ' ')  # 6 spaces
    return text


def remove_accents(text):
    return unidecode(text)


def remove_rt(text):
    if text.startswith('RT '):
        return text[3:]
    return text


def process_file(fp):
    try:
        df = pd.read_csv(fp, encoding='utf-8')
    except ParserError:
        print(f'ParserError: {fp}')
        df = pd.read_csv(fp, lineterminator='\n', encoding='utf-8')

    df.dropna(inplace=True)
    df.drop_duplicates(subset=['tweet_id'], inplace=True)

    df['tweet_id'] = df['tweet_id'].astype(int)
    df['user_id'].replace('error-co', 0, inplace=True)  # Error in the data (user_id = 'error-co')
    df['user_id'] = df['user_id'].astype(int)

    df['text'] = df['text'].str.replace('\n', '')
    df['text'] = df['text'].str.replace('\r', '')

    if urls:
        df['text'] = df['text'].apply(lambda x: remove_urls(x))
        df['text'] = df['text'].apply(lambda x: remove_twitter_urls(x))
    if emojis:
        df['text'] = df['text'].apply(lambda x: remove_emoji(x))
        df['text'] = df['text'].apply(lambda x: give_emoji_free_text(x))
    if mentions:
        df['text'] = df['text'].apply(lambda x: remove_mentions(x))
    if punctuation:
        df['text'] = df['text'].apply(lambda x: remove_punctuation(x))
    if accents:
        df['text'] = df['text'].apply(lambda x: remove_accents(x))
    if rt:
        df['text'] = df['text'].apply(lambda x: remove_rt(x))
    if spaces:
        df['text'] = df['text'].apply(lambda x: remove_extra_spaces(x))
    if lowercase:
        df['text'] = df['text'].apply(lambda x: to_lowercase(x))

    df.to_csv(os.path.join(output_, os.path.basename(fp)), index=False)

    print(f'Cleaned {os.path.basename(fp)}')


# -------------------------------------------------- MAIN -------------------------------------------------- #


def main():
    print('Cleaning data...')
    if not os.path.exists(output_):
        os.makedirs(output_)

    if os.path.isfile(input_):
        process_file(input_)
    else:

        for root, dirs, files in os.walk(input_):
            for file in tqdm(files):
                if file.endswith(".csv"):
                    fp = os.path.join(root, file)
                    process_file(fp)


# -------------------------------------------------- CLI -------------------------------------------------- #

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Perform data cleaning on the raw linguistic data.')
    parser.add_argument('--input', '--i', type=str, help='Directory containing the raw data, or CSV File',
                        required=True)
    parser.add_argument('--output', '--o', type=str, help='Directory to save the scraping-cleaned data.', required=True)

    parser.add_argument('--punctuation', '--p', action=argparse.BooleanOptionalAction, help='Keep punctuation', default=False)
    parser.add_argument('--accents', '--a', action=argparse.BooleanOptionalAction, help='Keep accents', default=False)
    parser.add_argument('--emojis', '--e', action=argparse.BooleanOptionalAction, help='Keep emojis', default=False)
    parser.add_argument('--mentions', '--m', action=argparse.BooleanOptionalAction, help='Keep mentions', default=False)
    parser.add_argument('--urls', '--u', action=argparse.BooleanOptionalAction, help='Keep urls', default=False)
    parser.add_argument('--spaces', '--s', action=argparse.BooleanOptionalAction, help='Keep extra spaces', default=False)
    parser.add_argument('--rt', '--r', action=argparse.BooleanOptionalAction, help='Keep RT', default=False)
    parser.add_argument('--lowercase', '--l', action=argparse.BooleanOptionalAction, help='Keep lowercase', default=False)

    args = parser.parse_args()

    input_ = args.input
    output_ = args.output
    punctuation = not args.punctuation
    accents = not args.accents
    emojis = not args.emojis
    mentions = not args.mentions
    urls = not args.urls
    spaces = not args.spaces
    rt = not args.rt
    lowercase = not args.lowercase

    main()
