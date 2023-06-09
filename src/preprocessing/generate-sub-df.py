"""
Generate sub-datasets for a CSV file.
Sub-datasets will be grouped by a column and will contain tweet_id and text columns.
"""

# -------------------------------------------------- IMPORTS -------------------------------------------------- #

# External
import pandas as pd
import argparse
import os


# ------------------------------------------------- MAIN ------------------------------------------------- #

def main():
    df = pd.read_csv(input_)
    df = df[['tweet_id', 'text', group_by]]
    if group_by == 'timestamp':
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        if unit == 'D':
            df['timestamp'] = df['timestamp'].dt.date
        elif unit == 'M':
            df['timestamp'] = df['timestamp'].dt.to_period('M')
        elif unit == 'Y':
            df['timestamp'] = df['timestamp'].dt.to_period('Y')
    df = df.groupby(group_by)

    if not os.path.exists(f'{input_[:-4]}_by_{group_by}'):
        os.makedirs(f'{input_[:-4]}_by_{group_by}')

    for group in df.groups:
        if len(df.get_group(group)) < min_size:
            continue
        df.get_group(group).drop(columns=[group_by]).to_csv(f'{input_[:-4]}_by_{group_by}/{group}.csv', index=False)
        print(f'Sub-dataset generated for {group_by} = {group}')


# -------------------------------------------------- CLI -------------------------------------------------- #

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate sub-datasets for a CSV file.')
    parser.add_argument('--input', '--i', type=str, help='CSV file', required=True)
    parser.add_argument('--group-by', '--gb', type=str, help='Column to group by', required=True)
    parser.add_argument('--unit', '--u', type=str,
                        help='If group-by is "timestamp" choose between "D" (day), "M" (month), "Y" (year)',
                        required=False)
    parser.add_argument('--min-size', '--ms', type=int, help='Minimum size of a sub-dataset', default=100,
                        required=False)

    args = parser.parse_args()

    input_ = args.input
    group_by = args.group_by
    min_size = args.min_size
    if group_by == 'timestamp':
        unit = args.unit
        if unit not in ['D', 'M', 'Y']:
            raise ValueError('Add --unit argument. Unit must be one of "D" (day), "M" (month), "Y" (year)')

    main()
