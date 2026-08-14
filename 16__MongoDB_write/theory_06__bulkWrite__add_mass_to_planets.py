"""
Для production крайне важно оптимизировать запросы к БД:
чем их меньше, тем лучше.
Метод bulk_write() позволяет
- собирать несколько запросов в список
- и выполнять их все за один заход.
"""


import json
from pymongo import MongoClient, UpdateOne, UpdateMany, InsertOne, DeleteOne, DeleteMany
from local_settings import MONGODB_URL_WRITE

# Извлекаем планеты из json-файла

def get_planets():
    with open("../planets.json", "r") as f:
        return json.load(f)

masses = {
    "Mercury": 0.33,
    "Venus": 4.87,
    "Earth": 5.97,
    "Mars": 0.642,
    "Jupiter": 1898,
    "Saturn": 568,
    "Uranus": 86.8,
    "Neptune": 102,
}


with MongoClient(MONGODB_URL_WRITE) as client:
    collection = client["ich_edit"]["planets_BAR"]

    # Если коллекция пустая - заполняем, если нет - пропускаем
    if collection.count_documents({}) == 0:
        print("The collection is empty. Adding data...")
        collection.insert_many(get_planets())
    else:
        print("The collection is not empty. Skipping data insertion.")


    # --- variant 1 ---------------------------------------------------------
    # Неоптимальное добавление нового поля:
    #   (один запрос -> одно изменение)
    for name, mass in masses.items():
        collection.update_one(
            {"name": name},
            {"$set": {"relativeMass": mass}}
        )


    # --- variant 2 ---------------------------------------------------------
    # Пакетное добавление нового поля к соответствующему документу коллекции
    #   (оптимальное добавление: один запрос -> много изменений)
    operations = [
        UpdateOne(
            {"name": name},
            {"$set": {"relativeMass": mass}}
        )
        for name, mass in masses.items()
    ]
    collection.bulk_write(operations)
