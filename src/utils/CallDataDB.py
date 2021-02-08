import psycopg2 as psy
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
"""
I chose PostgreSQL because of its performance in handling large datasets and writing complex queries.
It also has good join capabilities compared to other databases such as MYSQL.
Before I created this python class for accessing the postgres database,
I created the database and the tables using the postgres command line.
On the postgres command line, I created the database with the following command:
CREATE DATABASE nexcomdb;
On the postgres command line, I created the 4 tables with the following commands in the database I created:
CREATE TABLE transaction (
 ID BIGINT NOT NULL PRIMARY KEY,
 CreationDate DATE NOT NULL,
 TransactionDate DATE,
 EmployeeID BIGINT NOT NULL REFERENCES Employee(ID)
);
CREATE TABLE TransactionAttribute (
 TransactionID BIGINT NOT NULL REFERENCES Transaction(ID),
 AttributeID BIGINT NOT NULL REFERENCES Attribute(ID),
 Failed BIT(1),
 Appliable BIT(1)
);
CREATE TABLE Employee(
 ID BIGINT NOT NULL PRIMARY KEY,
 FullName VARCHAR(255) NOT NULL,
 Department VARCHAR(255) NOT NULL
);
CREATE TABLE Attribute(
 ID BIGINT NOT NULL PRIMARY KEY,
 Text VARCHAR(255),
 NonCritical BIT(1),
 CustomerCritical BIT(1),
 ComplianceCritical BIT(1),
 BusinessCritical BIT(1)
);
Once I created the 4 tables, used postgres's copy command to insert data from the
given csv file into the 4 tables.
I used the following commands to insert data from the csv files into each table
using the following commands:
copy transactionattribute from '/Users/jazzphil/nexcom_task/data/TransAttr.csv' with DELIMITER ',' CSV HEADER;
copy attribute from '/Users/jazzphil/nexcom_task/data/Attribute.csv' with DELIMITER ',' CSV HEADER;
copy transaction from '/Users/jazzphil/nexcom_task/data/Transaction.csv' with DELIMITER ',' CSV HEADER;
copy employee from '/Users/jazzphil/nexcom_task/data/Employee.csv' with DELIMITER ',' CSV HEADER;
"""
#database object for connecting to the postgres database and querying with SQL
#using python
class CallDataDB(object):
    def __init__(self, name):
        self._conn = psy.connect("dbname="+name)#connect to postgres database
        self._cursor = self._conn.cursor()

    def __enter__(self):
        return self

    #exit out of the database when done
    def __exit__(self,*args, **kwargs):
        self._cursor.close()
        self._conn.close()

    @property
    def connection(self):
        return self._conn

    @property
    def cursor(self):
        return self._cursor

    #save changes
    def commit(self):
        self.connection.commit()

    #close database connection
    def close(self, commit=True):
        if commit:
            self.commit()
        self.connection.close()
    #execute query commands
    def execute(self, sql_query, params=None):
        self.cursor.execute(sql_query, params or ())

    def fetchall(self):
        return self.cursor.fetchall()

    #write sql queries to retrieve data
    def query(self, sql_query, params=None):
        self.cursor.execute(sql_query, params or ())
        return self.fetchall()
