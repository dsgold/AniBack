from collections import namedtuple
import datetime
import psycopg2
import json


# Функция подключения к базе данных
def connect():
    conn = psycopg2.connect(
        host="localhost",
        database="AniMania",
        user="postgres",
        password="4123"
    )
    return conn


# Функция получения данных из таблицы "anime_list"

def get_anime_list():
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, name, url, episodes, release, image, genre_list, voice_over, update_date FROM anime_list")
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        result = []
        for row in rows:
            result.append(dict(zip(columns, row)))
        result = json.loads(json.dumps(result, ensure_ascii=False))
        for res in result:
            cur.execute(
                "SELECT number, name, release_date from anime_next_episodes where anime_id = %s", (res['id'],)
            )
            next_episodes = cur.fetchall()
            columns = [desc[0] for desc in cur.description]
            subres = []
            for row in next_episodes:
                subres.append(dict(zip(columns, row)))
            res['next_episodes'] = json.loads(json.dumps(subres, ensure_ascii=False))
        return json.dumps(result, ensure_ascii=False)
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def insert_anime(name, url, episodes, release, image, genre_list, voice_over, next_episodes):
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("INSERT INTO anime_list (name, url, episodes, release, image, genre_list, voice_over, update_date) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
                    "ON CONFLICT (name) DO UPDATE "
                    "SET url = EXCLUDED.url, episodes = EXCLUDED.episodes, release = EXCLUDED.release, "
                    "image = EXCLUDED.image, genre_list = EXCLUDED.genre_list, voice_over = EXCLUDED.voice_over, update_date = EXCLUDED.update_date "
                    "RETURNING id",
                    (name, url, episodes, release, image, genre_list, voice_over,
                     datetime.datetime.now().strftime('%d.%m.%Y %H:%M')))
        new_id = cur.fetchone()[0]
        for ep in next_episodes:
            cur.execute(
                "INSERT INTO anime_next_episodes (number, name, release_date, anime_id) VALUES (%s, %s, %s, %s) ON CONFLICT (name,release_date) DO UPDATE SET number = EXCLUDED.number, name = EXCLUDED.name, release_date = EXCLUDED.release_date",
                (ep['number'], ep['name'], ep['release_date'], new_id))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def update_anime(name, url, episodes, release, image, genre_list, voice_over, next_episodes):
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        print(next_episodes)
        cur.execute(
            "UPDATE anime_list SET name = %s, url = %s, episodes = %s, release = %s, image = %s, genre_list = %s, voice_over = %s, update_date = %s WHERE name = %s RETURNING id",
            (name, url, episodes, release, image, genre_list, voice_over,
             datetime.datetime.now().strftime('%d.%m.%Y %H:%M'), name))
        new_id = cur.fetchone()[0]

        for ep in next_episodes:
            cur.execute(
                "INSERT INTO anime_next_episodes (number, name, release_date, anime_id) VALUES (%s, %s, %s, %s) ON CONFLICT (name,release_date) DO UPDATE SET number = EXCLUDED.number, name = EXCLUDED.name, release_date = EXCLUDED.release_date",
                (ep['number'], ep['name'], ep['release_date'], new_id))
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


# Функция удаления данных из таблицы "anime_list" по полю "name"
def delete_anime_by_name(name):
    conn = None
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("DELETE FROM anime_list WHERE name = %s", (name,))
        conn.commit()
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
