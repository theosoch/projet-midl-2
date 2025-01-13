from scraping import *

# 

import pandas as pd
import numpy as np
import os
from datetime import datetime

# 

############

year = 2020
season = GameSeason.SUMMER

############

# 

resultdir = os.path.join(os.path.dirname(__file__), f'./result/{year}.{season.name.lower()}/')

if not os.path.exists(resultdir):
    os.makedirs(resultdir)

# 

scraper = Scraper(debug=True)

editionCode = scraper.game2editionCode(year, season)

competition_datetimes = scraper.getExactCompetitionDatetimes(editionCode)

countries = scraper.countries()

# 

dataframe_csv_filepath_list = []

for country in countries:
    dataframe_csv_filepath_list.append(os.path.join(resultdir, f'./countries/{country['code']}.{year}.{season.name.lower()}.csv'))

dataframe_csv_filepath_list.append(os.path.join(resultdir, f'./global.{year}.{season.name.lower()}.csv'))

# 

for dataframe_csv_filepath in dataframe_csv_filepath_list:
    print(dataframe_csv_filepath)
    
    if os.path.exists(dataframe_csv_filepath):
        df = pd.read_csv(dataframe_csv_filepath)
        
        # 
        
        df.drop(columns=['year', 'season'], inplace=True)
        
        # 
        
        df.to_csv(dataframe_csv_filepath, index=False)
        