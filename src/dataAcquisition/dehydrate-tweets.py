"""
This script takes a directory containing CSV files and dehydrates them by keeping only the tweet_id column.
"""

# ------------------------------------------- IMPORTS ------------------------------------------- #

# External
import os
import pandas as pd
from pathlib import Path
import argparse


# ------------------------------------------- FUNCTIONS ------------------------------------------- #


def process_file(fp):
    df = pd.read_csv(fp)
    tweet_id_df = df[['tweet_id']].dropna().astype(int)
    tweet_id_df.to_csv(fp, index=False)

    print(f'Dehydrated {fp}')
    return tweet_id_df


# ---------------------------------------------- MAIN ---------------------------------------------- #

def main():

    if os.path.isfile(input_):  # Single file
        fp = input_
        tweet_id_df = process_file(fp)

        new_dir = os.path.join(output + "_dehydrated")
        os.makedirs(new_dir, exist_ok=True)

        tweet_id_df.to_csv(os.path.join(new_dir, Path(fp).name), index=False)
    else:
        for root, dirs, files in os.walk(input_):
            for file in files:
                if file.endswith(".csv"):
                    fp = os.path.join(root, file)
                    tweet_id_df = process_file(fp)

                    # Replicate the directory structure in output directory
                    rel_path = os.path.relpath(root, input_)
                    new_dir = os.path.join(output, rel_path + "_dehydrated")
                    os.makedirs(new_dir, exist_ok=True)

                    tweet_id_df.to_csv(os.path.join(new_dir, file), index=False)


# ------------------------------------------- MAIN ------------------------------------------- #

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Dehydrate tweets from a csv file by keeping only tweet_id')

    parser.add_argument('--input', '--i', type=str, help='Directory or CSV file', required=True)
    parser.add_argument('--output', '--o', type=str, help='Directory where you want the dehydrated CSV files',
                        required=True)

    args = parser.parse_args()
    input_ = args.input
    output = args.output

    main()
