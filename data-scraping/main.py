from scraping import *

# 

import pandas as pd
import os
import json

# 

############

year = 2024
season = GameSeason.SUMMER

############

# 

resultdir = os.path.join(os.path.dirname(__file__), f'./result/{year}.{season.name.lower()}/')

if not os.path.exists(resultdir):
    os.makedirs(resultdir)

# 

scraper = Scraper(debug=True)

countries = scraper.countries()

# 

editionCode = scraper.game2editionCode(year, season)

competition_dates_str = [datetime.strftime(dt, '%Y-%m-%d') for dt in scraper.getExactCompetitionDatetimes(editionCode)]

metadata = {
    "year": year,
    "season": season.name.lower(),
    "dates": {
        "competitions": {
            "opening": competition_dates_str[0],
            "closing": competition_dates_str[1]
        }
    }
}

with open(os.path.join(resultdir, './metadata.json'), "w") as metadatafile:
    metadatafile.write(json.dumps(metadata, indent=4))

# 

global_df = None

with open(os.path.join(resultdir, './missings.txt'), "w") as missingsfile:
    for country in countries:
        dataframe_csv_filepath = os.path.join(resultdir, f'./countries/{country['code']}.{year}.{season.name.lower()}.csv')
        
        df = None
        if os.path.exists(dataframe_csv_filepath):
            print(f'File {dataframe_csv_filepath} already exists, skipping it')
            
            df = pd.read_csv(dataframe_csv_filepath)
        else:
            df = scraper.allEventsResults(country['code'], year=year, season=season)
            
            if df is None or df.empty:
                print('Missing data for', dataframe_csv_filepath)
                missingsfile.write(f'{os.path.basename(dataframe_csv_filepath)}\n')
            else:
                df.insert(0, 'season', season.name.lower())
                df.insert(0, 'year', year)
                df.insert(0, 'country_code', country['code'])
                df.insert(0, 'country_name', country['name'])
                
                df.to_csv(dataframe_csv_filepath, index=False)
            
        if df is not None and global_df is None:
            global_df = pd.DataFrame([], columns=df.columns)
        
        global_df = pd.concat([_df for _df in [global_df, df] if not _df.empty])

if global_df is not None:
    global_df.to_csv(os.path.join(resultdir, f'./global.{year}.{season.name.lower()}.csv'), index=False)