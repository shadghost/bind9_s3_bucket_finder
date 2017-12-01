import socket
import boto3 #not default, needs to pip install
from multiprocessing import Pool
import sqlite3
import time
NUM_THREADS=30  #number of threads to do dns queries with, this is the slow part
FILE_NAME='queries.log'
DB='test.db'

"""lets make a db test"""
conn = sqlite3.connect('example.db')
"""do we need to seed it?"""
c = conn.cursor()
try:
    c.execute("SELECT * from dummy")
except:
    print "first time running, setting up!"
    c.execute('''CREATE TABLE dummy (first_run)''')
    c.execute('''CREATE TABLE cache (dns,date)''')
    c.execute('''CREATE TABLE findings (dns,date)''')
    c.execute("INSERT INTO dummy VALUES ('good')")
    conn.commit()
"""We now have a working DB"""

"""
This will look for the s3 bucket
Requires:
    ~/.aws/config
    ~/.aws/credentials
you can set these via the aws clihttps://aws.amazon.com/cli/
Takes: a bucket name
Returns: True if bucket has directory listing, false otherwise
"""
def try_s3(bucket_name):
    s3 = boto3.client('s3')
    try:
        result = s3.list_objects(Bucket=bucket_name)
        c=conn.cursor()
        c.execute("INSERT INTO findings VALUES (?,?)",(bucket_name,int(time.time())))
        return True
    except:
        return False

"""
Take the DNS query and gets everything before the s3 part
todo: only look for AWS domain parts, not just s3
"""
def make_s3name(url,first_run=True):
    if not (url.find('s3') == -1):
        split=url.split('.')
        joined=""
        for i in split:
            if(first_run):
                joined = i
                first_run=False
            if i.find('s3'):
                return joined
            joined = joined + '.' + i
    return url


"""
Recursave function to deal with rdns returning more then one result
Takes: an blob (string, truple etc)
Returns: null if s3 keyword is not found
    The item it finds if s3 ketword is found
"""
def find_s3(item,level=0):
    if type(item) == str:
        if not (item.find('zonaws') == -1):
            if not (item.find('s3')):
                return item
    elif level<15:
        for i in item:
            try:
                iter(i)
                level=level+1
                return find_s3(i,level)
            except:
                return 'null'
    else:
        return "null"


"""
Takes: A file discreptor for a bind9 dns log file
Returns: a array with all domain names
"""
def get_queries(fi):
    domain_list=[]
    c=conn.cursor()
    for line in fi:
        dns=line.split()[6]
        c.execute('SELECT * FROM cache WHERE dns=?',(dns,))
        a = c.fetchone()
        if  (a==None):
            c.execute("INSERT INTO cache VALUES (?,?)",(dns,int(time.time())))
            domain_list.append(dns)
            conn.commit()
    return domain_list

"""
Takes a host name and does a dns lookup on it
Returns: the rdns lookup of the ip address behind the domain named result is a AWS s3 bucket 
"""
def rdns_lookup(host):
    try:
        ip=socket.gethostbyname(host)
    except:
        ip="bad"
    try:
        rev=socket.gethostbyaddr(ip)
    except:
        rev="bad"
    return rev


"""
Handles the multi threading
Takes: a domain name
Returns: the domain name back if looks to be a s3 bucket url
    False if not
"""
def multi_handler(domain):
    rev=rdns_lookup(domain)
    s3=find_s3(rev)
    if not (s3 == 'null' or s3 == None):
        return domain
    return False


"""Main"""
if __name__ == '__main__':
    fi = open(FILE_NAME, 'r')
    domain_list=get_queries(fi) #my array to genrate multi threaded
    pool = Pool(NUM_THREADS)
    results=pool.map(multi_handler,domain_list)
    pool.close()
    pool.join()
    for i in results:
        if i != False:
            name = make_s3name(i)
            try_s3(name)
                #print name

