from konlpy.tag import Okt
from collections import Counter
import pandas as pd
import re
from datetime import datetime, timedelta

okt  = Okt()

stopwords =  set(['있습니다', '합니다', '기자', '보도', '있다', '이번', '이후', '대한', '오늘', '지난'])

def clean_text(text):
    text = re.sub(r'[^가-힣\s]', ' ', text)  # 한글과 공백만 남김
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def extract_nouns(text):
    nouns = okt.nouns(text)
    nouns = [n for n in nouns if len(n) > 1 and n not in stopwords]
    return nouns

def process_new_file(date_str):
    print("hello")
    csv_path = f'data/naver_top30_news_{date_str}.csv'
    df = pd.read_csv(csv_path)
    word_counter = Counter()

    for content in df['content']:
        clean = clean_text(str(content))
        nouns = extract_nouns(clean)
        word_counter.update(nouns)
    
    result_df = pd.DataFrame(word_counter.items(), columns=['word', 'count'])
    result_df.insert(0, 'date', date_str) # 날짜 추가

    out_path = f'data/naver_news_{date_str}.csv'
    result_df.to_csv(out_path, index=False, encoding='utf-8-sig')
    print(f"[INFO] 저장 완료: {out_path}")

    return out_path

if __name__ == "__main__":
    date_str = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
    
    process_new_file(date_str)