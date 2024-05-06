import os
import psycopg2
import sqlite3
from functools import wraps
from rest_framework import status
from rest_framework.response import Response


def getConnection():
    """Configure database connection for Different Environments"""
    config_type = os.getenv('CONFIGURATION_MODE')
    if 'testing' == config_type:
        # Using Local DB => SQLITE
        connection = sqlite3.connect('db.sqlite3')
    elif 'production' == config_type:
        # Using Postgre testing database
        connection = psycopg2.connect(
            database="gcx_testing", user="postgres", password="7896005", host="localhost", port="5432")
    else:
        # Using Postgre Live database
        connection = psycopg2.connect(
            database="gcx_testing", user="postgres", password="7896005", host="localhost", port="5432")
    return connection
