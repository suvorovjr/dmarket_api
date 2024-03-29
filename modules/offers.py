import datetime
from typing import List
from db.crud import SelectSkinOffer, SkinOffer
from api.schemas import SellOffer, CreateOffer, CreateOffers, LastPrice, EditOffer, EditOffers, \
    DeleteOffers, DeleteOffer, OfferDetails
from api.dmarketapi import DMarketApi
from config import PUBLIC_KEY, SECRET_KEY, SellParams, logger, GAMES
from time import time, sleep


class History:
    """
    Класс предназначен для управления историей скинов, включая обработку закрытых сделок покупки и продажи.
    Отвечает за сохранение информации о купленных и проданных скинах в базу данных.
    """
    def __init__(self, bot: DMarketApi):
        """
        Конструктор класса History.

        :param bot: Экземпляр бота для взаимодействия с API DMarket.
        """
        self.bot = bot

    @staticmethod
    def skins_db() -> List[SkinOffer]:
        """
        Получает список скинов из базы данных, которые еще не были проданы.

        :return: Список объектов SkinOffer, представляющих скины, доступные для продажи.
        """
        skins = SelectSkinOffer.select_all()
        if skins:
            return [i for i in skins if not i.sellTime]
        return list()

    async def save_skins(self):
        """
        Сохраняет информацию о закрытых сделках покупки и проданных предложениях скинов.
        Обновляет базу данных скинов, добавляя новые купленные скины и обновляя информацию о проданных.
        """
        try:
            buy = await self.bot.closed_targets(limit='100')
            logger.debug(f'Получены закрытые сделки: {buy}')

            buy = buy.Trades
            buy = [SellOffer(AssetID=i.AssetID, buyPrice=i.Price.Amount) for i in buy]
            logger.debug(f'Обработанные закрытые сделки: {buy}')

            sold = []
            for game in GAMES:
                #Здесь мы изменили status='OfferStatusSold' на status='OfferStatusDefault'
                #так как с OfferStatusSold запрос не проходит видимо потому что вначале нету проданных скинов
                sell = await self.bot.user_offers(status='OfferStatusDefault', game=game, limit='20')
                logger.debug(f'Получены проданные предложения для {game}: {sell}')
                sell = sell.Items
                sold += sell

            logger.debug(f'Всего проданных предложений: {sold}')

            sell = [SellOffer(AssetID=i.AssetID, OfferID=i.Offer.OfferID,
                              sellPrice=i.Offer.Price.Amount, sellTime=datetime.datetime.now(),
                              title=i.Title, game=i.GameID) for i in sold]
            logger.debug('Обработанные проданные предложения')

            buy_asset_ids = [s.AssetID for s in SelectSkinOffer.select_all()]
            logger.debug(f'ID купленных активов: {buy_asset_ids}')

            for b in buy:
                if b.AssetID not in buy_asset_ids:
                    SelectSkinOffer.create_skin(b)
                    logger.debug(f'Создан скин для {b.AssetID}')

            skins = self.skins_db()
            logger.debug('Получена информация из skins_db')
            logger.debug(skins)
            for s in skins:
                for i in sell:
                    if s.AssetID == i.AssetID:
                        s.title = i.title
                        s.sellPrice = i.sellPrice * (1 - s.fee / 100)
                        s.OfferID = i.OfferID
                        s.sellTime = i.sellTime
                        s.game = i.game
                        logger.debug(f'Обновлена информация скина: {s.AssetID}')
                        break
            SelectSkinOffer.update_sold(skins)
            logger.debug('Обновление информации о проданных скинах завершено')

        except Exception as e:
            logger.error(f'Ошибка в save_skins: {type(e).__name__}, {e}')
            raise


