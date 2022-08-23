import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import discogs_client
import time
import pandas as pd
import sys

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
base_url = "https://www.nts.live"
discogs_token = ""
discogs_client = discogs_client.Client('ExampleApplication/0.1', user_token=discogs_token)

# selenium setup
options = Options()
options.headless = True
service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

def get_html(url: str):
    # Returns bs4.BeautifulSoup object from url using Requests
    req = requests.get(url, headers)
    soup = BeautifulSoup(req.content, 'html.parser')
    return soup

def get_html_selenium(url: str):
    # Returns bs4.BeautifulSoup object from url using Selenium
    driver.get(url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup

def get_episodes(soup: "bs4.BeautifulSoup object"):
    # Returns list of episode urls from bs4 object containing NTS 'shows' html
    episodes = []
    for element in soup.find_all("a",{"class":"nts-grid-v2-item__header"}):
        episodes.append(element['href'])
    return episodes

def get_tracklist(soup: "bs4.BeautifulSoup object", episode: str):
    # Returns list containing basic track metadata (artist, track, url and episode number from bs4 object containing NTS 'episodes' html
    tracklist = []
    for element in soup.find_all("li"):
        artist = element.find("span",{"class":"track__artist"}).text
        track = element.find("span",{"class":"track__title"}).text
        url = get_url(element, track)
        tracklist.append({"artist": artist,
                          "track" : track,
                          "url" : url,
                          "number" : str(episode)})
    return tracklist

def get_url(element: "", track: str):
    # Return NTS artists url for track
    try:
        return element.find('a', href=True)['href']
    except:
#         print("no url for " + track)
        return None

def expand_artist_html(url: str):
    # click 'MORE TRACKS' until all tracks are loaded in NTS artist html
    soup = get_html_selenium(url)
    while driver.find_element("xpath", "//*[contains(text(), 'MORE TRACKS')]"):
        try:
            element = driver.find_element("xpath", "//*[contains(text(), 'MORE TRACKS')]")
            element.click()
        except:
            break
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup

def get_track_metadata(soup: "bs4.BeautifulSoup object", track: str):
    # returns additional track metadata (label, year and discogs url) from NTS artists html for specified track
    label, year, discogs_url = None, None, None
    track_info = soup.find("div", string=track)
    if track_info:
        try:
            label = track_info.parent.find_all("span")[1].text
            year = track_info.parent.find_all("span")[3].text
            discogs_url = track_info.parent.find_all("div")[1].parent['href']
        except:
            pass
    return label, year, discogs_url

def find_track_metadata(url, soup: "bs4.BeautifulSoup object", track: str):
    # returns NTS artists html containing track metadata for artist url
    track_info = soup.find("div", string=track)
    if track_info:
        return soup
    else:
        soup = expand_artist_html(url)
        return soup

def get_discogs_metadata(discogs_url: str):
    release_number = [int(s) for s in discogs_url.split('/') if s.isdigit()]
    country = discogs_client.release(release_number[0]).country
    genres = discogs_client.release(release_number[0]).genres
    styles = discogs_client.release(release_number[0]).styles
    return country, genres, styles

def expand_shows_html(url: str):
    # scroll to the bottom of page until all shows are loaded in NTS shows html
    soup = get_html_selenium(url)
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
    #     print("last_height =" + str(last_height))
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Wait to load page
        time.sleep(0.3)
        new_height = driver.execute_script("return document.body.scrollHeight")
    #     print("new_height =" + str(new_height))
        if new_height == last_height:
            break
        last_height = new_height
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    return soup

def generate_csv(show_url: str):
    # generate relevant prefix for saving data to csv
    prefix = show_url.split('/')[-1]
    filename = prefix + '_tracklist.csv'
    # test creating csv
    with open(filename, 'w') as test_csv:
        pass
    return filename,prefix

def main(show_url: str):
    # returns combined tracklist for every episode of NTS show
    print(show_url)
    filename,prefix = generate_csv(show_url)
    soup = expand_shows_html(show_url)
    episodes = get_episodes(soup)
    full_tracklist = []
    for i, episode in enumerate(episodes):
        print(str(round((100*(i+1)/len(episodes)),1)) + "% complete")
        episode_tracklist = []
        episode_url = base_url + episode
        episode_html = get_html(episode_url)
        episode_tracklist = get_tracklist(episode_html, "0")
        for j, track in enumerate(episode_tracklist):
            if track['url']:
                url = base_url + track['url']
                artist_html = get_html(url)
                artist_html_with_metadata = find_track_metadata(url, artist_html, track['track'])
                episode_tracklist[j]["label"], episode_tracklist[j]["year"], episode_tracklist[j]["discogs_url"] = get_track_metadata(artist_html_with_metadata, track['track'])
                if episode_tracklist[j]["discogs_url"]:
                    episode_tracklist[j]["country"], episode_tracklist[j]["genre"], episode_tracklist[j]["styles"] = get_discogs_metadata(track['discogs_url'])
        full_tracklist += episode_tracklist
    df = pd.DataFrame(full_tracklist)
    df['mix'] = prefix.replace('-', ' ')
    df.to_csv(filename, encoding='utf-8', index=False)
    print("Tracklist saved to " + filename)

if __name__ == "__main__":
    main(str(sys.argv[1]))
