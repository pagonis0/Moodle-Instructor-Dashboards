import pandas as pd
from datetime import date, time, datetime
from tqdm import tqdm
import json
from DataHandling import EventHandling


class UsageGraph:
    def __init__(self):
        self.df = EventHandling().preproccess()
        self.grouped_df = None

    def usagegraph(self, courseid, chapter=None, date_range=None, LN=None):
        # Validate and filter by courseid
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

        grouped_df = self.df.groupby('day').agg(
            courseid=('courseid', 'first'),
            coursename=('coursename', 'first'),
            lectureDate=('lectureDate', lambda x: list(pd.to_datetime(x).dt.strftime('%Y-%m-%d'))),
            membersInCourse=('membersInCourse', 'first'),
            nuggetName=('nuggetName', lambda x: list(x.unique())),
            objectid=('objectid', lambda x: list(x.unique())),
            user_id_count=('user_id', 'count'),
            user_id_nunique=('user_id', 'nunique')
        ).reset_index()

        # Convert 'day' to the desired format
        grouped_df['day'] = pd.to_datetime(grouped_df['day'], format='%d-%m-%Y').dt.strftime('%d-%m-%Y')

        # Convert lists to strings for the final result
        grouped_df['nuggetName'] = grouped_df['nuggetName'].apply(
            lambda x: [str(n) for n in x]) if 'nuggetName' in grouped_df.columns else None
        grouped_df['objectid'] = grouped_df['objectid'].apply(
            lambda x: [float(o) for o in x]) if 'objectid' in grouped_df.columns else None

        # Rename columns for consistency
        grouped_df = grouped_df.rename(
            columns={'user_id_count': 'count_user_id', 'user_id_nunique': 'count_unique_user_id'})

        json_result = grouped_df.to_json(orient="table", date_format='iso')

        return json_result