class Offers:
    """
    Класс для создания, обновления и удаления предложений продажи скинов на платформе.
    Включает в себя методы для добавления скинов на продажу, обновления цен на существующие предложения
    и удаления предложений из активных продаж.
    """
    def __init__(self, bot: DMarketApi):
        """
        Инициализирует экземпляр класса Offers для управления предложениями продажи скинов.

        Этот конструктор сохраняет экземпляр API для взаимодействия с платформой DMarket и настраивает
        параметры ценообразования для продажи скинов на основе заданных конфигурационных значений.

        :param bot: Экземпляр DMarketApi, через который осуществляется взаимодействие с API DMarket.
        """
        self.bot = bot
        self.max_percent = SellParams.MAX_PERCENT
        self.min_percent = SellParams.MIN_PERCENT

    async def add_to_sell(self):
        """
        Добавляет скины в список продаж, устанавливая цены на основе заданных параметров и комиссии платформы.
        Синхронизирует информацию о скинах с инвентарем пользователя и базой данных предложений.
        """
        skins = SelectSkinOffer.select_not_sell()
        inv_skins = []
        invent = []
        for game in GAMES:
            inv = await self.bot.user_items(game=game)
            inv_skins += inv.objects
        for i in inv_skins:
            fee = 7
            if 'custom' in i.fees['dmarket']['sell']:
                fee = int(i.fees['dmarket']['sell']['custom']['percentage'])
            if i.inMarket:
                invent.append(SellOffer(AssetID=i.itemId, title=i.title, game=i.gameId, fee=fee))
        create_offers = []
        for i in invent:
            for j in skins:
                if i.AssetID == j.AssetID:
                    price = j.buyPrice * (1 + self.max_percent / 100 + i.fee / 100)
                    i.sellPrice = price
            try:
                create_offers.append(CreateOffer(AssetID=i.AssetID,
                                                 Price=LastPrice(Currency='USD', Amount=round(i.sellPrice, 2))))
            except TypeError:
                pass

        add = await self.bot.user_offers_create(CreateOffers(Offers=create_offers))
        if add.Result:
            for i in add.Result:
                for j in invent:
                    if i.CreateOffer.AssetID == j.AssetID:
                        j.sellPrice = i.CreateOffer.Price.Amount
                        j.OfferID = i.OfferID
                        SelectSkinOffer.update_offer_id(j)
        logger.debug(f'Add to sell: {add}')

    @staticmethod
    def offer_price(max_p, min_p, best) -> float:
        """
        Рассчитывает цену предложения на продажу скина, основываясь на текущей лучшей цене и заданных пределах.

        :param max_p: Максимальная цена предложения.
        :param min_p: Минимальная цена предложения.
        :param best: Текущая лучшая цена на рынке.
        :return: Оптимальная цена для предложения продажи.
        """
        if best < min_p:
            order_price = min_p
        elif min_p < best <= max_p:
            order_price = best - 0.01
        else:
            order_price = max_p
        return order_price

    async def update_offers(self):
        """
        Обновляет цены на активные предложения продажи, сравнивая их с текущими рыночными ценами и корректируя
        в соответствии с заданной стратегией ценообразования и комиссией платформы.
        """
        on_sell = sorted([i for i in SelectSkinOffer.select_not_sell() if i.OfferID],
                         key=lambda x: x.title)

        # names = [i.title for i in on_sell]
        # agr = await self.bot.agregated_prices(names=names, limit=len(names))
        items_to_update = list()

        for i in on_sell:
            itemid = OfferDetails(items=[i.AssetID])
            details = await self.bot.user_offers_details(body=itemid)
            best_price = details.objects[0].minListedPrice.amount / 100
            if i.sellPrice != best_price:
                max_sell_price = i.buyPrice * (1 + self.max_percent / 100 + i.fee / 100)
                min_sell_price = i.buyPrice * (1 + self.min_percent / 100 + i.fee / 100)
                price = self.offer_price(max_sell_price, min_sell_price, best_price)
                if round(price, 2) != round(i.sellPrice, 2):

                    i.sellPrice = price
                    items_to_update.append(EditOffer(OfferID=i.OfferID, AssetID=i.AssetID,
                                                     Price=LastPrice(Currency='USD', Amount=round(i.sellPrice, 2))))

        updated = await self.bot.user_offers_edit(EditOffers(Offers=items_to_update))
        for i in updated.Result:
            for j in on_sell:
                if i.EditOffer.AssetID == j.AssetID:
                    j.sellPrice = i.EditOffer.Price.Amount
                    j.OfferID = i.NewOfferID
                    logger.debug(f'{i.EditOffer.AssetID} {j.AssetID}')
                    SelectSkinOffer.update_offer_id(j)
        logger.debug(f'UPDATE OFFERS: {updated}')

    async def delete_all_offers(self):
        """
        Удаляет все активные предложения продажи пользователя, очищая список предложений на платформе.
        """
        offers = await self.bot.user_offers(status='OfferStatusActive')
        do = [DeleteOffer(itemId=o.AssetID, offerId=o.Offer.OfferID, price=o.Offer.Price) for o in offers.Items]
        await self.bot.user_offers_delete(DeleteOffers(objects=do))
