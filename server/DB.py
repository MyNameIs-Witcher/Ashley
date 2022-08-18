import pymysql
from config import host, port, user, password, db_name

try:
    connection = pymysql.connect(host=host, port=port, user=user, password=password,
                                 database=db_name, cursorclass=pymysql.cursors.DictCursor)
    print('Connection success!')
except Exception as ex:
    print('Connection refused...')
    print(ex)
