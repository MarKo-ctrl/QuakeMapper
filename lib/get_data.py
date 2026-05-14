import requests
import os

# Core Responsibilities of get_data.py
# 
# 1. Generate monthly date ranges — from 2000-01-01 to present, producing start/end pairs for each month
# 2. Build the USGS query URL for each chunk
# 3. Fetch each chunk from the API and handle the response
# 4. Assemble chunks into a single dataset
# 5. Cache locally as Parquet to avoid re-fetching

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

def get_usgs(url):
    return requests.get(url).text