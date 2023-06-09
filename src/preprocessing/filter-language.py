"""
Filter the raw data to only keep tweets in specified languages.
"""

# -------------------------------------------------- IMPORTS -------------------------------------------------- #

# External
import pandas as pd
import os
import argparse

# -------------------------------------------------- GLOBALS -------------------------------------------------- #

LANGUAGES = ['en', 'es', 'fr', 'it', 'de']


# ------------------------------------------------- FUNCTIONS ------------------------------------------------- #


def process_file(fp):
    df = pd.read_csv(fp)

    if 'lang' in df.columns:
        l = len(df)
        df = df[df['lang'].isin(languages)]
        df.to_csv(fp, index=False)
        print(f'Cleaned {os.path.basename(fp)}, {l - len(df)} tweets removed')
    else:
        print(f'No language column (lang) in {os.path.basename(fp)}')


# -------------------------------------------------- MAIN -------------------------------------------------- #


def main():
    print('Filtering data...')

    if os.path.isfile(input_):
        process_file(input_)
    else:
        for root, dirs, files in os.walk(input_):
            for file in files:
                if file.endswith(".csv"):
                    fp = os.path.join(root, file)
                    process_file(fp)


# -------------------------------------------------- CLI -------------------------------------------------- #

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filter the raw data to only keep tweets in specified languages.')
    parser.add_argument('--input', '--i', type=str, help='Directory containing the raw data, or CSV File',
                        required=True)
    parser.add_argument('--languages', '--l', type=str, nargs='+', help='Languages to keep', default=LANGUAGES,
                        required=False)

    args = parser.parse_args()

    input_ = args.input
    languages = args.languages

    main()
