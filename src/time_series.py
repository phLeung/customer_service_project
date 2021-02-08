import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from utils.NexcomDB import NexcomDB
import numpy as np
import seaborn as sb
"""
Produce a graph that shows the accuracy rate of each employee over a monthly range.
the x axis contains the months or monthly range and the y axis contains the percentage.
The accuracy rate is calculated as follows: 100 * (Total transactions - Failed Transaction)/ Total transactions

Libraries used and why:
matplotlib: data visualization and displaying of graph
numpy: fast computation of datasets retrieved by sql queries
pandas: data cleanup and analysis. Useful for labeling data for plotting graph.
        useful in displaying time series graph.
seaborn: a subset of matplotlib. useful for displaying time series. Access to coloring schemes
         to denote different employees for graph. seaborn also offers close integration with Pandas
         data structures, making it easier for me to plot graph from pandas datasets. Seaborn reduces syntax complexity for data visualization. As a result,
         this allowed me to write less code for displaying the time series graph.
"""
"""
Given the parameters and the data provided for this task,
this graph is a time series because the datapoint accuracy for each employee is
measured at different points in time.
"""
#get failed transactions
def get_failed_transactions():
    #safely connect and close database with context manage
    #I used a self join for transaction table to get the transaction dates that match with each employee ids
    #This allowed me to get each employee's respective transaction date
    with NexcomDB('calldatadb') as db:
        db.execute('set datestyle = "EUROPEAN, DMY"')
        failed_transactions = db.query('''
         select e.fullname,count(ta.failed),t1.transactiondate from transaction t1 join transaction t2 on t1.employeeid = t2.employeeid
         join Employee e on e.id = t1.employeeid join transactionattribute ta on ta.transactionID = t1.ID join attribute a on a.ID = ta.AttributeID
         WHERE ta.failed = '1' AND t1.transactiondate BETWEEN '01/01/2020' AND '30/09/2020'
         group by e.fullname,ta.failed,t1.transactiondate;
        ''')
        return failed_transactions

#get total failed transactions from each employee
def get_failed_transaction_data_frames():
    #create pandas data frame for total failed transactions from each employee
    total_failed_transactions = get_failed_transactions()
    names_list = [text[0] for text in total_failed_transactions]
    number_of_fails = [text[1] for text in total_failed_transactions]
    months_list = [month[2] for month in total_failed_transactions]
    df_total_failed = pd.DataFrame({"names":names_list,"transactions":number_of_fails,"months":months_list})
    return df_total_failed

#get total applicable transactions
def get_transactions():
    #safely connect and close database with context manage
    with NexcomDB('calldatadb') as db:
        db.execute('set datestyle = "EUROPEAN, DMY"')
        #the point of this query is to count the total number of transactions.
        # you could count the number of failed transactions (pass or fail) or
        #you could count the number of applicable transactions.
        #when computing the total number of transactions, it does not matter what kind of transaction you use
        #based on the given datasets. The query below gets the total number of transactions for each employee.
        #I used a self join for this query to get the transaction dates that matches with the employee name based on employee id.
        #This allowed me to retrieve each employee's transaction date. In other words,
        # I was able to map each transaction date with its repective employee
        total_transactions = db.query('''
             select e.fullname,count(ta.appliable),t1.transactiondate from transaction t1 join transaction t2 on t1.employeeid = t2.employeeid
             join Employee e on e.id = t1.employeeid join transactionattribute ta on ta.transactionID = t1.ID join attribute a on a.ID = ta.AttributeID
             WHERE t1.transactiondate BETWEEN '01/01/2020' AND '30/09/2020'
             group by e.fullname,ta.appliable,t1.transactiondate;

        ''')
        return total_transactions

#get the total applicable transactions as a pandas data frame
#total transactions include all transactions such as applicable, failed, or passed
def get_total_transactions():
    total_transactions = get_transactions()
    names_list = [text[0] for text in total_transactions]
    number_of_transactions = [text[1] for text in total_transactions]
    months_list = [month[2] for month in total_transactions]
    df_total_transactions = pd.DataFrame({"names":names_list,"transactions":number_of_transactions,"months":months_list})
    return df_total_transactions


def get_datapoint_accuracy():
    df_failed_transactions = get_failed_transaction_data_frames()
    df_total_transactions = get_total_transactions()
    #combine data frames
    #merge dataframes via left join.
    #I used left join because i am interested in retrieving transactions from two datasets with common dates
    # in addition to all failed transactions with dates that correspond to the dates of successful transactions
    df_datapoint = pd.merge(df_failed_transactions,df_total_transactions, left_on='months',right_on='months',suffixes=('_failed','_total'),how="left")
    df_data_accuracies = pd.DataFrame({"total_transactions": df_datapoint["transactions_failed"] + df_datapoint["transactions_total"]})
    df_data_accuracies['accuracy'] = 100*(df_datapoint['transactions_total']-df_datapoint['transactions_failed'])/df_data_accuracies['total_transactions']
    df_data_accuracies["names"] = df_datapoint["names_total"]#names from total transactions data frame
    df_data_accuracies["months"] = df_datapoint["months"]
    return df_data_accuracies



#show the time series report
def show_report():
    #customize matplotlib graph
    matplotlib.rcParams.update(
      {
         'text.usetex':False,
         'font.family':'stixgeneral',
         'mathtext.fontset': 'stix',
      }
    )
    #configure size of graph
    dimensions = (10.75, 7.5)
    fig, ax = plt.subplots(figsize=dimensions)
    ax.yaxis.grid(True)#show horizontal lines on y axis
    #seaborn allows me to set a coloring scheme for all ten employees to show patterns within the data
    sb.set(color_codes=True)#different color schemes for employee lines
    #get dataset
    datapoint_frames = get_datapoint_accuracy()
    #plot the time series graph
    #I chose seaborn library because of uses beautiful themes for decorating graphs.
    #The seaborn library also makes it easy for me to integrate with pandas data structures
    #The seaborn library offers specialized support for categorical variables, in this case months and accuracy,
    #to show observations or aggregate statistics.
    sb.lineplot(x='months',y='accuracy',hue='names',data=datapoint_frames,marker='o',ax=ax)
    #decorate graph
    plt.title("Accuracy Rate")
    plt.xticks(rotation=45)
    plt.ylabel("Accuracy Rate")
    plt.yticks(np.arange(0,125,25))#display y axis numbers from 0 to 100
    plt.show()




if __name__ == '__main__':
    show_report()
