"""
Language NLP detection

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
from lingua import Language, LanguageDetectorBuilder
from tqdm import tqdm

# ---------------------------------------------- CONSTANTS ---------------------------------------------- #

# List of languages to use for detection (can be changed)
LANGUAGES = [Language.ENGLISH, Language.FRENCH, Language.GERMAN, Language.ITALIAN, Language.SPANISH]


# ---------------------------------------------- FUNCTIONS ---------------------------------------------- #


def detect_language(text):
    result = detector.detect_language_of(text)
    if result:
        conf = detector.compute_language_confidence(text, result)
        if conf > 0.90:
            return result.iso_code_639_1.name.lower()
    return 'und'


def process_file(fp):
    df = pd.read_csv(fp)

    if 'lang' in df.columns:
        if df['lang'].isnull().sum() == 0:
            print('Already detected')
            return

    df['text'] = df['text'].astype(str)  # Avoids errors in the detection
    tqdm.pandas()
    df['lang'] = df['text'].progress_apply(detect_language)

    df.to_csv(fp, index=False)


# ------------------------------------------------- MAIN ------------------------------------------------- #


def main():
    print(f'Language detection on {input_}...')

    if os.path.isfile(input_):  # Single file
        fp = input_
        process_file(fp)
    else:
        for root, dirs, files in os.walk(input_):  # Directory
            for file in files:
                if file.endswith(".csv"):
                    print(file)
                    fp = os.path.join(root, file)
                    process_file(fp)


# -------------------------------------------------- CLI -------------------------------------------------- #


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Apply NLP language detection to a CSV file.')

    parser.add_argument('--input', '--i', type=str, help='Directory or CSV File', required=True)
    parser.add_argument('--fast', '--fa', action=argparse.BooleanOptionalAction, help='Use fast language detection',
                        default=False)
    parser.add_argument('--force', '--fo', action=argparse.BooleanOptionalAction, help='Force detection', default=False)

    args = parser.parse_args()

    input_ = args.input
    fast = args.fast
    force = args.force

    if fast:
        print('Using fast language detection')
        detector = LanguageDetectorBuilder.from_languages(*LANGUAGES).with_low_accuracy_mode().build()
    else:
        detector = LanguageDetectorBuilder.from_languages(*LANGUAGES).build()

    # If you want to use all languages, uncomment the following line and comment the previous one
    # detector = LanguageDetectorBuilder.from_all_languages().with_preloaded_language_models().build()

    main()
