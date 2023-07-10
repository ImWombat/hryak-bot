import datetime
import random
import asyncio
import json
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
pigs_file = "pigs_data.json"  # Файл для хранения информации о хряках

pigs = {}  # Словарь для хранения информации о хряках


class Pig:
    def __init__(self, name, weight, last_updated=None):
        self.name = name
        self.weight = weight
        self.last_updated = last_updated

    def to_dict(self):
        return {
            "name": self.name,
            "weight": self.weight,
            "last_updated": self.last_updated,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name"),
            weight=data.get("weight"),
            last_updated=data.get("last_updated"),
        )


class PigRenameStates(StatesGroup):
    enter_new_name = State()


async def save_pigs():
    with open(pigs_file, "w", encoding="utf-8") as file:
        pigs_data = {user_id: pig.to_dict() for user_id, pig in pigs.items()}
        json.dump(pigs_data, file, ensure_ascii=False)


async def load_pigs():
    global pigs
    try:
        with open(pigs_file, "r", encoding="utf-8") as file:
            pigs_data = json.load(file)
            pigs = {user_id: Pig.from_dict(data) for user_id, data in pigs_data.items()}
    except FileNotFoundError:
        pigs = {}


async def rename_pig(user_id, message):
    str_user_id = str(user_id)  # Преобразуем user_id в строку для использования в качестве ключа
    if str_user_id in pigs:
        pig = pigs[str_user_id]
        # Проверяем, если у хряка уже установлено имя
        if pig.name is not None:
            await message.reply("У вашего хряка уже есть имя.")
            return

        await save_pigs()  # Сохраняем хряков

        await bot.send_message(chat_id=user_id, text=message_text)
    else:
        await bot.send_message(chat_id=user_id,
                               text=f"@{message.from_user.username}, у вас нет хряка. Начните с команды /start")


@dp.message_handler(state=PigRenameStates.enter_new_name)  # Обработчик для ввода нового имени хряка
async def enter_new_name_handler(message: types.Message, state: FSMContext):
    user_id = message.chat.id

    pig_name = message.text  # Получаем введенное новое имя хряка
    pig = pigs[user_id]  # Получаем хряка для данного пользователя
    pig.name = pig_name  # Изменяем имя хряка

    await state.finish()  # Завершаем состояние ожидания ввода нового имени

    await save_pigs()  # Сохраняем хряков

    await message.reply(f"Ник вашего хряка успешно изменен на: {pig.name}")


@dp.message_handler(commands=["rename"], state="*")
async def rename(message: types.Message, state: FSMContext):
    user_id = message.chat.id

    if user_id in pigs:
        await rename_pig(user_id, message)
    else:
        await message.reply("У вас нет хряка. Начните с команды /start.")


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    user_id = message.chat.id

    if user_id not in pigs:
        pigs[user_id] = Pig(name=None, weight=100)
        await message.reply("Бот был успешно настроен.")
    else:
        await message.reply("У вас уже есть хряк.")


@dp.message_handler(commands=["weight"])
async def weight_handler(message: types.Message):
    user_id = str(message.chat.id)  # Преобразуем user_id в строку для использования в качестве ключа

    if user_id in pigs:
        pig = pigs[user_id]
        await message.reply(f"Ваш хряк {pig.name if pig.name else 'без имени'}. Текущий вес: {pig.weight} кг.")
    else:
        await message.reply("У вас нет хряка. Начните с команды /start.")


@dp.message_handler(commands=["grow"])
async def grow(message: types.Message):
    user_id = message.chat.id

    if user_id in pigs:
        pig = pigs[user_id]  # Получаем хряка для данного пользователя

        if pig.last_updated is None:
            await modify_weight(user_id, message)
        else:
            last_updated = datetime.datetime.strptime(pig.last_updated, "%Y-%m-%d %H:%M:%S")
            current_time = datetime.datetime.now()
            time_difference = current_time - last_updated

            if time_difference.days >= 1:  # Проверяем, прошел ли хотя бы 1 день с последнего обновления
                await modify_weight(user_id, message)
            else:
                await bot.send_message(chat_id=user_id,
                                       text=f"@{message.from_user.username}, обновление веса уже выполнялось сегодня.")
    else:
        await bot.send_message(chat_id=user_id,
                               text=f"@{message.from_user.username}, у вас нет хряка. Начните с комкоманды /start")


async def modify_weight(user_id, message):
    pig = pigs[user_id]  # Получаем хряка для данного пользователя

    random_number = random.randint(0, 1)  # Генерируем случайное число (0 или 1)

    if random_number == 0:
        weight_change = random.randint(1, 10)  # Генерируем случайное число для изменения веса (от 1 до 10)
        pig.weight += weight_change
        message_text = f"@{message.from_user.username}, ваш хряк потолстел на {weight_change} кг."
    else:
        weight_change = random.randint(1, 10)  # Генерируем случайное число для изменения веса (от 1 до 10)
        pig.weight -= weight_change
        message_text = f"@{message.from_user.username}, ваш хряк похудел на {weight_change} кг."

    pig.last_updated = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Обновляем дату последнего обновления

    await save_pigs()  # Сохраняем хряков

    await bot.send_message(chat_id=user_id, text=message_text)


async def main():
    try:
        await load_pigs()  # Загрузка данных о хряках
    except FileNotFoundError:
        pigs = {}  # Если файл не найден, создаем пустой словарь хряков

    dp.register_message_handler(start_handler, commands=["start"])
    dp.register_message_handler(weight_handler, commands=["weight"])
    dp.register_message_handler(rename, commands=["rename"], state="*")
    dp.register_message_handler(grow, commands=["grow"])

    await dp.start_polling()


if __name__ == "__main__":
    # Запуск бота
    asyncio.run(main())
