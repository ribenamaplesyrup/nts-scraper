# NTS Scraper

The following python script can be used to generate a csv file containing all of the tracks and associated metadata for an NTS show with multiple episodes. The script uses a combination of `requests`, `beautifulsoup` and `selenium` to extract base metadata from NTS (track name, artist, year, label). For tracks with a Discogs link, futher metadata is extracted through the Discogs API, such as country, genre and styles, using this nice [Discogs client library](https://github.com/joalla/discogs_client).

If you enjoy using this script, please also consider [becoming an NTS supporter](https://www.nts.live/supporters) to help them continue providing an incredible platform for discovering new music.

## Requirements

You will require a user-token to authenticate with the Discogs API. For this, you'll need to [generate a user-token from your developer settings](https://python3-discogs-client.readthedocs.org/en/latest/authentication.html#user-token-authentication) on the Discogs website. Until I implement a more elegant way of adding tokens, you will need to hardcode it into the script as the string value for the `discogs_token` variable.

## Installation

Requirements can be installed using conda:

```bash
conda env create -f environment.yml
conda activate nts
```

## Example Usage

```bash
python3 nts_scrape.py <nts show url>
python3 nts_scrape.py https://www.nts.live/shows/oli-xl
```

Once you have scraped metadata for multiple shows, you can use 'generate_network.py' to create mappings of how shows connect through playing artists from the same record labels. The script will generate a JSON file containing nodes (shows, artists and record labels) and links between nodes:

```bash
python3 generate_network.py <multiple csv files generated from nts_scrape.py>
python3 generate_network.py james-k_tracklist.csv loraine-james_tracklist.csv oli-xl_tracklist.csv
```
