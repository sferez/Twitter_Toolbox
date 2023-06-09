"""
Perform data cleaning on the raw linguistic data (tweets).
"""

# -------------------------------------------------- IMPORTS -------------------------------------------------- #

# External
import pandas as pd
import argparse
import os


# ------------------------------------------------- FUNCTIONS ------------------------------------------------- #

def process_file(fp):
    df = pd.read_csv(fp)
    df['class'] = class_
    df.to_csv(fp, index=False)
    print(f'Labelled {fp}')


# ------------------------------------------------- MAIN ------------------------------------------------- #

def main():
    print('Labelling data...')

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
    parser = argparse.ArgumentParser(description='Perform data cleaning on the raw linguistic data.')
    parser.add_argument('--input', '--i', type=str, help='Directory or CSV file', required=True)
    parser.add_argument('--class_', '--c', type=str, help='Class to labelled the data', required=True)

    args = parser.parse_args()

    input_ = args.input
    class_ = args.class_

    main()
