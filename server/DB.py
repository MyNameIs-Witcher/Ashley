import pymysql
from config import host, port, user, password, main_db, tg_db


def test_connection():
    try:
        pymysql.connect(host=host, port=port, user=user, password=password,
                        database=main_db, cursorclass=pymysql.cursors.DictCursor)
        print("Connection to main DB success!")
    except Exception as ex:
        print("Connection refused...")
        print(ex)


def get_tg_users(table="customers"):
    with pymysql.connect(host=host, port=port, user=user, password=password,
                         database=tg_db, cursorclass=pymysql.cursors.DictCursor) as connection:
        with connection.cursor() as cursor:
            sql = f"SELECT * FROM {table};"
            cursor.execute(sql)
            result = cursor.fetchall()
    return result


def add_tg_user_to_db(user_id, nickname):
    with pymysql.connect(host=host, port=port, user=user, password=password,
                         database=tg_db, cursorclass=pymysql.cursors.DictCursor) as connection:
        with connection.cursor() as cursor:
            sql = f"INSERT IGNORE INTO customers (user_id, nickname) VALUES ({user_id}, {nickname})"
            cursor.execute(sql)
        connection.commit()


def add_info_to_db(user_id, phone_number, city,
                   name, surname, nickname, date_of_birth):
    city_name = "Санкт-Петербург" if (city is None) else city
    with pymysql.connect(host=host, port=port, user=user, password=password,
                         database=tg_db, cursorclass=pymysql.cursors.DictCursor) as connection:
        with connection.cursor() as cursor:
            sql = "REPLACE INTO customers (user_id, phone_num, city) VALUES (%s, %s, %s)"
            cursor.execute(sql, (user_id, phone_number, city_name))
        connection.commit()
    if name or surname or date_of_birth:
        with pymysql.connect(host=host, port=port, user=user, password=password,
                             database=main_db, cursorclass=pymysql.cursors.DictCursor) as connection:
            with connection.cursor() as cursor:
                sql = "REPLACE INTO friends (phone_num, username, surname, nickname, date_of_birth, city) " \
                      "VALUES (%s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (phone_number, name, surname, nickname, date_of_birth, city_name))
            connection.commit()


def autostart(table="customers"):
    with pymysql.connect(host=host, port=port, user=user, password=password,
                         database=tg_db, cursorclass=pymysql.cursors.DictCursor) as connection:
        with connection.cursor() as cursor:
            sql = f"SELECT user_id, time_to_notif  FROM {table} WHERE time_to_notif != 'None';"
            cursor.execute(sql)
            result = cursor.fetchall()
        for res in result:
            res['h'] = str(res['time_to_notif'].seconds // 3600)
            res['m'] = str(int(res['time_to_notif'].seconds / 60 % 60))
            res.pop('time_to_notif')
    return result


if __name__ == '__main__':
    # test_connection()
    # add_tg_user_to_db('456516914')
    # print(get_tg_users())
    # add_info_to_db('456516914', '89995201591', None, None, None, None, None)
    # print(get_tg_users())
    users_with_notif = autostart()
    for user in users_with_notif:
        user['h'] = str(user['time_to_notif'].seconds // 3600)
        user['m'] = str(int(user['time_to_notif'].seconds / 60 % 60))
        user.pop('time_to_notif')
    print(users_with_notif)
