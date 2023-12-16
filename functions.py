import datetime
import json
import random
from typing import List

from user_class import Pig

pigs_file = "pigs_data.json"
pigs = dict()


def save_pigs():
    with open(pigs_file, "w", encoding="utf-8") as file:
        pigs_data = {str(user_id): pig.to_dict() for user_id, pig in
                     pigs.items()}  # Преобразование идентификаторов в строки
        json.dump(pigs_data, file, ensure_ascii=False)


def load_pigs():
    global pigs
    try:
        with open(pigs_file, "r", encoding="utf-8") as file:
            pigs_data = json.load(file)
            for user_id, data in pigs_data.items():
                pigs[int(user_id)] = Pig.from_dict(data)
    except FileNotFoundError:
        print("Файл не найден")

async def shop_func(user_id, message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    buttons = [
        KeyboardButton("Автосалон"),
        KeyboardButton("Риэлтерское агентство"),
        KeyboardButton("Кафе"),
        KeyboardButton("Остаться дома")
    ]

    markup.add(*buttons)

    message_text: str = f"@{message.from_user.username}, вы захотели закупиться. Вы можете пойти в автосалон, в риэлтерское агенство, или просто сходить в кафе." \
                        f" Также вы можете остаться дома"



async def modify_weight(user_id, message):
    pig = pigs[user_id]  # Получаем хряка для данного пользователя

    random_number = random.randint(0, 1)  # Генерируем случайное число (0 или 1)

    weight_change = random.randint(-10, 25)  # Генерируем случайное число для изменения веса (от 1 до 10)
    if weight_change > 0:

        pig.weight += weight_change
        message_texts: list[str] = [
            f"@{message.from_user.username}, ваш хряк поел на {weight_change} кг. Теперь он весит {pig.weight} кг.",
            f"@{message.from_user.username}, ваш хряк валялся весь день и потолстел на {weight_change} кг. Теперь он весит {pig.weight} кг.",
            f"@{message.from_user.username}, ваш хряк потолстел на {weight_change} кг. Теперь он весит {pig.weight} кг.",
            f"@{message.from_user.username}, ваш хряк на {weight_change} кг стал толще. Теперь он весит {pig.weight} кг.",
            f"@{message.from_user.username}, ваш хряк потолстел на {weight_change} кг при невыясненных обстоятельствах. Теперь он весит {pig.weight} кг.",
            f"@{message.from_user.username}, ваш хряк поспал и стал больше на {weight_change} кг. Теперь он весит {pig.weight} кг.",
            f"@{message.from_user.username}, вы накормили своего любимого хряка лучшим кормом, и тот потолстел на {weight_change} кг. Теперь он весит {pig.weight} кг."
        ]
        message_text = random.choice(message_texts)
    elif weight_change == 0:
        message_text = f"@{message.from_user.username}, ваш хряк не изменился в весе. Теперь он весит {pig.weight} кг."
    else:
        pig.weight += weight_change
        message_texts = [
            f"@{message.from_user.username}, ваш хряк похудел на {- weight_change} кг. Теперь он весит {pig.weight} кг.",
            f"@{message.from_user.username}, вашего хряка покусали собаки отъев {- weight_change} кг. Теперь он весит {pig.weight} кг.",
            f"@{message.from_user.username}, ваш хряк долго не ел и похудел на {- weight_change} кг. Теперь он весит {pig.weight} кг.",
            f"@{message.from_user.username}, вашему хряку отъели {- weight_change} кг. Вы предполагаете, что их съела наука. Теперь он весит {pig.weight} кг.",
            f"@{message.from_user.username}, вашему хряку не посчастливилось встретиться с писькогрызом, и тот отъел {- weight_change} кг от вашего хряка. Теперь он весит {pig.weight} кг.",
            f"@{message.from_user.username}, ваш хряк похудел на {- weight_change} кг при невыясненных обстоятельствах. Теперь он весит {pig.weight} кг.",
            f"@{message.from_user.username}, ваш хряк упал в лужу и выплакал {- weight_change} кг слёз. Теперь он весит {pig.weight} кг."
        ]
        message_text = random.choice(message_texts)
        if pig.weight <= 15:
            pigs.pop(user_id)
            message_text = f"@{message.from_user.username}, ваш хряк умер от недоедания."

    pig.last_updated = datetime.datetime.now().strftime("%Y-%m-%d")  # Обновляем дату последнего обновления

    save_pigs()  # Сохраняем хряков

    await message.reply(text=message_text)

# auto_shop_choices = {
#     "Автомобиль": "Цена: $20,000",
#     "Мотоцикл": "Цена: $5,000",
#     "Аксессуары": "Цены разные"
# }
#
# async def auto_shop(user_id, message):

