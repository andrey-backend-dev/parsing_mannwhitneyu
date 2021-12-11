# install needed libraries
# pip install requests bs4 lxml pandas scipy
# import needed libraries
import random
import pandas as pd
import requests
from bs4 import BeautifulSoup as BS
import time
from scipy.stats import mannwhitneyu


def parse_kinopoisk(page: int = 1):
    old_rate_list = []
    new_rate_list = []
    film_list = []
    while True:
        if page > 5:
            break
        s = requests.get(f'https://www.kinopoisk.ru/lists/top250/?page={page}&tab=all')
        soup = BS(s.content, 'lxml')
        film_list.extend(list(map(lambda x: x.text, soup.find_all(class_="selection-film-item-meta__name"))))
        old_rate_list.extend(list(map(lambda x: x.text, soup.find_all(class_="selection-film-item-poster__rating"))))
        new_rate_list.extend(list(map(lambda x: x.text, soup.find_all(class_="rating__value"))))
        page += 1
        # random.randint(1, 4) for the emulation of human's behavior
        time.sleep(random.randint(1, 4))
    df = pd.DataFrame({'Film': film_list, 'Old Rating': old_rate_list, 'New Rating': new_rate_list})
    df.dropna()
    if df.empty:
        raise Warning('Your DataFrame is empty!\nFailed to parse kinopoisk. It could happened because of captcha.')
    df.to_csv('data-kinopoisk.csv')
    return df


def compare_ratings(df):
    # Here we use a MannaWhitneyu method, because we compare ordinal data type between 2 ratings.
    mw_result = mannwhitneyu(df['Old Rating'], df['New Rating'])
#     The null hypothesis is that the two ratings do not differ.
#     If pvalue >= 0.05 it will mean that two ratings do not differ.
    if mw_result.pvalue >= 0.05:
        return True
    return False


def main():
    try:
        df = pd.read_csv('data-kinopoisk.csv')
    except FileNotFoundError:
        df = parse_kinopoisk()
    print(df)
    print('Two ratings', end=' ')
    if compare_ratings(df):
        print('are same')
    else:
        print('are different')
    return 0
    

if __name__ == '__main__':
    main()