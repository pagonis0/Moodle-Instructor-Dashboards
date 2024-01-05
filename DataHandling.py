import pandas as pd
from pandas import json_normalize
from datetime import date, time
from tqdm import tqdm
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('mode.chained_assignment', None)

class EventHandling:

    def __init__(self):
        self.df = None
        self.usr_rmv = [-20, -10, -1, 2, 3, 5, 6, 7, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                   99, 101, 103, 117, 119, 120, 122, 123, 131, 145, 146, 149, 156, 161, 248]

    def __fetch(self):
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

        print('Fetching new json data... (Creating local cache)')

        try:
            json_data = requests.get('https://success-ai.rz.fh-ingolstadt.de/eventService/get_data_from_db',
                                     verify=False).json()
        except requests.exceptions.RequestException as e:
            print(f"Could not access Event Collection Data (EVC): {e}")

        self.df = json_normalize(json_data['data'])
        

        return self.df

    def _filter_data(self, usr_rmv: list, userid='user_id'):
        """
        Filter the user ids based on the given criteria.
        :param usr_rmv: A list of the user ids to be removed
        :return: pd.DataFrame: The filtered DataFrame.
        """
        self.df = self.df[~self.df[userid].isin(usr_rmv)]
        return self.df

    def preproccess(self):
        if self.__fetch() is None:
            return None

        self.df['courseid'] = self.df['courseid'].astype(int)
        self.df['objectid'] = pd.to_numeric(self.df['objectid'], errors='coerce')

        # Drop rows where 'objectid' is None after conversion
        self.df = self.df.dropna(subset=['objectid'])

        self.df['timecreated'] = pd.to_datetime(self.df['timecreated'])

        self.df['timecreated'] = pd.to_datetime(self.df['timecreated'], unit='s')
        self.df['month'] = self.df['timecreated'].dt.strftime("%Y-%m")
        self.df['week'] = self.df['timecreated'].dt.isocalendar().week
        self.df['year-week'] = self.df['timecreated'].dt.strftime("%G-%V")
        self.df['year'] = self.df['timecreated'].dt.year
        self.df['day'] = self.df['timecreated'].dt.date

        return self.df
