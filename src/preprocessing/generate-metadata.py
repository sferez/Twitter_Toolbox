"""
Generate metadata for a CSV file.
Metadata will be the raw dataset without the text column.
"""

# -------------------------------------------------- IMPORTS -------------------------------------------------- #

# External
import pandas as pd
import argparse


# ------------------------------------------------- MAIN ------------------------------------------------- #

def main():
    print('Generating metadata...')

    df = pd.read_csv(input_)
    df = df.drop(columns=['text'])
    df.to_csv(f'{input_[:-4]}_metadata.csv', index=False)
    print(f'Metadata generated for {input_}')


# -------------------------------------------------- CLI -------------------------------------------------- #

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate metadata for a CSV file.')
    parser.add_argument('--input', '--i', type=str, help='CSV file', required=True)

    args = parser.parse_args()

    input_ = args.input

    main()
