
#!/usr/bin/env python
"""
'NUM_THREADS': Number of threads to run the queries on
'FILE_NAME': Location of log file for DNS queries
'DATABASE_LOCATION': Location of database
'DNS_LOCATION': Index in line of logfile of query EG in the following line it is 6 (default for bind9)
30-Nov-2017 22:04:11.121 client 10.0.0.85#37062 (www.googleapis.com): query: www.googleapis.com IN A + (10.0.0.79)
"""

settings = {'NUM_THREADS': 20,
         'FILE_NAME':'queries.log',
         'DATABASE_LOCATION':'queries_new.db',
        'DNS_LOCATION': 6 }

