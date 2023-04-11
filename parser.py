from datetime import datetime

import requests
import os
import json
from bs4 import BeautifulSoup as bs
import re


def clean_file_name(name):
    invalid_chars = '<>:"/\\|?*'
    clean_name = re.sub(r'[{}]'.format(re.escape(invalid_chars)), '', name)
    return clean_name


def baseRequest(ani_url):
    r = requests.get(
        url=ani_url)
    return bs(r.text, "html.parser")


def normalizeText(text):
    return [t.strip(", ") for t in text.split(',')]


def getMainInfo(soup, ani_url):
    idx = 0
    try:
        if soup.find('div', class_='anime-info').dl.find_all('dt')[0].get_text().strip() == 'Следующий эпизод':
            idx = 2
    except AttributeError:
        print(ani_url)

    anime_info = soup.find('div', class_='anime-info').dl.find_all('dd')
    anime_title = soup.find('div', class_='anime-title').div.h1.get_text().strip()
    anime_img_url = soup.find('div', class_='anime-poster').find('img').attrs['src']
    saveImg(anime_img_url, anime_title)
    return {
        'name': clean_file_name(anime_title),
        'url': ani_url,
        'episodes': anime_info[1 + idx].get_text(),
        'status': anime_info[2 + idx].get_text(),
        'genre_list': normalizeText(anime_info[3 + idx].get_text()),
        'release': anime_info[6 + idx].get_text(),
        'voice_over': normalizeText(anime_info[11 + idx].get_text()),
        'image': f'ani_images/{anime_title}.jpg',
        'last_update': datetime.utcnow().strftime('%d.%m.%Y %H:%M'),
    }


def getNextEpisodesReleaseDates(soup):
    episodes = soup.find('div', 'row released-episodes-container').find_all('div', 'col-12 released-episodes-item')
    episodes_info = []
    for row in episodes:
        episode_info = {}
        for (idx, col) in enumerate(row.div.div.find_all('div')):
            item = col.get_text().strip()
            if idx == 0:
                episode_info['number'] = item
            if idx == 1:
                episode_info['name'] = item
            if idx == 2:
                episode_info['release_date'] = item
        episodes_info.append(episode_info)

    return episodes_info


def saveImg(url, name):
    response = requests.get(url)
    name = clean_file_name(name)
    if response.status_code == 200:
        folder_name = "ani_images"
        if not os.path.exists(folder_name):
            os.mkdir(folder_name)
        if os.path.exists(folder_name + f"/{name}.jpg"):
            return
        file_path = os.path.join(folder_name, f"{name}.jpg")
        with open(file_path, "wb") as f:
            f.write(response.content)
            print("Image saved successfully!")
    else:
        print("Failed to download image")

#
# def checkExists(anime_name, anime_list):
#     for idx, anime in enumerate(anime_list):
#         if anime['title_name'] == anime_name:
#             return idx
#     return -1
#
#
# def updateFile(filename, anime_info):
#     with open(filename, 'w', encoding='utf-8') as file:
#         json.dump(anime_info, file, ensure_ascii=False)


def parseAnime(URL):
    soup = baseRequest(URL)
    info = getMainInfo(soup, URL)
    info['next_episodes'] = getNextEpisodesReleaseDates(soup)
    return info

