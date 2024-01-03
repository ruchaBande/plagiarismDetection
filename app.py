import nltk
nltk.download('punkt')
import streamlit as st
import pandas as pd
from nltk import tokenize
from bs4 import BeautifulSoup
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_sentences(text):
    sentences = tokenize.sent_tokenize(text)
    return sentences

def get_url(sentence):
    base_url = 'https://papersowl.com/plagiarism-checker-send-data'
    # query = sentence
    # query = query.replace(' ', '+')
    url = base_url 
    # + query
    headers= {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0",
        "Accept": "/",
        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "https://papersowl.com/free-plagiarism-checker",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": "https://papersowl.com",
        "Dnt": "1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "no-cors",
        "Sec-Fetch-Site": "same-origin",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Te": "trailers",
        "Connection": "close",
    }

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    divs = soup.find_all('div', class_='yuRUbf')
    urls = []
    for div in divs:
        a = div.find('a')
        urls.append(a['href'])
    if len(urls) == 0:
        return None
    elif "youtube" in urls[0]:
        return None
    else:
        return urls[0]
    

    
def get_text(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = ' '.join(map(lambda p: p.text, soup.find_all('p')))
    return text

def get_similarity(text1, text2):
    text_list = [text1, text2]
    cv = CountVectorizer()
    count_matrix = cv.fit_transform(text_list)
    similarity = cosine_similarity(count_matrix)[0][1]
    return similarity

def get_similarity_list(text, url_list):
    similarity_list = []
    for url in url_list:
        text2 = get_text(url)
        similarity = get_similarity(text, text2)
        similarity_list.append(similarity)
    return similarity_list

st.set_page_config(page_title='Plagiarism Detection')
st.title('Plagiarism Detection')

st.write("""
### Enter the text to check for plagiarism
""")
text = st.text_area("Enter text here", height=200)

url = []

if st.button('Check for plagiarism'):
    st.write("""
    ### Checking for plagiarism...
    """)
    sentences = get_sentences(text)
    for sentence in sentences:
        url.append(get_url(sentence))
    if None in url:
        st.write("""
        ### No plagiarism detected!
        """)
        st.stop()
    similarity_list = get_similarity_list(text, url)
    df = pd.DataFrame({'Sentence': sentences, 'URL': url, 'Similarity': similarity_list})
    df = df.sort_values(by=['Similarity'], ascending=False)
    df = df.reset_index(drop=True)
    st.table(df)
    
