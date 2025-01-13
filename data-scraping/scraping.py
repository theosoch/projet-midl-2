from requests import get
from bs4 import BeautifulSoup

import pandas as pd

# 

from enum import Enum
from datetime import datetime
import re

# 

class GameSeason(Enum):
    SUMMER = 0,
    WINTER = 1
    
# 

def getFieldValueByName(table, fieldName):
    fieldValue = None

    for row in table.find_all('tr'):
        if row.find('th').text.strip() == fieldName:
            fieldValue = row.find('td').text.strip()
            
    return fieldValue

# 

class Scraper:
    def __init__(self, debug=False):
        self.baseUrl = 'https://www.olympedia.org'
        self.setDebugMode(debug)
        
        self.__methodCaches = {}
    
    # 
    
    def __getMethodCache(self, methodName):
        cache = self.__methodCaches.get(methodName)
        
        if cache is None:
            cache = {}
            self.__methodCaches[methodName] = cache
        
        return cache
            
    
    def setDebugMode(self, debug):
        self.__debugMode = debug
    
    # 
    
    def __getdom(self, url, debug):
        if debug or (debug == None and self.__debugMode):
            print('Scraping at:', url)
        
        resp = get(url)
        html = resp.text
        return (BeautifulSoup(html, 'html.parser'), resp)
    
    # 
    
    def __extractEditionCodeFromUrl(self, url):
        return int(url.split('/')[-1])
    
    def game2editionCode(self, year, season, debug=None):
        cache = self.__getMethodCache("game2editionCode")
        cacheKey = f'{year}.{season.name.lower()}'
        cacheResult = cache.get(cacheKey)
        if cacheResult is not None:
            if debug or (debug == None and self.__debugMode):
                print('Cache found for game2editionCode')
            
            return cacheResult
        
        #
        
        dom, resp = self.__getdom(f'{self.baseUrl}/editions', debug)
        
        edition_table_index = 0 if season == GameSeason.SUMMER else 1
        edition_table = dom.find_all('table')[edition_table_index]
        
        edition_row = None
        for row in edition_table.find_all('tr')[1:]:
            try:
                if int(row.find_all('td')[1].text.strip()) == year:
                    edition_row = row
                    break
            except:
                pass
    
        if edition_row == None:
            return None

        result = self.__extractEditionCodeFromUrl(edition_row.find('a')['href'])
        
        # 
        
        cache[cacheKey] = result
        return result

    def editionCode2game(self, editionCode, debug=None):
        cache = self.__getMethodCache("editionCode2game")
        cacheKey = editionCode
        cacheResult = cache.get(cacheKey)
        if cacheResult is not None:
            if debug or (debug == None and self.__debugMode):
                print('Cache found for editionCode2game')
            
            return cacheResult
        
        #
        
        dom, resp = self.__getdom(f'{self.baseUrl}/editions/{editionCode}', debug)
        
        title = dom.find('div', {'class': 'container'}).find('h1').text.strip()
        title_split = title.split(' ')
        
        result = (
            int(title_split[0]),
            GameSeason[title_split[1].upper()]
        )
        
        # 
        
        cache[cacheKey] = result
        return result

    def getExactCompetitionDatetimes(self, editionCode, debug=None):
        cache = self.__getMethodCache("getExactCompetitionDatetimes")
        cacheKey = editionCode
        cacheResult = cache.get(cacheKey)
        if cacheResult is not None:
            if debug or (debug == None and self.__debugMode):
                print('Cache found for getExactCompetitionDatetimes')
            
            return cacheResult
        
        #
        
        dom, resp = self.__getdom(f'{self.baseUrl}/editions/{editionCode}', debug)
        
        biotable = dom.find('table', {'class': 'biotable'})
        
        competition_dates_str = getFieldValueByName(biotable, 'Competition dates')
        competition_dates_str_split = [s.strip() for s in re.split(r"\s+[^\s]\s+", competition_dates_str)]
        
        if competition_dates_str_split[0].count(' ') < 2:
            competition_dates_str_split[0] += f' {competition_dates_str_split[1].split(' ')[-1]}'
        
        result = tuple([datetime.strptime(s, '%d %B %Y') for s in competition_dates_str_split])
        
        # 
        
        cache[cacheKey] = result
        return result
        
    # 
    
    def countries(self, debug=None):
        cache = self.__getMethodCache("countries")
        cacheKey = 'result'
        cacheResult = cache.get(cacheKey)
        if cacheResult is not None:
            if debug or (debug == None and self.__debugMode):
                print('Cache found for countries')
            
            return cacheResult
        
        #
        
        dom, resp = self.__getdom(f'{self.baseUrl}/countries', debug)
        
        countries = []
        
        country_table = dom.find_all('table')[0]
        for country_table_row in country_table.find_all('tr')[1:]:
            countries.append({ 'code': country_table_row.find_all('td')[0].text.strip(), 'name': country_table_row.find_all('td')[1].text.strip() })
        
        #
        
        cache[cacheKey] = countries
        return countries
    
    # 
    
    def __fetchAthlete(self, athleteCode, debug):
        cache = self.__getMethodCache("__fetchAthlete")
        cacheKey = athleteCode
        cacheResult = cache.get(cacheKey)
        if cacheResult is not None:
            if debug or (debug == None and self.__debugMode):
                print('Cache found for athlete', athleteCode)
            
            return cacheResult

        # 
        
        dom, resp = self.__getdom(f'{self.baseUrl}/athletes/{athleteCode}', debug)
        
        athlete_biodata_table = dom.find('table', {'class': 'biodata'})
        
        athlete_full_name_field_value = getFieldValueByName(athlete_biodata_table, 'Full name')
        athlete_full_name_split = [None, None] if athlete_full_name_field_value is None else athlete_full_name_field_value.split('\u2022')
            
        birth_date_field_value = getFieldValueByName(athlete_biodata_table, 'Born')
        birth_date_str = None if birth_date_field_value is None else ' '.join(birth_date_field_value.split(' ')[0:3])
        birth_datetime = None if birth_date_str is None else datetime.strptime(birth_date_str, '%d %B %Y')
        
        athlete_measurments_field_value = getFieldValueByName(athlete_biodata_table, 'Measurements')
        athlete_measurments = {}
        try:
            if athlete_measurments_field_value is not None:
                for s in athlete_measurments_field_value.split('/'):
                    sp = s.strip().split(' ')
                    athlete_measurments[sp[1]] = int(sp[0])
        except ValueError as err:
            pass
        except Exception as err:
            raise err
            
        athlete_results_table = dom.find('table', {'class': 'table'})
        
        medals = {}
        
        current_editionCode = None
        current_discipline = None
        
        for row in athlete_results_table.find('tbody').find_all('tr'):
            fields = row.find_all('td')
            
            if row.has_attr('class') and 'active' in row['class']:
                
                edition_hyperlink = fields[0].find('a')
                if edition_hyperlink is not None:
                    current_editionCode = self.__extractEditionCodeFromUrl(edition_hyperlink['href'])
                
                current_discipline = fields[1].find('a').text.strip()
                
                current_medal_value = medals.get(current_editionCode)
                medals[current_editionCode] = {} if current_medal_value is None else current_medal_value
                
                current_medal_editionCode_value = medals[current_editionCode].get(current_discipline)
                medals[current_editionCode][current_discipline] = {} if current_medal_editionCode_value is None else current_medal_editionCode_value
                    
            elif current_discipline != None:
                current_event = fields[1].find('a').text.strip()
                medals[current_editionCode][current_discipline][current_event] = fields[4].text.strip().lower()
        
        data = {
            'athlete_firstname': athlete_full_name_split[0] if len(athlete_full_name_split) > 0 else None,
            'athlete_lastname': athlete_full_name_split[1] if len(athlete_full_name_split) > 1 else None,
            'athlete_birthdate': birth_datetime,
            'athlete_sex': getFieldValueByName(athlete_biodata_table, 'Sex'),
            'athlete_height_cm': athlete_measurments.get('cm'),
            'athlete_weight_kg': athlete_measurments.get('kg'),
            'athlete_medals': medals
        }
        
        # 
        
        cache[cacheKey] = data
        return data
        
    def allEventsResults(self, countryCode, year=None, season=None, editionCode=None, debug=None):
        if editionCode is None:
            editionCode = self.game2editionCode(year, season, debug=debug)
        
        year, season = self.editionCode2game(editionCode, debug=debug)
        competition_datetimes = self.getExactCompetitionDatetimes(editionCode, debug=debug)
        
        dom, resp = self.__getdom(f'{self.baseUrl}/countries/{countryCode}/editions/{editionCode}', debug)
        if resp.status_code != 200:
            return None
        
        table = dom.find('table')
        
        data = []
        
        team_id = 0
        
        current_discipline = None
        current_event = None
        current_team_id = -1
        
        for row in table.find_all('tr'):
            
            if row.find('td', attrs={ 'colspan': 4 }):
                current_discipline = row.text.strip()
            else:
                fields = row.find_all('td')
                
                event_candidate = fields[0].text.strip()
                
                if len(event_candidate) > 0:
                    current_event = event_candidate
                
                athlete_hyperlinks = fields[1].find_all('a')
                
                if len(athlete_hyperlinks):
                    current_team_id = team_id
                    team_id += 1
                else:
                    current_team_id = -1
                
                for athlete_hyperlink in athlete_hyperlinks:
                    athleteData = self.__fetchAthlete(athlete_hyperlink['href'].split('/')[-1], debug)
                    
                    athlete_birth_datetime = athleteData.get('athlete_birthdate')
                    athlete_age = None if athlete_birth_datetime is None else int((competition_datetimes[0] - athlete_birth_datetime).days / 365.25)
                    
                    data.append([
                        current_discipline,
                        current_event,
                        current_team_id,
                        athleteData.get('athlete_firstname'),
                        athleteData.get('athlete_lastname'),
                        athlete_birth_datetime,
                        athlete_age,
                        athleteData.get('athlete_sex'),
                        athleteData.get('athlete_height_cm'),
                        athleteData.get('athlete_weight_kg'),
                        athleteData.get('athlete_medals')[editionCode][current_discipline][current_event]
                    ])
        
        dataframe = pd.DataFrame(data, columns=[
            'discipline',
            'event',
            'team_id',
            'athlete_firstname',
            'athlete_lastname',
            'athlete_birthdate',
            'athlete_age',
            'athlete_sex',
            'athlete_height_cm',
            'athlete_weight_kg',
            'athlete_medal'
        ])
        
        return dataframe