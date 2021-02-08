import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.ticker import FuncFormatter
import pandas as pd
from utils.NexcomDB import NexcomDB
"""
Produce a bar and line graph. The x-axis contains the text of Attributes. The bars
represent the number of failed transaction attributes and the line represents the
accumulated percentage.
Libraries used and why:
Numpy: I used numpy for its fast computational abilities for calculating the accumulated percentage
Pandas: I used pandas for formatting the data retrieved from postgres so that it can be displayed
        Furthermore, pandas was great for calculating the accumulated percentage.

Matplotlib: data visualization and displaying of graph.

"""
#function to get transaction attributes that have failed and the number of fails associated with transaction attributes
#on transactions between January 1 and September 30
#retrieve the number of failed transactions for each text
def get_fails():
    #safely connect and close database with context manager
    with NexcomDB('calldatadb') as db:
        #set the date style
        db.execute('set datestyle = "EUROPEAN, DMY"')
        fails = db.query('''
        SELECT COUNT(ta.failed),Text FROM transactionattribute ta join transaction t on t.ID = ta.TransactionID
        join attribute a on a.ID=ta.AttributeID
        join Employee e on t.employeeID = e.ID
        WHERE t.transactiondate BETWEEN '01/01/2020' AND '30/09/2020' AND ta.failed = '1' GROUP BY a.Text,ta.failed;
        ''')

        return fails

#display the graph
def show_report():
    #customize matplotlib graph
    matplotlib.rcParams.update(
      {
         'text.usetex':False,
         'font.family':'stixgeneral',
         'mathtext.fontset': 'stix',
      }
    )
    #set up y axis
    failures = get_fails()
    fail_list = [fail[0] for fail in failures]
    fail_list = sorted(fail_list)
    number_of_fails = np.array(fail_list)
    #set up x axis
    text_attributes = [text[1] for text in failures]
    attribute_texts = np.array(text_attributes)
    #create data frame for failed attributes
    failed_df = pd.DataFrame({'fails':number_of_fails})
    #accumulated sum and percentage for failed attributes
    failed_df['failed_accumulated_sum'] = failed_df['fails'].cumsum()
    failed_df['failed_accumulated_percent'] = round(100*failed_df.failed_accumulated_sum/failed_df['fails'].sum(),2)
    #create bar plot
    fig = plt.figure(1)#create figure
    h = plt.bar(range(len(attribute_texts)),number_of_fails,label=attribute_texts)
    plt.subplots_adjust(bottom=0.3)
    xticks_pos = [0.65*patch.get_width() + patch.get_xy()[0] for patch in h]
    plt.xticks(xticks_pos,attribute_texts, ha='right', rotation=45)
    plt.yticks(np.arange(0,125,25))
    plt.ylabel("No. failed")
    #create line graph
    ax = fig.add_subplot(111)
    #add annotations for bar graph
    for patch in ax.patches:
        bar_width = patch.get_width()
        bar_height = patch.get_height()
        x1,y1 = patch.get_xy()
        ax.annotate(f'{bar_height}', (x1 +bar_width/2,y1+bar_height*1.02),ha='center',weight='bold')
    ax2 = ax.twinx()
    ax2.yaxis.set_label_position("right")#set y axis for line graph to the right
    ax2.yaxis.tick_right()#show ticks for percentages on right for line graph
    ax2.set_yticks(np.arange(0,125,25))#set y axis range for accumulated percentage
    ax2.set_ylabel("Accumulated Percentage")
    #format right side of y axis for percentages. In other words, show % on right side of line graph for y axis
    ax2.yaxis.set_major_formatter(FuncFormatter(lambda y, _ :f'{y}%'))
    #draw line graph for accumulated percentage
    failed_df['failed_accumulated_percent'].plot(kind='line',marker='o',color="black",ax=ax2).grid(axis='y')
    #add annotations for line graph
    for index,x in enumerate(failed_df['failed_accumulated_percent']):
        ax.annotate(f'{x}%',xy=(index,x),ha='center',weight="bold")


    plt.show()#show graph



if __name__ == '__main__':
    show_report()
