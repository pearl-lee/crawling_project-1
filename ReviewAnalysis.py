import pymongo
from pymongo import MongoClient
import configparser
import re
import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
from collections import Counter
from wordcloud import WordCloud
from PIL import Image
from bson.binary import Binary

class ReviewAnalysis():
    def __init__(self, section='ju'):
        config = configparser.ConfigParser()
        config.read('login.ini')
        user = config.get(section, 'ID')
        pwd = config.get(section, 'PW')
        ip = config.get(section, 'IP')
        account = f'mongodb://{user}:{pwd}@{ip}'
        self.account = account

    def bring_reviews(self):
        server = pymongo.MongoClient(self.account, 27017) 
        db = server.jobplanet
        review_a = db.collection
        collection = db.review
        rv = pd.DataFrame(list(collection.find()))
        rv = rv[['company_name', 'review_num', 'stats', 'strength', 'title', 'want', 'weakness', 'person']]
        rv.review_num = rv.review_num.apply(lambda x: int(x))
        rv = rv[rv.review_num > 0]
        rv['company_name2'] = rv.company_name.apply(lambda x:  ''.join(re.findall('[가-힣]+', x.replace('(주)', '').replace('(유)', '').replace(' ', '').replace('(', '').replace(')', ''))))

        return rv


    def pros_and_cons(self, company):
        """
        return company pros and cons wordcloud images
        input =>
            - rv : review DataFrame 
            - company : company_name2
        """
        rv = bring_reviews('ju')
        pros = list(rv[rv.company_name2 == company].strength)[0][0]
        pros = re.sub('[0-9][.]', '', pros)
        pros = pros.replace('|', ' ').replace('/', ' ').replace('(', ' ').replace(')', ' ').replace('-', ' ')

        cons = list(rv[rv.company_name2 == company].weakness)[0][0]   
        cons = re.sub('[0-9][.]', '', cons)
        cons = cons.replace('|', ' ').replace('/', ' ').replace('(', ' ').replace(')', ' ').replace('-', ' ')

        # 토큰화, 2글자 이상만 추출
        token_p = word_tokenize(pros)
        token_p = [t for t in token_p if len(t) >= 2]
        token_c = word_tokenize(cons)
        token_c = [t for t in token_c if len(t) >= 2]

        # 불용어 제거
        stop = open('./review_stopwords.txt', 'r').read().split(' ')
        token_pr = [t for t in token_p if not t in stop]
        token_cr = [t for t in token_c if not t in stop]

        # 사용빈도 카운트
        count_p = Counter(token_pr)
        tags_p = count_p.most_common(100)
        count_c = Counter(token_cr)
        tags_c = count_c.most_common(100)

        # 시각화
        path = '/System/Library/Fonts/Supplemental/AppleGothic.ttf'
        thumbsup = np.array(Image.open('./thumbsup.png'))
        thumbsdown = np.array(Image.open('./thumbsdown.png'))
        wordcolud1 = WordCloud(font_path=path, mask=thumbsup, 
                               background_color='white', colormap='Blues', width=80, height=80, stopwords=stop, prefer_horizontal=0.9)
        cloud1 = wordcolud1.generate_from_frequencies(dict(tags_p))


        wordcolud2 = WordCloud(font_path=path, mask=thumbsdown, 
                               background_color='white', colormap='Reds', width=80, height=80, stopwords=stop, prefer_horizontal=0.0)
        cloud2 = wordcolud2.generate_from_frequencies(dict(tags_c))

        plt.figure(figsize=(7, 4))
        plt.subplot(121)
        plt.axis('off'); plt.imshow(cloud1)

        plt.subplot(122)
        plt.axis('off'); plt.imshow(cloud2)

        plt.suptitle(f'<{company}의 장단점>', size=14)
        plt.tight_layout()
        plt.savefig(f'./pros_and_cons/{company}.png')
        plt.show()


    def save_to_mongodb_ra(self, section): 
        """
        Save review analysis image to mongodb
        section => 
            - 'ju' : juhyun's server
            - 'jin': jinju's server
        """
        server = pymongo.MongoClient(self.account, 27017) 
        db = server.jobplanet
        collection_a = db.review_a
        rv = bring_reviews('ju')
        companies = list(rv.company_name2.unique())
        for company in companies:
            try:
                img = open(f'./pros_and_cons/{company}.png', mode='rb').read()
                review = {
                    "company_name": company,
                    "analysis": Binary(img)
                }
                collection_a.insert_one(review)
            except:
                continue
