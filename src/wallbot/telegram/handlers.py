import logging
import textwrap
from re import sub

import telebot

from src.wallbot.database.db_helper import DBHelper
from src.wallbot.database.models import ChatSearch


class TelegramHandlers:
    def __init__(self, bot: telebot.TeleBot, db: DBHelper):
        self.bot = bot
        self.db = db
        self._register_handlers()

    def _register_handlers(self):
        self.bot.message_handler(
            commands=['start', 'help'])(self.send_welcome)
        self.bot.message_handler(
            commands=['add'])(self.add_search)
        self.bot.message_handler(
            commands=['delete'])(self.delete_search)
        self.bot.message_handler(
            commands=['list'])(self.get_searches)
        self.bot.message_handler(
            commands=['stop'])(self.stop_bot)
        self.bot.message_handler(
            func=lambda message: message.text)(self.unknown_command)

    def unknown_command(self, message):
        self.bot.send_message(
            message.chat.id,
            'Comando no reconocido. Usa /help para ver los comandos disponibles.'
        )

    def send_welcome(self, message):
        welcome_text = textwrap.dedent("""\
            *Uso:*
            \t\t/help
                                       
            *Añadir búsqueda:*
            \t\t/add `búsqueda,min-max,categoria_ID_1,categoria_ID_2,...`
                     (precio y categorías son opcionales)
                                       
            Ejemplos:
            \t\t/add zapatos azules 
                     (sin precio ni categorías)
            \t\t/add zapatos rojos,5-25 
                     (5 es el precio mínimo, 25 el máximo)
            \t\t/add zapatos verdes,20,1,2,3 
                     (20 es el precio mínimo; 1,2,3 son IDs de categorías)
                                       
            *Borrar búsqueda:*
            \t\t/delete `búsqueda`
                                       
            Ejemplos:
            \t\t/delete zapatos rojos
            \t\t/delete zapatos azules
                                       
            *Mostrar búsquedas:*
            \t\t/list
                                       
            *Detener el bot y eliminar todas las búsquedas:*
            \t\t/stop
        """)
        self.bot.send_message(
            message.chat.id, welcome_text, parse_mode='Markdown')

    def add_search(self, message):
        cs = ChatSearch()
        cs.chat_id = message.chat.id
        parameters = str(message.text).split(' ', 1)

        if len(parameters) < 2:
            # Solo puso el comando
            self.bot.send_message(
                message.chat.id, 'Uso incorrecto del comando. Usa /help para más información.')
            return

        token = ' '.join(parameters[1:]).split(',')

        if len(token) < 1:
            # Puso un espacio después del comando y nada más
            self.bot.send_message(
                message.chat.id, 'Uso incorrecto del comando. Usa /help para más información.')
            return

        cs.kws = token[0].strip()

        if len(token) > 1:
            rango = token[1].split('-')
            cs.min_price = rango[0].strip()
            if len(rango) > 1:
                cs.max_price = rango[1].strip()

        if len(token) > 2:
            cs.cat_ids = sub('[\s+]', '', ','.join(token[2:]))
            if len(cs.cat_ids) == 0:
                cs.cat_ids = None

        cs.username = message.from_user.username
        cs.name = message.from_user.first_name
        cs.active = 1
        logging.info('%s', cs)
        self.db.add_search(cs)
        self.bot.send_message(
            message.chat.id, 'Búsqueda `' + cs.kws + '` añadida.', parse_mode='Markdown')

    def delete_search(self, message):
        parameters = str(message.text).split(' ', 1)
        if len(parameters) < 2:
            self.bot.send_message(
                message.chat.id, 'Uso incorrecto del comando. Usa /help para más información.')
            return

        kws = ' '.join(parameters[1:])
        self.db.del_chat_search(message.chat.id, kws)
        self.bot.send_message(
            message.chat.id, 'Búsqueda `' + kws + '` eliminada.', parse_mode='Markdown')

    def get_searches(self, message):
        text = ''

        for chat_search in self.db.get_chat_searches(message.chat.id):
            if len(text) > 0:
                text += '\n'

            text += 'Búsqueda: `' + chat_search.kws + '`'

            if chat_search.min_price is not None:
                text += ' | Precio: `'
                text += chat_search.min_price
                text += '`'

            if chat_search.max_price is not None:
                text += '-'
                text += '`' + chat_search.max_price + '`'

            if chat_search.cat_ids is not None:
                text += ' | Categorías: `'
                text += chat_search.cat_ids + '`'

        if len(text) > 0:
            self.bot.send_message(message.chat.id, text, parse_mode='Markdown')
        else:
            self.bot.send_message(
                message.chat.id, 'No tienes búsquedas activas.')

    def stop_bot(self, message):
        self.db.del_all_chat_searches(message.chat.id)
        self.bot.send_message(
            message.chat.id, 'Bot detenido. Todas tus búsquedas han sido eliminadas.')
