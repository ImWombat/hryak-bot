from functions import pigs, save_pigs, load_pigs, modify_weight, restart_handler
from aiogram import executor

import datetime
from user_class import PigRenameStates, Pig
from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from config import TOKEN

bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

MAX_NAME_LENGTH = 50

# Укорачиваем имена и избавляем их от лишних символов
def process_name(name):
    return name.replace('\n', " ")[:MAX_NAME_LENGTH]


@dp.message_handler(state=PigRenameStates.enter_new_name)  # Обработчик для ввода нового имени хряка
async def enter_new_name_handler(message: types.Message, state: FSMContext):
    user_id = message.from_id

    pig_name = message.text[:50]  # Получаем введенное новое имя хряка
    pig = pigs[user_id]  # Получаем хряка для данного пользователя
    pig.name = process_name(pig_name)  # Изменяем имя хряка

    await state.finish()  # Завершаем состояние ожидания ввода нового имени

    save_pigs()  # Сохраняем хряков

    await message.reply(f"Ник вашего хряка успешно изменен на: {pig.name}")


@dp.message_handler(commands=["rename"], state="*")
async def rename(message: types.Message, state: FSMContext):
    user_id = message.from_id

    if user_id in pigs:
        # Запрашиваем новое имя хряка у пользователя
        await message.reply(text="Введите в ответы новое имя для своего хряка:")
        # Устанавливаем состояние ожидания ввода нового имени
        await PigRenameStates.enter_new_name.set()
    else:
        await message.reply("У вас нет хряка. Начните с команды /start.")


@dp.message_handler(commands=["grow"])
async def grow(message: types.Message):
    user_id = message.from_id

    if user_id in pigs:
        pig = pigs[user_id]  # Получаем хряка для данного пользователя

        if pig.last_updated is None:
            await modify_weight(user_id, message)
        else:
            last_updated = datetime.datetime.strptime(pig.last_updated, "%Y-%m-%d")
            current_time = datetime.datetime.now()
            time_difference = current_time - last_updated

            if time_difference.days >= 1:  # Проверяем, прошел ли хотя бы 1 день с последнего обновления
                await modify_weight(user_id, message)
            else:
                await message.reply(text=f"@{message.from_user.username}, обновление веса уже выполнялось сегодня. "
                                         f"Ваш хряк весит {pig.weight} кг.")
    else:
        await message.reply(text=f"@{message.from_user.username}, у вас нет хряка. Начните с команды /start")


@dp.message_handler(commands=["restart"])
async def start_handler(message: types.Message):
    user_id = message.from_id  # Получаем идентификатор чата

    if user_id in pigs:
        await message.reply("У вас уже есть хряк. ВЫ ТОЧНО ХОТИТЕ НАЧАТЬ СНАЧАЛА?!")
        restart_handler()

    else:
        restart_handler()

    save_pigs()  # Сохраняем хряков


@dp.message_handler(commands=["weight"])
async def weight_handler(message: types.Message):
    user_id = message.from_id

    if user_id in pigs:
        pig = pigs[user_id]

        if pig.weight <= 50:
            image_path = "images/image_1.jpg"
        elif 50 < pig.weight <= 100:
            image_path = "images/image_2.jpg"
        elif 100 < pig.weight <= 150:
            image_path = "images/image_3.jpg"
        elif 150< pig.weight <= 200:
            image_path = 'images/image_5.jpg'
        elif 200 < pig.weight <= 250:
            image_path = 'images/image_4.jpg'
        elif 250 < pig.weight <= 500:
            image_path = 'images/image_6.jpg'
        else:
            image_path = 'images/image_7.jpg'

        with open(image_path, "rb") as photo:
            await message.reply_photo(photo=photo,
                                      caption=f"Ваш {process_name(pig.name) if pig.name else 'безымянный хряк'} весит {pig.weight} кг.")
    else:
        await message.reply("У вас нет хряка. Начните с команды /start.")

def replace_name(name, user_id):
    if "\n" in name or len(name) > 50:
        return 'Я уебан с длинным ником, мой ID:' + str(user_id)
    else:
        return name

@dp.message_handler(commands=["top"])
async def top_handler(message: types.Message):
    sorted_pigs = sorted(pigs.values(), key=lambda pig: pig.weight, reverse=True)
    top_message = "Топ 10 хряков по весу:\n\n"
    for index, pig in enumerate(sorted_pigs[:10], start=1):
        top_message += f"{index}. {replace_name(pig.name, message.from_id)} - {pig.weight} кг \n"
    await message.reply(top_message)


if __name__ == "__main__":
    load_pigs()  # Загрузка данных о хряках
    # Запуск бота
    executor.start_polling(dispatcher=dp, skip_updates=True)