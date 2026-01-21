import locale

import requests

from src.wallbot.config.constants import ICON_EXCLAMATION, ICON_DIRECT_HIT, ICON_COLLISION, ICON_LOCK, ICON_RESERVED
from src.wallbot.config.settings import TELEGRAM_API_URL


def send_notification(chat_id, price, title, url_item, notes=None, notification_type='default'):
    # https://apps.timwhitlock.info/emoji/tables/unicode
    if notification_type == 'reserved':
        text = ICON_LOCK + ' *RESERVADO: ' + title + '*'
    elif notes is not None:
        text = ICON_EXCLAMATION + ' *' + title + '*'
    else:
        text = ICON_DIRECT_HIT + ' *' + title + '*'

    text += '\n'

    if notification_type == 'reserved':
        text += ICON_RESERVED + ' Este artículo ha sido reservado\n'
    elif notification_type == 'price':
        text += ICON_EXCLAMATION + ' Nuevo precio: '
    elif notes is not None:
        text += ICON_COLLISION + ' '

    text += locale.currency(price, grouping=True)

    if notes is not None:
        text += notes + ' ' + ICON_COLLISION

    text += '\n'
    text += 'https://es.wallapop.com/item/' + url_item

    bot_url = TELEGRAM_API_URL + \
        "sendMessage?chat_id=%s&parse_mode=markdown&text=%s" % (chat_id, text)
    requests.get(url=bot_url)
