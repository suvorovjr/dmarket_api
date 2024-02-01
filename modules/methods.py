from pyti.simple_moving_average import simple_moving_average as sma
from typing import List
from api.schemas import LastSale


def mov_av_5(history: List[LastSale]) -> list:
    """
    Вычисляет 5-периодную простую скользящую среднюю (SMA) для списка последних продаж.

    Эта функция предназначена для анализа тенденций цен на скины путем расчета скользящей средней,
    что может быть полезно для принятия решений о покупке или продаже. В качестве входных данных
    используется список объектов LastSale, каждый из которых содержит информацию о цене скина.
    Список цен на продажи инвертируется перед расчетом, чтобы убедиться, что расчет SMA начинается с самой
    последней продажи.

    :param history: Список объектов LastSale, представляющих историю продаж скинов.
                    Каждый объект LastSale должен иметь атрибут Price, который, в свою очередь,
                    содержит атрибут Amount с ценой продажи.

    :return: Список, содержащий значения 5-периодной простой скользящей средней для цен продаж.
             Длина возвращаемого списка будет соответствовать длине исходного списка цен минус 4
             (так как для расчета SMA по 5 точкам необходимо минимум 5 цен).
    """
    prices = [i.Price.Amount for i in history]
    prices.reverse()
    mov_av = [i for i in list(sma(prices, 5))]
    mov_av.reverse()
    return mov_av
