import locale
import logging
import time
from decimal import Decimal
from re import sub
from typing import List

from src.wallbot.config.settings import SEARCH_INTERVAL, CLEANUP_INTERVAL, CLEANUP_RETENTION_HOURS
from src.wallbot.database.models import ChatSearch
from src.wallbot.telegram.notifications import send_notification
from src.wallbot.wallapop.api_client import WallapopClient


class WallapopMonitor:
    def __init__(self, db):
        self.db = db
        self.client = WallapopClient()
        self.is_running = False
        self.last_cleanup_time = 0

    def start(self):
        self.is_running = True
        logging.info("Starting monitoring to Wallapop")

        while self.is_running:
            try:
                self._monitor_cycle()
                time.sleep(SEARCH_INTERVAL)
            except KeyboardInterrupt:
                logging.info("Stopping monitoring")
                self.stop()
            except Exception as e:
                logging.error(f"Error in monitoring cycle: {e}")
                time.sleep(SEARCH_INTERVAL)

    def stop(self):
        self.is_running = False
        logging.info("Monitoring stopped")

    def _monitor_cycle(self):
        # Check if it's time to run cleanup
        current_time = time.time()
        if current_time - self.last_cleanup_time >= CLEANUP_INTERVAL:
            self._run_cleanup()
            self.last_cleanup_time = current_time

        searches: List[ChatSearch] = self.db.get_chats_searches()

        for search in searches:
            try:
                response = self.client.search_items(search)
                logging.info(f"API response: {response}")
                if response:
                    self._handle_response(search, response)
            except Exception as e:
                logging.error(
                    f"Error processing search for chat `{search.chat_id}`: {e}")

    def _run_cleanup(self):
        """Run database cleanup to remove old items"""
        try:
            logging.info(f"Running database cleanup - removing items older than {CLEANUP_RETENTION_HOURS} hours")
            self.db.delete_items(CLEANUP_RETENTION_HOURS)
            logging.info("Database cleanup completed successfully")
        except Exception as e:
            logging.error(f"Error during database cleanup: {e}")

    def _handle_response(self, search, response):
        try:
            items = response['data']['section']['payload']['items']

            for item in items:
                self._process_item(item, search.chat_id)

        except (KeyError, ValueError) as e:
            logging.error(f"Error processing API response: {e}")

    def _process_item(self, item, chat_id):
        item_id = item['id']
        item_price = item['price']['amount']
        item_title = item['title']
        item_user = item['user_id']
        item_web_slug = item['web_slug']
        item_reserved = item['reserved']['flag']

        logging.info(
            'Found: id=%s, price=%s, title=%s, user=%s, reserved=%s',
            str(item_id),
            locale.currency(item_price, grouping=True),
            item_title,
            item_user,
            item_reserved
        )

        existing_item = self.db.search_item(item_id, chat_id)

        if existing_item is None:
            self._process_new_item(
                item_id, chat_id, item_title, item_price, item_web_slug, item_user, item_reserved)
        else:
            self._process_existing_item(
                existing_item, item_id, item_price, item_title, item_web_slug, chat_id, item_reserved)

    def _process_new_item(self, item_id, chat_id, title, price, web_slug, user_id, reserved):
        self.db.add_item(item_id, chat_id, title, price,
                         web_slug, user_id, reserved=reserved)

        if reserved:
            send_notification(chat_id, price, title, web_slug,
                              notification_type='reserved')
        else:
            send_notification(chat_id, price, title, web_slug)

        logging.info(
            'New: id=%s, price=%s, title=%s, reserved=%s',
            str(item_id),
            locale.currency(price, grouping=True),
            title,
            reserved
        )

    def _process_existing_item(self, existing_item, item_id, new_price, title, web_slug, chat_id, new_reserved):
        """Procesa actualizaciones de precio y estado de reserva"""
        # Convertir precios a decimales para comparación
        new_price_decimal = Decimal(sub(r'[^\d.]', '', str(new_price)))
        old_price_decimal = Decimal(sub(r'[^\d.]', '', existing_item.price))

        price_changed = new_price_decimal < old_price_decimal
        reservation_changed = not existing_item.reserved and new_reserved

        if price_changed:
            # Construir historial de precios
            price_history = locale.currency(existing_item.price, grouping=True)
            if existing_item.observaciones:
                price_history += ' < ' + existing_item.observaciones

            # Actualizar item en base de datos
            self.db.update_item(item_id, str(new_price),
                                price_history, new_reserved)

            # Notificar cambio de precio
            send_notification(chat_id, new_price, title, web_slug,
                              ' < ' + price_history, notification_type='price')

            logging.info(
                'Price drop: id=%s, price=%s, title=%s',
                str(item_id),
                locale.currency(new_price, grouping=True),
                title
            )
        elif reservation_changed:
            self.db.update_item(item_id, existing_item.price,
                                existing_item.observaciones, new_reserved)

            send_notification(chat_id, new_price, title,
                              web_slug, notification_type='reserved')

            logging.info(
                'Reserved: id=%s, title=%s',
                str(item_id),
                title
            )
        elif new_reserved != existing_item.reserved:
            self.db.update_item(item_id, existing_item.price,
                                existing_item.observaciones, new_reserved)
