# dmarket_bot
Bot for automatic trading on dmarket 




### Для использования:

- git clone https://github.com/timagr615/dmarket_bot.git
- cd dmarket_bot
- Создайте виртуальное окружение, например python3 -m venv venv
- Затем активируйте virtualenv . venv/bin/activate
- pip install -r requirements.txt
- Создать файл `credentials.py` в корневой директории с следующим содержанием:

```python
PUBLIC_KEY = "your public api key"
SECRET_KEY = "your secret api key"
```

- Запустить бота можно с помощью файла `main.py`

## Возможности
- Мультиигровая торговля. Поддержка всех игр, доступных на dmarket
- Автоматический анализ базы скинов для каждой игры
- Выставление ордеров, отобранных по 15-ти различным параметрам. Борьба ордеров за первое место.
- Автоматическое выставление скинов на продажу после покупки. Корректировка цен в соответствии с настройками и борьба за 1 место.
## Параметры
Все параметры бота находятся в файле `config.py` в корневой директории бота.
### Подробное описание параметров:
- `logger_config`- конфигурация логгера
```python
logger_config = {
    "handlers": [
        {"sink": sys.stderr, 'colorize': True, 'level': 'INFO'},
        # {"sink": "log/debug.log", "serialize": False, 'level': 'DEBUG'},
        {"sink": "log/info.log", "serialize": False, 'level': 'INFO'},
    ]
}
logger.configure(**logger_config)
```
`"sink": sys.stderr` -  выводлогов в консоль
`"sink": "log/info.log"` - вывод логов в файл
`'level': 'INFO'` это уровень логов. Возможные уровни: `TRACE, DEBUG, INFO, SUCCESS, WARNING, ERROR , CRITICAL`. Каждый следующий слева направо уровень запрещайт вывод логов более низкого уровня. То есть если указан уровень `INFO`, сообщения с уровнем `TRACE, DEBUG` выводиться не будут.
- `GAMES = [Games.CS, Games.DOTA, Games.RUST]` - список игр, по которым будет производиться торговля. Доступные значения: `Games.CS, Games.DOTA, Games.RUST, Games.TF2`
- `PREV_BASE = 60 * 60 * 4` - обновление базы скинов каждые `PREV_BASE` секунд
- `ORDERS_BASE = 60 * 10`- обновление базы ордеров каждые `ORDERS_BASE` секунд
- `BAD_ITEMS` - список слов. Если слово входит в название предмета, то он не будет куплен.

### BuyParams -  параметры выставления ордеров
-  `STOP_ORDERS_BALANCE = 1000` - Останавливать выставление ордеров при балансе на 10 долларов меньше минимальной цены ордера
- `MIN_AVG_PRICE = 400` - Минимальная средняя цена за последние 20 покупок предмета в центах. Предметы с более низкой ценой не будут добавляться в базу скинов.
- `MAX_AVG_PRICE = 3500` - Максимальная средняя цена за последние 20 покупок предмета в центах. Предметы с более высокой ценой не будут добавляться в базу скинов.
- `FREQUENCY = True` - Включить ли алгоритм высокочастотной торговли. При значении True следует указывать параметр `PROFIT_PERCENT = 6` или меньше, а параметр `GOOD_POINTS_PERCENT = 50` или выше
-    `MIN_PRICE = 300` - минимальная средняя цена. Ниже этой цены ордер выставляться не будет.
-    `MAX_PRICE = 3000` - максимальная средняя цена. Выше этой цены ордер на предмет не поставится.

-    `PROFIT_PERCENT = 7` - минимальный профит, который мы хотим получить, если купим предмет по цене текущего первого ордера.
-    `GOOD_POINTS_PERCENT = 50` - процент точек в истории 20-ти последних продаж, соответствующих параметру `PROFIT_PERCENT = 7`. В данном случае, если менне 50 процентов точек продавались с профитом меньше 7 процентов, то ордер на такой предмет ставиться не будет.

-    `ALL_SALES = 100` - минимальное количество продаж за весь период, ниже которого ордер выставляться не будет
-    `DAYS_COUNT = 20` - не менее `SALE_COUNT = 15` продаж за `DAYS_COUNT = 20` дней. Отбор по популярности`
-    `SALE_COUNT = 15` - не менее `SALE_COUNT = 15` продаж за `DAYS_COUNT = 20` дней. Отбор по популярности`
-    `LAST_SALE = 2`  - последняя продажа не позднее LAST_SALE дней назад
-   `FIRST_SALE = 15`  - первая покупка не позже FIRST_SALE дней назад

-    `MAX_COUNT_SELL_OFFERS = 30` - максимальное количество выставленных предметов на продажу. Выше 30 ордер не поставится.

-    `BOOST_PERCENT = 24` - удаляем до 3 точек, которые выше средней цены на 24 процента
-    `BOOST_POINTS = 3` - удаляем до 3 точек, которые выше средней цены на 24 процента

-    `MAX_THRESHOLD = 1`  - Максимальное повышение цены на MAX_THRESHOLD процентов от текущего ордера. Максимальное повышение цены нашего ордера от цены текущего первого ордера
-   `MIN_THRESHOLD = 3` - Максимальное понижение цены нашего ордера от цены текущего. Задают границы изменения цены для ордера

### SellParams - парамтры выставления на продажу
- `MIN_PERCENT = 4` - минимальный процент профита
-   `MAX_PERCENT = 12` - максимальный процент профита
