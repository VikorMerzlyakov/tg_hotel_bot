from peewee import IntegrityError
from database.core import crud
from loader import bot
from states.contact_information import UserRegister
from telebot.types import Message
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

@bot.message_handler(commands=['register'])
def start_survey(message: Message):
    try:
        # Получаем Telegram ID пользователя
        telegram_id = message.from_user.id

        # Проверяем, зарегистрирован ли пользователь
        users = crud.retrieve_users()()
        user = next((u for u in users if u['id_tg'] == telegram_id), None)

        if user:
            logging.info(f"Пользователь с Telegram ID {telegram_id} уже зарегистрирован.")
            bot.send_message(message.chat.id, "Вы уже прошли регистрацию! Переходите к поиску отелей.")
            return

        logging.info(f"Пользователь {telegram_id} начал регистрацию.")
        bot.set_state(message.from_user.id, UserRegister.first_name, message.chat.id)
        bot.send_message(message.chat.id, "Введите ваше имя:")
    except Exception as e:
        logging.error(f"Ошибка при обработке команды /register: {e}")

# Обработчик для получения имени
@bot.message_handler(state=UserRegister.first_name)
def get_first_name(message: Message):
    """
    Получает имя пользователя и запрашивает фамилию.
    """
    logging.debug(f"Получено сообщение от пользователя {message.from_user.id}: {message.text}")

    if message.text.isalpha():  # Проверяем, что имя состоит только из букв
        logging.info(f"Пользователь {message.from_user.id} ввел корректное имя: {message.text}")
        bot.send_message(message.chat.id, "Спасибо! Теперь введите вашу фамилию.")
        bot.set_state(message.from_user.id, UserRegister.last_name, message.chat.id)

        # Сохраняем имя в состояние
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['first_name'] = message.text
            logging.debug(f"Сохранено имя в состояние: {data['first_name']}")
    else:
        logging.warning(f"Пользователь {message.from_user.id} ввел некорректное имя: {message.text}")
        bot.send_message(message.chat.id, "Имя должно содержать только буквы. Попробуйте снова.")

# Обработчик для получения фамилии
@bot.message_handler(state=UserRegister.last_name)
def get_last_name(message: Message):
    """
    Получает фамилию пользователя и сохраняет данные в базу данных.
    """
    logging.debug(f"Получено сообщение от пользователя {message.from_user.id}: {message.text}")

    if message.text.isalpha():  # Проверяем, что фамилия состоит только из букв
        logging.info(f"Пользователь {message.from_user.id} ввел корректную фамилию: {message.text}")

        # Автоматически получаем Telegram ID пользователя
        telegram_id = message.from_user.id
        logging.debug(f"Получен Telegram ID пользователя: {telegram_id}")

        # Сохраняем фамилию в состояние и получаем остальные данные
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            first_name = data.get('first_name')  # Имя из состояния
            last_name = message.text  # Фамилия из сообщения
            logging.debug(f"Получены данные из состояния: first_name={first_name}, last_name={last_name}")

        if not first_name or not last_name:
            logging.error("Не удалось получить данные из состояния. Перезапуск регистрации.")
            bot.send_message(message.chat.id,
                             "Произошла ошибка при получении данных. Пожалуйста, начните регистрацию заново.")
            bot.delete_state(message.from_user.id, message.chat.id)
            return

        try:
            logging.info(f"Попытка создания пользователя с Telegram ID: {telegram_id}")
            # Добавляем пользователя через CRUD
            user_data = {
                'first_name': first_name,
                'last_name': last_name,
                'id_tg': telegram_id
            }
            crud.create_user()(user_data)

            logging.info(f"Пользователь успешно зарегистрирован: {user_data}")
            bot.send_message(message.chat.id, f"Вы успешно зарегистрированы! Ваш Telegram ID: {telegram_id}")
        except IntegrityError as e:
            logging.error(f"Ошибка при создании пользователя: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.")
        except Exception as e:
            logging.error(f"Неожиданная ошибка при работе с базой данных: {e}")
            bot.send_message(message.chat.id, "Произошла неожиданная ошибка. Пожалуйста, свяжитесь с администратором.")

        # Сбрасываем состояние
        bot.delete_state(message.from_user.id, message.chat.id)
        logging.debug(f"Состояние пользователя {message.from_user.id} сброшено.")
    else:
        logging.warning(f"Пользователь {message.from_user.id} ввел некорректную фамилию: {message.text}")
        bot.send_message(message.chat.id, "Фамилия должна содержать только буквы. Попробуйте снова.")