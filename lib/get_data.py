import requests
import os

## Get the Data
# The National Observatory of Athens has an earthquake catalog; for each year there is a txt file with all the earthquakes in Greece.
# Each text file is named 'CAT' followed by the year e.g. 'CAT2019.TXT' 

def make_url(years):
    return [f'https://www.gein.noa.gr/HTML/Noa_cat/CAT{year}.TXT' for year in years]

def make_filename(urls: list):
    return [f"Data/{url.split('/')[-1]}" for url in urls]

def get_earthquakes(years: list):
    urls = make_url(years)
    filenames = make_filename(urls)

    for year, url, filename in zip(years, urls, filenames):
        if os.path.exists(filename):
            print(f'{year} earthquake data already downloaded!')
        else:        
            with open(filename, mode='w') as f:
                try:
                    f.write((response := requests.get(url)).text)
                    response.status_code
                except Exception as e:
                    print(e)
                    print('Website currently not available')