#  `$facet` (читается как «фасет»)
Позволяет выполнять **несколько независимых подагрегаций** в одном этапе конвейера `aggregate`. 

Возвращает результат в виде объекта, где 
* **ключи** соответствуют названиям "граней" (фасетов), 
* а **значения** — массивам с результатами подагрегаций.


### Пример:
Коллекция `Atlas > sample_airbnb > listingsAndReviews`. Нужно:
1. Подсчитать количество документов по странам (`Docs_by_countries`).
2. Получить 3 документа, которые были обновлены самыми последними (`3_last_updates`).

#### Совет:
Про использовании `$facet` удобнее
* Сначала сделать запрос по каждой грани отдельно
* А затем вставить эти проверенные стадии в `$facet`

#### Запрос 1:
```javascript
db.listingsAndReviews.aggregate([
  { $sortByCount: "$address.country" },
  { $project: {
      country: "$_id",
      number: "$count",
      _id: 0
    }
  }
]);
```

#### Запрос 2:
```javascript
db.listingsAndReviews.aggregate([
  { $sort: { last_scraped: -1 } }, 
  { $limit: 3 }
]);
```

#### Объединённый запрос:
```javascript
db.listingsAndReviews.aggregate([
  {
    $facet: {
        
      Docs_by_countries: [
        { $sortByCount: "$address.country" },
        { $project: {
            country: "$_id",
            number: "$count",
            _id: 0
          }
        }
      ],
        
      "3_last_updates": [
        { $sort: { last_scraped: -1 } },
        { $limit: 3 }
      ]
        
    }
  }
]);
```

#### Результат:

```json
{
  "Docs_by_countries": [
    {"country":"United States", "number": 1222 },
    {"country":"Turkey", "number": 661 },
    {"country":"Canada", "number":649},
    {"country":"Spain", "number":633},
    {"country":"Australia", "number":610},
    {"country":"Brazil", "number":606},
    {"country":"Hong Kong", "number":600},
    {"country":"Portugal", "number":555},
    {"country":"China", "number":19}
  ],
  "3_last_updates": [
    {
      "_id": "10240767",
      "listing_url": "https://www.airbnb.com/rooms/10084023",
      "name": "City center private room with bed",
      "summary": "House is located 5mins walk from Sham Shui Po and Prince Edward MTR. T…",
      "space": "The house is old fashion type, and paint the whole flat by ourselves, …",
      "description": "House is located 5mins walk from Sham Shui Po and Prince Edward MTR. T…",
      "neighborhood_overview": "Cheapest food, electronic device, clothing and other stuff in Hong Kon…",
      "notes": "Deposit of $1000 will be charged and will return back when check out i…",
      "transit": "Close to 3 different MTR Station, Sham shui Po and Shek Kei Mei 5 mins…",
      "access": "Living Room, Kitchen and Toilet, All cooking equipment can be used to…",
      "interaction": "A phone card of unlimited data will be provided during the stay, and p…",
      "house_rules": "1. 禁止吸煙, 只限女生入住 (除得到批准) No smoking and only female is allowed 2. 熱水爐是…",
      "property_type": "Guesthouse",
      "room_type": "Private room",
      "bed_type": "Futon",
      "minimum_nights": "1",
      "maximum_nights": "500",
      "cancellation_policy": "strict_14_with_grace_period",
      "last_scraped": "2019-03-11T04:00:00.000+00:00",
      "calendar_last_scraped": "2019-03-11T04:00:00.000+00:00",
      "first_review": "2015-12-22T05:00:00.000+00:00",
      "last_review": "2019-03-01T05:00:00.000+00:00",
      "accommodates": 1,
      "bedrooms": 1,
      "beds": 1,
      "number_of_reviews": 81,
      "bathrooms": 1.0,
      "amenities": [],
      "price": 181.00,
      "weekly_price": 1350.00,
      "monthly_price": 5000.00,
      "security_deposit": 0.00,
      "cleaning_fee": 50.00,
      "extra_people": 100.00,
      "guests_included": 1,
      "images": {},
      "host": {},
      "address": {},
      "availability": {},
      "review_scores": {},
      "reviews": []
    },
    {
      "_id": "10059244",
      ...
              
    },
    {
      "_id": "10084023",
      ...
              
    }
  ]
}
```


### Ключевые моменты:
* Результат каждой "грани" — массив. Что одновременно и плюс, и минус:
 * **Удобство:** можно получать разные срезы данных за один запрос.
 * **Неудобство:** Если обрабатывать документы дальше, то придётся преобразовывать массивы.

