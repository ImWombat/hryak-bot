import datetime
import json
import random

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


async def modify_weight(user_id, message):
    pig = pigs[user_id]  # Получаем хряка для данного пользователя

    random_number = random.randint(0, 1)  # Генерируем случайное число (0 или 1)

    weight_change = random.randint(-10, 25)  # Генерируем случайное число для изменения веса (от 1 до 10)
    if weight_change > 0:

        pig.weight += weight_change
        message_text = f"@{message.from_user.username}, ваш хряк потолстел на {weight_change} кг. Теперь он весит {pig.weight}"
    elif weight_change == 0:
        message_text = f"@{message.from_user.username}, ваш хряк не изменился в весе. Теперь он весит {pig.weight}"
    else:
        pig.weight += weight_change
        message_text = f"@{message.from_user.username}, ваш хряк похудел на {- weight_change} кг. Теперь он весит {pig.weight}"
        if pig.weight <= 15:
            pigs.pop(user_id)
            message_text = f"@{message.from_user.username}, ваш хряк умер от недоедания."
    pig.last_updated = datetime.datetime.now().strftime("%Y-%m-%d")  # Обновляем дату последнего обновления

    save_pigs()  # Сохраняем хряков

    await message.reply(text=message_text)
