import jieba
from collections import Counter
import pandas as pd
import re
import string
import requests
import streamlit as st
from streamlit_echarts import st_echarts
from bs4 import BeautifulSoup

custom_words = ["对比研究", "非言语", "教学研究", "影响研究", "多模态研究", "行为研究", "编码与分析", "评价研究",
                "影响",
                "应用调查", "调查研究", "案例研究", "作用"]

for word in custom_words:
    jieba.add_word(word)


def load_stop_words():
    stop_words = []
    with open('stop_words.txt', 'r', encoding='utf-8') as f:
        for line in f:
            stop_words.append(line.strip())
    return stop_words


stopwords = load_stop_words()


def remove_stopwords(text, stopwords):
    words = text.split()
    cleaned_words = [word for word in words if word.lower() not in stopwords]
    return ' '.join(cleaned_words)


def remove_punctuation(text):
    return text.translate(str.maketrans('', '', string.punctuation))


def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
    text = text.strip()  # Remove leading/trailing whitespace
    return text


def segment(text):
    words = jieba.cut(text, cut_all=False)
    word_list = [word for word in words if word not in stopwords]
    return word_list


def remove_html_tags(text):
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)


def extract_body_text(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.find('body').get_text()
    return text


def run():
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )
    st.write("# Welcome to Streamlit! 👋")
    url = st.text_input('Enter URL:')
    if url:
        r = requests.get(url)
        r.encoding = 'utf-8'
        text = r.text
        text = extract_body_text(text)
        text = remove_html_tags(text)  # Remove HTML tags from the extracted text
        text = remove_punctuation(text)  # Remove punctuation before further processing
        text = clean_text(text)
        words = segment(text)
        word_counts = Counter(words)
        top_words = word_counts.most_common(20)

        wordcloud_options = {
            "tooltip": {
                "trigger": 'item',
                "formatter": '{b} : {c}'
            },
            "xAxis": [{
                "type": "category",
                "data": [word for word, count in top_words],
                "axisLabel": {
                    "interval": 0,
                    "rotate": 30
                }
            }],
            "yAxis": [{"type": "value"}],
            "series": [{
                "type": "bar",
                "data": [count for word, count in top_words]
            }]
        }

        st_echarts(wordcloud_options, height='500px')


if __name__ == "__main__":
    run()
