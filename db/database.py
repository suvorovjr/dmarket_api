from pathlib import Path
from playhouse.sqlite_ext import SqliteExtDatabase
from config import DATABASE_NAME


# Создание абсолютного пути к файлу базы данных, соединяя путь к текущему файлу (__file__) и имя базы данных
DATABASE_URL = str(Path(__file__).resolve().parent) + DATABASE_NAME

# Создание объекта базы данных, указывая путь к файлу базы данных и параметр check_same_thread,
# который необходим для многопоточного доступа к базе данных в SQLite
db = SqliteExtDatabase(DATABASE_URL, check_same_thread=False)


