"""
Умеет выполнять классификацию клиентов по трём фичам

Запускаем из python3:
    python3 service.py
Проверяем работоспособность:
    curl http://0.0.0.0:5001/
"""
import http.server
import json
import logging
import os
import socketserver
from http import HTTPStatus

import psycopg2
from msgpack import packb, unpackb
from redis import Redis

# файл, куда посыпятся логи модели
FORMAT = '%(asctime)-15s %(message)s'
log_file_name = "/www/app/service.log"
logging.basicConfig(filename=log_file_name, level=logging.INFO, format=FORMAT)


class Handler(http.server.SimpleHTTPRequestHandler):
    """Простой http-сервер"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_response(self) -> dict:
        response = {'health-check': 'ok'}
        params_parsed = self.path.split('?')

        if self.path.startswith('/ping/'):
            response = {'message': 'pong'}

        # Реализуем API profile
        elif self.path.startswith('/user/profile'):
            response = self.get_user_profile()

        # Реализуем API /rates/user_id
        elif self.path.startswith('/rates'):
            response = self.get_user_watch_history()

        return response

    def get_user_profile(self) -> dict:
        user_id = self.path.split('/')[-1]
        logging.info(f'Поступил запрос по пользователю user_id={user_id}')
        redis_profile_key = f'profile:{user_id}'
        # проверяем наличие объекта в Redis-кеше
        if redis_interactor.is_cached(redis_profile_key):
            logging.info(f'Профиль пользователя user_id={user_id} присутствует в кеше')
            response = redis_interactor.get_data(redis_profile_key)
        # если ключ отcутствует в кеше - выполняем "тяжёлый" SQL-запрос в Postgres
        else:
            logging.info(f'Профиль пользователя user_id={user_id} отсутствует в кеше, выполняем запрос к Postgres')
            user_profile = [None, None]  # [num_rating, avg_rating]
            try:
                user_profile = postgres_interactor.get_sql_result(
                    f"""
                    SELECT COUNT(rating) as rate_count, AVG(rating) as avg_rating
                    FROM movie.ratings
                    WHERE userId = {user_id}"""
                )[0]
            except Exception as e:
                logging.info(f'Произошла ошибка запроса к Postgres:\n{e}')
            response = {'user_id': user_id, 'num_rating': user_profile[0], 'avg_rating': user_profile[1]}
            logging.info(f'Сохраняем профиль пользователя user_id={user_id} в Redis-кеш')
            redis_interactor.set_data(redis_profile_key, response)
        return response

    def get_user_watch_history(self) -> dict:
        """
        Для каждого переданного user_id API должен возвращать историю оценок, которые ставил этот user_id в виде

        {
            "0": {"movie_id": 4119470, "rating": 4.5, "timestamp": "2019-09-03 10:00:00"},
            "1": {"movie_id": 5691170, "rating": 2.0, "timestamp": "2019-09-05 13:23:00"},
            "2": {"movie_id": 3341191, "rating": 5.0, "timestamp": "2019-09-08 16:40:00"}
        }
        """
        user_id = self.path.split('/')[-1].split('?')[0]
        logging.info(f'Поступил запрос по рейтингам пользователя user_id={user_id}')
        redis_profile_key = f'user_rate:{user_id}'
        # проверяем наличие объекта в Redis-кеше
        if redis_interactor.is_cached(redis_profile_key):
            logging.info(f'Рейтинги пользователя user_id={user_id} присутствуют в кеше')
            response = redis_interactor.get_data(redis_profile_key)
        # если ключ отcутствует в кеше - выполняем "тяжёлый" SQL-запрос в Postgres
        else:
            logging.info(f'Рейтинги пользователя user_id={user_id} отсутствуют в кеше, выполняем запрос к Postgres')
            user_rates = [[]]
            try:
                user_rates = postgres_interactor.get_sql_result(
                    f"""
                        SELECT movieid, rating, to_char(to_timestamp(timestamp), 'YYYY-MM-DD HH24:MI:SS') 
                        FROM movie.ratings 
                        WHERE userid = {user_id};
                        """)
            except Exception as e:
                logging.info(f'Произошла ошибка запроса к Postgres:\n{e}')
            response = {}
            for i in range(len(user_rates)):
                response[i] = {"movie_id": user_rates[i][0], "rating": user_rates[i][1], "timestamp": user_rates[i][2]}
            logging.info(f'Сохраняем рейтинги пользователя user_id={user_id} в Redis-кеш')
            redis_interactor.set_data(redis_profile_key, response)
        return response


    def do_GET(self):
        # заголовки ответа
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(self.get_response()).encode())


class PostgresStorage:
    def __init__(self):
        # подключение к Postgres
        params = {
            "host": os.environ['APP_POSTGRES_HOST'],
            "port": os.environ['APP_POSTGRES_PORT'],
            "user": 'postgres'
        }
        self.conn = psycopg2.connect(**params)

        # дополнительные настройки
        psycopg2.extensions.register_type(
            psycopg2.extensions.UNICODE,
            self.conn
        )
        self.conn.set_isolation_level(
            psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT
        )
        self.cursor = self.conn.cursor()

    def get_sql_result(self, sql_str):
        """Исполняем SQL и возвращаем PandasDF"""
        # исполняем SQL
        self.cursor.execute(sql_str)
        # получаем результат запроса
        query_data = [a for a in self.cursor.fetchall()]
        # коммит необязательно, но для порядка необходим
        self.conn.commit()
        return query_data


class RedisStorage:
    def __init__(self):
        REDIS_CONF = {
            "host": os.environ['APP_REDIS_HOST'],
            "port": os.environ['APP_REDIS_PORT'],
            "db": 0
        }
        self.storage = Redis(**REDIS_CONF)

    def set_data(self, redis_key, data):
        self.storage.set(redis_key, packb(data, use_bin_type=True))

    def get_data(self, redis_key):
        result = dict()
        redis_data = self.storage.get(redis_key)
        if redis_data is not None:
            result = unpackb(redis_data, raw=False)
        return result

    def is_cached(self, redis_key: str) -> bool:
        return self.storage.exists(redis_key)


postgres_interactor = PostgresStorage()
logging.info('Инициализирован класс для работы с Postgres')
redis_interactor = RedisStorage()
logging.info('Инициализирован класс для работы с Redis')
if os.path.exists(log_file_name):
    os.chmod(log_file_name, 0o0777)

if __name__ == '__main__':
    classifier_service = socketserver.TCPServer(('', 5000), Handler)
    logging.info('Приложение инициализировано')
    classifier_service.serve_forever()
