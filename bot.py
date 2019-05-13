from config import *
from jobinja import *

# import telegram

# bot = telegram.Bot(token=TOKEN)
# print(bot.get_me())

from telegram.ext import Updater
from telegram.parsemode import ParseMode

updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher

from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup


def get_buttons():
    buttons = [InlineKeyboardButton(item, callback_data=item) for item in skill_mapping.keys()]
    mark_up = InlineKeyboardMarkup(
        split(buttons, 3)
    )
    return mark_up


def split(list_, n):
    return [list_[start::n] for start in range(n)]


def start(update, context):
    print('salam')
    buttons = [InlineKeyboardButton(item, callback_data=item) for item in skill_mapping.keys()]
    context.bot.send_message(chat_id=update.message.chat_id, text=start_message, reply_markup=get_buttons())


def send_feeds(feeds, chat_id, context, mode=None):
    for feed in feeds:
        link = feed['link'].split('?')[0]
        import urllib.parse
        link = urllib.parse.unquote(link)
        title = htmlspecialchars(feed['title'])
        pureContent = htmlspecialchars(feed['pureContent'])
        # mark_up = InlineKeyboardMarkup(
        #     [[InlineKeyboardButton('link', url=url)]]
        # )
        mark_up = None
        if isinstance(feed['workType'], (list,)):
            feed['workType'] = '، '.join(feed['workType'])
        context.bot.send_message(chat_id=chat_id, text=feed_message
                                 .format(title=title, company=feed['company'],
                                         location=feed['location'], workType=feed['workType'],
                                         minExperience=feed['minExperience'],
                                         price=feed['price'], minDegree=feed['minDegree'],
                                         pureContent=pureContent, link=link), reply_markup=mark_up,
                                 parse_mode=mode)
        print('done')
    return


def htmlspecialchars(text):
    return (
        text.replace("&", "&amp;").
            replace('"', "&quot;").
            replace("<", "&lt;").
            replace(">", "&gt;")
    )


def get_next_button(query, id):
    mark_up = InlineKeyboardMarkup(
        [[InlineKeyboardButton('صفحه بعد', callback_data=query + '_next_' + str(id))]]
    )
    return mark_up


def callback(update, context):
    query = update.callback_query.data
    chat_id = update.callback_query.message.chat_id
    message_id = update.callback_query.message.message_id
    # context.bot.deleteMessage(chat_id, message_id)
    print(query)
    if query in skill_mapping:
        feeds = crawl.getFeedBySkill(skill_mapping[query])
        if feeds == 'Error':
            return
        send_feeds(feeds['feeds'], chat_id, context, mode=ParseMode.HTML)
        if feeds['is_next_page']:
            context.bot.send_message(chat_id=chat_id, text=paging_message,
                                     reply_markup=get_next_button(query, feeds['next_max_id']))
        else:
            context.bot.send_message(chat_id=chat_id, text=menu_message, reply_markup=get_buttons())
    elif ('next' or 'prev') in query:
        last_query, mode, id = query.split('_')
        context.bot.editMessageText(chat_id=chat_id, message_id=message_id, text=next_page_message)
        feeds = crawl.getFeedBySkill(skill_mapping[last_query], id, mode)
        if feeds == 'Error':
            return
        send_feeds(feeds['feeds'], update.callback_query.message.chat_id, context, mode=ParseMode.HTML)
        print('done page {}'.format(id))
        if feeds['is_next_page']:
            context.bot.send_message(chat_id=chat_id, text=paging_message,
                                     reply_markup=get_next_button(last_query, feeds['next_max_id']))
        else:
            context.bot.send_message(chat_id=chat_id, text=menu_message, reply_markup=get_buttons())


from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.callbackquery import CallbackQuery

start_handler = CommandHandler('start', start)
query_handler = CallbackQueryHandler(callback)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(query_handler)

updater.start_polling()

crawl = jobinjaParser()
crawl.getFeedBySkill('PHP')
