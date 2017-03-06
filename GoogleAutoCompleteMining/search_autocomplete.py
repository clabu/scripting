from __future__ import print_function
import mysql.connector
import urllib
import sys
import xml.etree.ElementTree as ElementTree
from mysql.connector import errorcode
from xml.dom import minidom

DB_NAME = 'test'
TABLES = {}
TABLES['test'] = (

	"CREATE TABLE `" +DB_NAME+ "`.`search_results` ("
	"`id` INT NULL AUTO_INCREMENT,"
	"`search_string` VARCHAR(100) NULL,"
	"`results` VARCHAR(45) NULL,"
	"PRIMARY KEY (`id`));"

	)

## function to create database
def create_database(cursor):
	try:
		cursor.execute(
			"CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(DB_NAME))
	except mysql.connector.Error as err:
		print("Failed creating database: {}".format(err))
		#exit(1)



try:
	cnx = mysql.connector.connect(user='root', password='root',
		database='test', host='localhost')
	print("welcome, connection successful!")
	cursor = cnx.cursor()
	create_database(cursor)

except mysql.connector.Error as err:
	if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
		print("Something is wrong with your user name or password")
	elif err.errno == errorcode.ER_BAD_DB_ERROR:
		print("Database does not exists")
	else:
		print(err)
else:
	##finally create tables
	for name, ddl in TABLES.iteritems():
		try:
			print("Creating table {}: ".format(name), end='')
			cursor.execute(ddl)
		except mysql.connector.Error as err:
			if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
				print("already exists.")
			else:
				print(err.msg)
		else:
			print("OK")


searchWord = (str(sys.argv[1]));
print('Argument List:', searchWord)

add_search = ("INSERT INTO  " + DB_NAME + ".search_results"  +
	"(search_string, results) "
	"VALUES (%s, %s)")

def search(searchThis):
	params = urllib. urlencode({'q': searchThis, 'output': 'toolbar'})
	f = urllib.urlopen("http://google.com/complete/search?%s" % params)
	cache = f.read()
	#root = ElementTree.fromstring(cache)
	xmldoc = minidom.parseString(cache)
	itemlist = xmldoc.getElementsByTagName('suggestion')
	for s in itemlist:
    		print(s.attributes['data'].value)
    		data_search = (searchWord, s.attributes['data'].value)
    		cursor.execute(add_search, data_search)
	#for child in root:
		
	#print(cache)
#searchWord = (str(sys.argv[1]));


search(searchWord)



# Make sure data is committed to the database
cnx.commit()
cursor.close()
cnx.close()