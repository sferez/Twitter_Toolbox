"""
Topic NLP detection

Based on TweetNLP: Cutting-Edge Natural Language Processing for Social Media.
Camacho-Collados, J., Rezaee, K., Riahi, T., Ushio, A., Loureiro, D., Antypas, D., Boisson, J., Espinosa-Anke, L.,
Liu, F., Martinez-Cámara, E., & others (2022).
In Proceedings of the 2022 Conference on Empirical Methods in Natural Language Processing: System Demonstrations.
Association for Computational Linguistics.
"""

# ----------------------------------------------- IMPORTS ----------------------------------------------- #

# External
import argparse
import pandas as pd
import os
from tqdm import tqdm
import tweetnlp


# ---------------------------------------------- FUNCTIONS ---------------------------------------------- #


def detect_topic(text):
    topic = model.predict(text)

    if len(topic['label']) == 0:
        topic['label'] = ['und']

    return label_to_id[topic['label'][0]]


def process_file(fp):
    df = pd.read_csv(fp)

    if 'topic' in df.columns and not force:
        if df['topic'].isnull().sum() == 0:
            print('Already detected')
            return

    df['text'] = df['text'].astype(str)  # Avoids errors in the detection
    tqdm.pandas()
    df['topic'] = df['text'].progress_apply(detect_topic)

    df.to_csv(fp, index=False)


# ------------------------------------------------- MAIN ------------------------------------------------- #


def main():
    print(f'Topic detection on {input_}...')

    if os.path.isfile(input_):  # Single file
        fp = input_
        process_file(fp)
    else:
        for root, dirs, files in os.walk(input_):
            for file in files:
                if file.endswith(".csv"):
                    print(file)
                    fp = os.path.join(root, file)
                    process_file(fp)


# -------------------------------------------------- CLI -------------------------------------------------- #


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Apply NLP Topic detection to a CSV file.')

    parser.add_argument('--input', '--i', type=str, help='Directory or CSV File', required=True)
    parser.add_argument('--force', '--fo', action=argparse.BooleanOptionalAction, help='Force detection', default=False)

    args = parser.parse_args()
    input_ = args.input
    force = args.force

    model = tweetnlp.load_model('topic_classification')

    # /!\ Note: Id 0 is reserved for the 'und' label, All the other labels are shifted by 1 /!\
    label_to_id = {v: int(k) + 1 for k, v in model.id_to_label.items()}
    label_to_id['und'] = 0
    # 1: arts_&_culture
    # 2: business_&_entrepreneurs
    # 3: celebrity_&_pop_culture
    # 4: diaries_&_daily_life
    # 5: family
    # 6: fashion_&_style
    # 7: film_tv_&_video
    # 8: fitness_&_health
    # 9: food_&_dining
    # 10: gaming
    # 11: learning_&_educational
    # 11: music
    # 13: news_&_social_concern
    # 14: other_hobbies
    # 15: relationships
    # 16: science_&_technology
    # 17: sports
    # 18: travel_&_adventure
    # 19: youth_&_student_life

    main()
