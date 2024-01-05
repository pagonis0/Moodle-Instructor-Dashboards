import pandas as pd
import matplotlib.pyplot as plt
from DataHandling import *
from UsageGraph import *

#evnt_handling = EventHandling()
#evnt = evnt_handling.preproccess()
#evnt_math = evnt[evnt["courseid"] == "32"]


# all users all times
#count_df = evnt_math.groupby(['day', 'objectid']).size().unstack(fill_value=0)


# Remove duplicate rows based on 'user_id', 'objectid', and 'day'
#unique_rows = evnt_math.drop_duplicates(subset=['user_id', 'objectid', 'day'])

# Create a new DataFrame to count occurrences of 'objectid' for each 'day'
#count_df = unique_rows.groupby(['day', 'objectid']).size().unstack(fill_value=0)

# Plotting the stacked barplot
#plt.figure(figsize=(12, 8))
#count_df.plot(kind='bar', stacked=True)
#plt.title('Stacked Barplot of unique objectid counts per day per user_id')
#plt.xlabel('Day')
#plt.ylabel('Count')
#plt.legend(title='objectid', bbox_to_anchor=(1.05, 1), loc='upper left')
#plt.show()

usage_graph = UsageGraph()
filtered_df = usage_graph.usagegraph(courseid=32, date_range=["10.11.2023", "15.11.2023"], LN=[828, 830])
print(filtered_df)
