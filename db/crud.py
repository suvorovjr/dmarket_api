from typing import List
from datetime import datetime
from loguru import logger
from peewee import DoesNotExist
from db.models import Skin, SkinOffer, db
from api.schemas import SkinHistory, MarketOffer, SellOffer


db.connect()
Skin.create_table()
SkinOffer.create_table()
db.close()


class SelectSkin:
    """
    Класс, предоставляющий статические методы для работы с моделью Skin в базе данных.
    Включает функционал для создания, поиска и обновления записей скинов.
    """
    @staticmethod
    def create_all_skins(items: List[SkinHistory]):
        """
        Создает записи для всех скинов в базе данных.

        :param items: Список объектов SkinHistory для создания записей.
        """
        skins = [Skin(**i.dict()) for i in items]
        with db.atomic():
            Skin.bulk_create(skins, batch_size=500)

    @staticmethod
    def skin_existence(item: MarketOffer):
        """
        Проверяет наличие скина в базе данных по названию.

        :param item: Объект MarketOffer, содержащий название скина для проверки.
        :return: True, если скин существует в базе данных, иначе False.
        """
        skin = Skin.select().where(Skin.title == item.title)
        if skin:
            return True
        return False

    @staticmethod
    def find_by_name(items: List[SkinHistory]):
        """
        Обновляет или создает записи скинов в базе данных на основе предоставленного списка.

        :param items: Список объектов SkinHistory для обновления или создания.
        """
        skins_to_update = list()
        skin_to_create = list()
        for item in items:
            try:
                skin = Skin.get(Skin.title == item.title)
                it = item.dict()
                skin.avg_price = it['avg_price']
                skin.LastSales = it['LastSales']
                skin.update_time = it['update_time']
                skins_to_update.append(skin)
            except DoesNotExist:
                skin_to_create.append(Skin(**item.dict()))
        with db.atomic():
            Skin.bulk_update(skins_to_update,
                             fields=[Skin.avg_price, Skin.LastSales, Skin.update_time],
                             batch_size=500)
        with db.atomic():
            Skin.bulk_create(skin_to_create, batch_size=500)

    @staticmethod
    def select_all() -> List[SkinHistory]:
        """
        Возвращает список всех скинов из базы данных.

        :return: Список объектов SkinHistory.
        """
        skins = Skin.select()
        return [SkinHistory.from_orm(skin) for skin in skins]

    @staticmethod
    def select_update_time(now, delta) -> List[SkinHistory]:
        """
        Возвращает список скинов, которые не обновлялись в течение определенного времени.

        :param now: Текущее время в формате timestamp.
        :param delta: Временной интервал в секундах, в течение которого скины не обновлялись.
        :return: Список объектов SkinHistory.
        """
        skins = Skin.select().where(Skin.update_time < datetime.fromtimestamp(now - delta))
        if skins:
            return [SkinHistory.from_orm(skin) for skin in skins]
        return []


class SelectSkinOffer:
    """
    Класс, предоставляющий статические методы для работы с моделью SkinOffer в базе данных.
    Включает функционал для создания, обновления и удаления записей предложений скинов.
    """
    @staticmethod
    def create_skin(item: SellOffer) -> None:
        """
        Создает новую запись предложения скина в базе данных.

        :param item: Объект SellOffer, содержащий информацию для создания записи.
        """
        new_skin = SkinOffer.create(
            title=item.title,
            game=item.game,
            AssetID=item.AssetID,
            buyPrice=item.buyPrice,
            buyTime=item.buyTime,
            OfferID=item.OfferID,
            sellTime=item.sellTime,
            sellPrice=item.sellPrice
        )
        new_skin.save()

    @staticmethod
    def update_sold(skins: List[SkinOffer]):
        """
        Обновляет информацию о проданных скинах в базе данных.

        :param skins: Список объектов SkinOffer для обновления.
        """
        if skins:
            with db.atomic():
                SkinOffer.bulk_update(skins, fields=[SkinOffer.title, SkinOffer.sellPrice,
                                                     SkinOffer.sellTime, SkinOffer.OfferID])
        else:
            logger.debug("Список skins пустой. Нет объектов для обновления.")
    @staticmethod
    def select_not_sell() -> List[SellOffer]:
        """
        Возвращает список предложений скинов, которые еще не были проданы.

        :return: Список объектов SellOffer.
        """
        skins = SkinOffer.select().where(SkinOffer.sellTime == None)
        return [SellOffer.from_orm(s) for s in skins]

    @staticmethod
    def select_all() -> List[SkinOffer]:
        """
        Возвращает список всех предложений скинов из базы данных.

        :return: Список объектов SkinOffer.
        """
        skins = SkinOffer.select()
        return skins

    @staticmethod
    def delete_all():
        """
        Удаляет все записи предложений скинов из базы данных.
        """
        skins = SkinOffer.select()
        for s in skins:
            s.delete_instance()

    @staticmethod
    def update_by_asset(skin: SellOffer):
        """
        Обновляет запись предложения скина в базе данных, используя AssetID.

        :param skin: Объект SellOffer, содержащий обновленную информацию.
        """
        try:
            item = SkinOffer.get(SkinOffer.AssetID == skin.AssetID)
            item.OfferID = skin.OfferID
            item.sellTime = skin.sellTime
            item.sellPrice = skin.sellPrice
            item.save()
        except DoesNotExist:
            pass

    @staticmethod
    def update_offer_id(skin: SellOffer):
        """
        Обновляет идентификатор предложения и другую информацию скина в базе данных.

        :param skin: Объект SellOffer, содержащий обновленную информацию.
        """
        try:
            item = SkinOffer.get(SkinOffer.AssetID == skin.AssetID)
            item.OfferID = skin.OfferID
            item.title = skin.title
            item.fee = skin.fee
            item.sellPrice = skin.sellPrice
            # item.sell_time = skin.sell_time
            # item.sell_price = skin.sell_price
            # item.update_time = skin.update_time
            item.save()
        except DoesNotExist:
            pass
