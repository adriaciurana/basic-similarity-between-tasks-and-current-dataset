"""
Cleaning pipeline extractd from:
    https://www.kaggle.com/jonathanbesomi/cord-19-embeddings-from-abstracts-with-spacy
"""

import re
import unidecode

from tqdm import tqdm

import nltk
nltk.download('stopwords')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

tqdm.pandas()

"""
Raw text clean
"""
# Remove empty brackets (that could happen if the contents have been removed already
# e.g. for citation ( [3] [4] ) -> ( ) -> nothing
# https://github.com/jakelever/bio2vec/blob/master/PubMed2Txt.py
def removeBracketsWithoutWords(text):
    fixed = re.sub(r'\([\W\s]*\)', ' ', text)
    fixed = re.sub(r'\[[\W\s]*\]', ' ', fixed)
    fixed = re.sub(r'\{[\W\s]*\}', ' ', fixed)
    return fixed

# Some older articles have titles like "[A study of ...]."
# This removes the brackets while retaining the full stop
# https://github.com/jakelever/bio2vec/blob/master/PubMed2Txt.py
def removeWeirdBracketsFromOldTitles(titleText):
    titleText = titleText.strip()
    if titleText[0] == '[' and titleText[-2:] == '].':
        titleText = titleText[1:-2] + '.'
    return titleText

def remove_citations(input):
    return re.sub(r"(\[\d+\])", "", input)
    fixed = re.sub(r'\([\W\s]*\)', ' ', text)
    fixed = re.sub(r'\[[\W\s]*\]', ' ', fixed)
    fixed = re.sub(r'\{[\W\s]*\}', ' ', fixed)
    return fixed

def remove_pharentesis(input):
    return re.sub(r"(\(|\)|\[|\])", " ", input)

def remove_punctuations(input):
    """Remove punctuations from input"""
    return input.translate(str.maketrans("", "", '!"#$%&\'()_-*+,.:;<=>?@[\\]^`{|}~')) # all string punctuations except '_' and '-'

def remove_numbers(input):
    """Remove numbers that are not close to alphabetic character"""
    return re.sub(r"(\s+\d+\s+|^\d+\s+|\s+\d+$)", "", input)

def remove_diacritics(input):
    """Remove diacritics (as accent marks) from input"""
    return unidecode.unidecode(input)

def remove_white_space(input):
    """Remove all types of spaces from input"""
    input = input.replace(u"\xa0", u" ")  # remove space
    # remove white spaces, new lines and tabs
    return " ".join(input.split())

def remove_stop_words(input):
    """Remove stopwords from input"""
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(input)
    return ' '.join([i for i in words if not (i in stop_words)])


def clean_text(text):
    text = text.lower()
    text = removeBracketsWithoutWords(text)
    text = removeWeirdBracketsFromOldTitles(text)
    text = remove_citations(text)
    text = remove_pharentesis(text)
    text = remove_punctuations(text) # powerful
    text = remove_numbers(text) # only in case SPACE NUM SPACE
    text = remove_diacritics(text)
    text = remove_white_space(text)
    text = remove_stop_words(text)
    
    return text

"""
ToDo Move to nlp pipeline, cleaner solution

import spacy

import nltk
from nltk.corpus import wordnet
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk import WordNetLemmatizer

from gensim.models import Word2Vec
# lazy loading :)
# will trigger data download
def get_pipeline_start():
    nlp = spacy.load('en_core_web_sm')

def clean_pipeline(text):
    nlp = get_pipeline_start()
    nlp.add_pipe()

def get_wordnet_pos(tag):
    if tag.startswith("J"):
        return wordnet.ADJ
    elif tag.startswith("V"):
        return wordnet.VERB
    elif tag.startswith("N"):
        return wordnet.NOUN
    elif tag.startswith("R"):
        return wordnet.ADV
    else:
        return wordnet.NOUN  # NLTK default tag is NOUN

lemmatizer = WordNetLemmatizer()


def lemmatize_word(word, tag):
    return lemmatizer.lemmatize(word, get_wordnet_pos(tag))


def lemmatize(tokens):
    return list(map(lambda x: lemmatize_word(x[0], x[1]), nltk.pos_tag(tokens)))

"""
