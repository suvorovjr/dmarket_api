import datetime
import json
from playhouse.sqlite_ext import Model, CharField, FloatField, TextField, DateTimeField, IntegerField

from db.database import db


def default(o):
    """
    Функция для преобразования даты и времени в формат ISO для сериализации JSON.

    :param o: Объект даты или времени.
    :return: Строковое представление даты/времени в формате ISO.
    """
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


class JSONField(TextField):
    """
    Пользовательское текстовое поле для хранения и извлечения данных в формате JSON.
    """
    def db_value(self, value):
        """
        Сериализует значение в JSON строку перед сохранением в базу данных.

        :param value: Значение для сериализации.
        :return: Строковое представление JSON.
        """
        return json.dumps(value, default=default)

    def python_value(self, value):
        """
        Десериализует строку JSON обратно в объект Python при извлечении из базы данных.

        :param value: Строковое представление JSON для десериализации.
        :return: Десериализованный объект Python.
        """
        if value is not None:
            return json.loads(value)


class BaseModel(Model):
    """
    Базовый класс модели, определяющий общую базу данных для всех моделей.
    """
    class Meta:
        database = db


class Skin(BaseModel):
    """
    Модель скина, представляющая информацию о скине в базе данных.

    :param title: Название скина.
    :param game: Игра, к которой относится скин.
    :param LastSales: История последних продаж в формате JSON.
    :param avg_price: Средняя цена скина.
    :param update_time: Время последнего обновления информации о скине.
    """
    title = CharField()
    game = CharField()
    LastSales = JSONField()
    avg_price = FloatField()
    update_time = DateTimeField()


class SkinOffer(BaseModel):
    """
    Модель предложения скина, содержащая детали купленных или проданных скинов.

    :param title: Название скина.
    :param AssetID: Уникальный идентификатор скина.
    :param game: Игра, к которой относится скин.
    :param buyPrice: Цена покупки.
    :param buyTime: Время покупки.
    :param OfferID: Идентификатор предложения.
    :param sellTime: Время продажи.
    :param sellPrice: Цена продажи.
    :param fee: Комиссия за продажу.
    """
    title = CharField(null=True)
    AssetID = CharField()
    game = CharField(null=True)
    buyPrice = FloatField(null=True)
    buyTime = DateTimeField(null=True)
    OfferID = CharField(null=True)
    sellTime = DateTimeField(null=True)
    sellPrice = FloatField(null=True)
    fee = IntegerField(default=7)