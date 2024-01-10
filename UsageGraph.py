import pandas as pd
from datetime import datetime
import json
from DataHandling import EventHandling


class UsageGraph:
    """
    The class methods performs data processing in way to create a ready to use object
    for the Moodle system with all the needed information to generate a graph of the
    usage of Learning Nuggets of each course.
    The Methods of the class give the opportunity to filter the data using Learning
    Nugget ID, course, a date range, chapters of the course and even the lecture dates.
    The provided final form is a JSON object with the requested filtered data.
    The service was build by Panos Pagonis. For questions email
    panos.pagonis@thi.de.
    The main methods are:
    usagegraph()
    """
    def __init__(self):
        """
        Initializing method, calls the preprocessed data from EVD.
        :return: None
        """
        self.df = EventHandling().preproccess()
        self.grouped_df = None

    def usagegraph(self, courseid, chapter=None, date_range=None, LN=None):
        """

        :param courseid: Given course id in order to filter out the data.
        Only 1 courseid must be provided.
        :param chapter: The chapther or capitals of the specific course to
        be used in the analysis. Multiple could be used in a form of list
        of intergers e.g. [1, 2, 3, 4,] in case all are given leave empty
        or better give ["*"] a list of a single asterisk string.
        :param date_range: The date range to be calculated for the graph.
        Default value to be sent is the minimum and maximum date found in
        the data. Please enter input in form of list of two objects. A
        format could be ["DD.MM.YYYY", "DD.MM.YYYY"].
        :param LN: The learning nuggets to be included in the analysis.
        Multiple could be used in a form of list of intergers e.g.
        [1, 2, 3, 4,] in case all are given leave empty or better give
        ["*"] a list of a single asterisk string.

        :return: JSON object with a filtered dataframe based on the
        requested parameters. It includes an object per DAY with
        unique users per item or all the usages of the item as
        well as lecture dates, chapter, Learning Nuggets and members
        enroled in course
        """

        # Check if courseid is given or if is in dataset included
        if courseid is None:
            raise ValueError("Please provide a valid courseid.")

        if not any(self.df['courseid'] == courseid):
            raise ValueError(f"Courseid {courseid} not found in the data.")

        self.df = self.df[self.df['courseid'] == courseid]

        # Filter by chapter (if provided)
        if chapter is not None:
            # TODO for chapter filtering
            pass

        # Filter by date_range (if provided)
        if date_range is not None:
            try:
                start_date, end_date = map(lambda x: datetime.strptime(x, "%d.%m.%Y").date(), date_range)
                if start_date > end_date:
                    raise ValueError("End date should be after the start date.")
                self.df = self.df[(self.df['day'] >= start_date) & (self.df['day'] <= end_date)]
            except ValueError as e:
                raise ValueError(f"Error parsing date range: {e}")

        self.df['objectid'] = pd.to_numeric(self.df['objectid'], errors='coerce')

        # Filter by LN (if provided)
        if LN is not None and LN != ['*']:
            if not isinstance(LN, list) or not all(isinstance(item, int) for item in LN):
                raise ValueError("LN should be a list of integers.")
            self.df = self.df[self.df["objectid"].isin(LN)]

        self.df['day'] = pd.to_datetime(self.df['day'])
        self.df['day'] = self.df['day'].dt.strftime('%d-%m-%Y')

        columns_to_keep = ['action', 'component', 'courseid', 'coursename', 'finishtime', 'grade',
                           'grade_to_pass', 'lectureDate', 'membersInCourse', 'nuggetName',
                           'objectid', 'user_id', 'day']
        self.df = self.df[columns_to_keep]

        # Create JSON object view with Day in top level and LN in second layer
        grouped_df = self.df.groupby(['day', 'objectid']).agg(
            courseid=('courseid', 'first'),
            coursename=('coursename', 'first'),
            lectureDate=('lectureDate', lambda x: list(pd.to_datetime(x).dt.strftime('%Y-%m-%d'))),
            membersInCourse=('membersInCourse', 'first'),
            nuggetName=('nuggetName', lambda x: list(x.unique())),
            user_id_count=('user_id', 'count'),
            user_id_nunique=('user_id', 'nunique')
        ).reset_index()

        grouped_df['day'] = pd.to_datetime(grouped_df['day'], format='%d-%m-%Y').dt.strftime('%d-%m-%Y')

        grouped_df['nuggetName'] = grouped_df['nuggetName'].apply(
            lambda x: [str(n) for n in x]) if 'nuggetName' in grouped_df.columns else None
        grouped_df = grouped_df.rename(
            columns={'user_id_count': 'count_user_id', 'user_id_nunique': 'count_unique_user_id'})

        # Fill dictionary with values
        result_dict = {}
        for _, row in grouped_df.iterrows():
            day = row['day']
            object_id = int(row['objectid'])
            data = {
                "courseid": row['courseid'],
                "coursename": row['coursename'],
                "lectureDate": row['lectureDate'],
                "membersInCourse": row['membersInCourse'],
                "nuggetName": row['nuggetName'],
                "count_user_id": row['count_user_id'],
                "count_unique_user_id": row['count_unique_user_id']
            }

            if day not in result_dict:
                result_dict[day] = {}

            result_dict[day][object_id] = data

        # Dict to JSON
        json_result = json.dumps(result_dict, indent=2)

        return json_result
