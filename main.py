import telebot
from telebot import types
import psycopg2
import requests
from psycopg2 import sql
from config import bot_token, bot_owner_chat_id


bot = telebot.TeleBot(bot_token)


@bot.message_handler(commands=['start'])
def send_big_description(message):
    description = """
Ух, кто-то открыл описание! Ну ок...

💬 Связаться с решалой: /get_help
    
- Тебе нужно будет выбрать тип задачи (экзамен, дз, etc), срочность и предмет. Затем подробно опиши суть задачи, приложи все имеющиеся у тебя фото и файлы по заданию. А можешь этого и не делать. Мы все равно свяжемся с тобой, если ты отправил заявку. Удачи!

📋 Снова открыть подробное описание (but why?..): /start

Пока мы больше ничего не умеем 😔
    """
    bot.send_message(message.chat.id, description)


@bot.message_handler(commands=['get_help'])
def get_help(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton('Экзамен'))
    markup.add(types.KeyboardButton('Домашка'))
    markup.add(types.KeyboardButton('Другое'))
    bot.send_message(message.chat.id, 'С чем нужна помощь?', reply_markup=markup)
    bot.register_next_step_handler(message, save_problem)

def save_problem(message):
    # Save the problem type to the answers table
    answers = {"chat_id": message.chat.id, "problem": message.text}
    
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton('Сейчас'))
    markup.add(types.KeyboardButton('Завтра'))
    markup.add(types.KeyboardButton('Позже'))
    bot.send_message(message.chat.id, 'Что по срокам?', reply_markup=markup)
    bot.register_next_step_handler(message, save_urgency, answers)

def save_urgency(message, answers):
    # Save the urgency level to the answers table
    answers["urgency"] = message.text
    
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton('Химия'))
    markup.add(types.KeyboardButton('Физика'))
    markup.add(types.KeyboardButton('Математика'))
    markup.add(types.KeyboardButton('Другое'))
    bot.send_message(message.chat.id, 'Какой предмет?', reply_markup=markup)
    bot.register_next_step_handler(message, save_subject, answers)

def save_subject(message, answers):
    # Save the subject to the answers table
    answers["subject"] = message.text

    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    markup.add(types.KeyboardButton('Отправить заявку'))

    bot.send_message(message.chat.id, 'Хорошо, теперь дай всю дополнительную '
                                      'информацию, какой располагаешь (текст, фото, файлы к экзамену с примерами). '
                                      'Либо нажми просто кнопку "Отправить заявку", мы все равно с тобой свяжемся',
                                      reply_markup=markup)
    bot.register_next_step_handler(message, save_additional_info, answers)


def save_additional_info(message, answers):
    if message.text == 'Отправить заявку':
        send_request_to_owner(answers)
    else:
        # bot.forward_message(chat_id=bot_owner_chat_id, from_chat_id=message.chat.id, message_id=message.message_id)
        if answers.get('additional_resources'):
            answers['additional_resources'].append({'message_id': message.id})
        else:
            answers['additional_resources'] = [{'message_id': message.id}]

        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(types.KeyboardButton('Отправить заявку'))

        bot.send_message(message.chat.id, 'Если ты хочешь добавить еще какие-то файлы, '
                                            'сдеалй это. Или нажми "Отправить заявку".', reply_markup=markup)
        bot.register_next_step_handler(message, save_additional_info, answers)


def send_request_to_owner(answers):
    # bot.send_message(bot_owner_chat_id, make_request_text(answers))
    bot.send_message(bot_owner_chat_id, create_request_message_for_owner(answers))
    for additional_resource in answers.get('additional_resources', []):
        bot.forward_message(chat_id=bot_owner_chat_id, from_chat_id=answers['chat_id'], message_id=additional_resource['message_id'], disable_notification=True)
    markup = types.ReplyKeyboardMarkup()
    bot.send_message(answers['chat_id'], 'Твоя заявка принята! Скоро с тобой свяжется наш решала.', reply_markup=markup)


def create_request_message_for_owner(answers):
    user_url = get_user_url_from_chat_id(answers['chat_id'])
    template = """
🌟 Новый заказ от профиля {0}!

🔬 Предмет: {1}
😩 Проблема: {2}
⏰ Срочность: {3}
📝 Дополнительная информация: {4}.

    """

    return template.format(user_url, answers['subject'], answers['problem'], answers['urgency'],
        'в пересланных сообщениях' if answers.get('additional_resources') else 'не предоставлена')


def get_user_url_from_chat_id(chat_id):
    user = bot.get_chat(chat_id)
    if user.username:
        return f"https://t.me/{user.username}"
    else:
        return None


# bot.infinity_polling()
bot.polling()