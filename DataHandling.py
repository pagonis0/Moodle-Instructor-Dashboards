import pandas as pd
from pandas import json_normalize
import requests, json, time, os
from urllib3.exceptions import InsecureRequestWarning
from flask import request
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('mode.chained_assignment', None)


class EventHandling:
    """
    The main class of Event Handler service. It calls the data
    from the Event Collection Database (ECD), cache them and
    performs the basic preprocessing in order to be ready to used
    for graphics production.
    This classes requires no inputs at all, just call it as it is,
    events = EventHandling()
    The proposed use of class is to provide ready to use data,
    to become graphs in a Moodle instance for the THISuccessAI
    project.
    The service was build by Panos Pagonis. For questions email
    panos.pagonis@thi.de.
    The main methods are:
    __init__()
    __fetch()
    _filter_data()
    preprocess()
    """
    def __init__(self, cache_file='event_data_cache.json', url):
        """
        Initializer method.
        Contains the user IDs that need to be removed.
        Often updated.
        :return: None
        """
        self.df = None
        self.usr_rmv = [-20, -10, -1, 2, 3, 5, 6, 7, 9, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                        99, 101, 103, 117, 119, 120, 122, 123, 131, 145, 146, 149, 156, 161, 248]
        self.cache_file = cache_file
        self.url = url


    def __fetch(self):
        """
        Method to call the data from the EVD. It strores the data in a DataFrame object.
        If the data exists already calls them from a file, but if they are expired
        (file older than 24h) call a new set of data.
        :return: pandas.DataFrame object with all the data from EVD
        """
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

        if os.path.exists(self.cache_file):
            file_modified_time = os.path.getmtime(self.cache_file)
            current_time = time.time()
            if current_time - file_modified_time < 24 * 3600:
                print('Loading data from cache...')
                with open(self.cache_file, 'r') as file:
                    return json.load(file)
        else:
            print('Cache file not found. Creating a new one.')

        print('Fetching new json data... (Creating local cache)')
        try:
            json_data = requests.get(self.url, verify=False).json()
        except requests.exceptions.RequestException as e:
            print(f"Could not access Event Collection Data (EVC): {e}")

        with open(self.cache_file, 'w') as file:
            json.dump(json_data, file)

        self.df = json_normalize(json_data['data'])
        
        return self.df

    def _filter_data(self, usr_rmv: list, userid='user_id'):
        """
        Filter the user ids based on the given criteria.
        :param usr_rmv: A list of the user ids to be removed
        :return: pandas.DataFrame object with the filtered DataFrame.
        """
        self.df = self.df[~self.df[userid].isin(usr_rmv)]
        return self.df

    def preproccess(self):
        """
        The method performs a basic preprocessing of the dataset.
        It transforms the times to pandas.datetime and generates
        week, day and year
        :return: pandas.DataFrame object with the newly added columns
        """

        fetch_result = self.__fetch()
        if fetch_result is not None:
            self.df = json_normalize(fetch_result['data'])
        else:
            # Fallback to fetch_fallback_data method
            courseid_for_fallback = request.json.get("courseid")
            self.__fetch_fallback_data(courseid=courseid_for_fallback)
            return self.df

        """"# USE ONLY FOR TESTING THE FALLBACK
        courseid_for_fallback = request.json.get("courseid")
        self.df = self.fetch_fallback_data(courseid=courseid_for_fallback)"""

        self.df["user_id"] = self.df["user_id"].astype(int)
        self._filter_data(usr_rmv=self.usr_rmv)

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


    def fetch_fallback_data(self, courseid, action: str = "viewed", fallback_url: str):
        """
        If the EVD is not reachable is calls the data from
        Moodle log files. The method also does the preprocessing
        of the data in form that they are similar to the EVD data.
        :return: pandas.DataFrame object with the whole dataset
        """

        url = fallback_url
        params = {
            'wstoken': "38cb1aa68d55c4f2d8dcb691a306b2f6",
            'wsfunction': "local_wstemplate_get_site_logs",
            'moodlewsrestformat': "json",
            'courseid': courseid,
            'action': action
        }

        response = requests.get(url, params=params)

        data = response.json()
        self.df = json_normalize(data["site_logs"])
        self.df['lectureDate'] = None
        self.df['membersInCourse'] = self.df["userid"].nunique()
        self.df['timecreated'] = pd.to_datetime(self.df['timecreated'], unit='s')
        self.df.rename(columns={'userid': 'user_id'}, inplace=True)

        return self.df
