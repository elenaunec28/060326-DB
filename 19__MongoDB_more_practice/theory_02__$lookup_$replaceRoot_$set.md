## $lookup
Стадия $lookup позволяет объединить данные из двух коллекций, аналогично операции JOIN в SQL.  
Она связывает коллекции по ключу, и результат добавляется в новый массив.

### Ключевое отличие $lookup от SQL JOIN: 
В MongoDB результат `$lookup` представляет собой массив документов из связанной коллекции,   
а не простое добавление полей.  
Если для каждой записи из исходной коллекции найдены несколько записей в связанной коллекции,   
то в итоговом документе будет массив этих записей.

*Пример:*

1-4. Добавить в коллекцию Atlas sample_restaurants.restaurants новые поля:  
- avgScore — среднее значение всех оценок для этого ресторана (grades.score),  
- grade — последнюю оценку из отзывов (grades.grade) (первый элемент массива)  
- totalReviews — общее количество отзывов.

(решение не оптимальное, но хорошо иллюстрирующее `$lookup`)

1. Получаем агрегирующие значения:
   - "Анвиндим" массив оценок `grades` 
   - и группируем по id ресторана `restaurant_id`

```
db.getCollection('restaurants').aggregate(
  [
    // добавляем оценки как поля в новые документы колллекции
    { $unwind: { path: '$grades' } },

    // группируем оценки по каждому ресторану
    {
      $group: {
        _id: '$restaurant_id',
        avgScore: { $avg: '$grades.score' },
        totalReviews: { $sum: 1 },
        grade: { $first: '$grades.grade' }
      }
    }
 ])
```

2. Группировка изменила коллекцию.  
   Поэтому "джойним" изменённую коллекцию (новые агрегированные поля) с тем, что было.
```
db.getCollection('restaurants').aggregate(
  [
    ...
   
    {
      $lookup: {
        from: 'restaurants',
        localField: '_id',
        foreignField: 'restaurant_id',
        as: 'restaurantInfo'
      }
    }
  ]
 )
```

| Поле           | Значение         | Что значит                                     |
| -------------- |------------------|------------------------------------------------|
| `from`         | `restaurants`    | В какую коллекцию "смотреть" для поиска данных |
| `localField`   | `_id`            | Поле из текущей коллекции                      |
| `foreignField` | `restaurant_id`  | Поле из коллекции `from`, с которым сравнивать |
| `as`           | `restaurantInfo` | Имя нового поля, в которое добавится результат |

В этом примере все данные коллекции `restaurants` добавятся к соответствующим документам  
текущей коллекции именно как элементы массива `restaurantInfo`.

3. Коллекция добавилась в виде "неудобных массивов".
   Решение: "анвиндим" все ненужные массивы

```
db.getCollection('restaurants').aggregate(
  [
    ...
   
    { 
      $unwind: '$restaurantInfo' 
    },
    
  ]
)
```



4. `$set
   Теперь к добавленным данным можно обращаться как к полноценным полям.
   И далее в этот объект переносятся все необходимые поля из существующей коллекции с помощью команды (стадии) `$set`.

```
db.getCollection('restaurants').aggregate(
  [
  
    ...
    {
      $set: {
        'restaurantInfo.avgScore': '$avgScore',
        'restaurantInfo.totalReviews': '$totalReviews',
        'restaurantInfo.grade': '$grade'
      }
    }
  ]
)
```
5. `$replaceRoot`
   Обычно следующим этапом идёт именно эта команда (стадия) `$replaceRoot`.
   В результате чего новый объект становится основным документом 
   (а поля "бывшего основного" документа при этом удаляются)

```
db.getCollection('restaurants').aggregate(
  [
    ...

    {
      $replaceRoot: { newRoot: '$restaurantInfo' }
    },

  ]
```

### Все стадии полностью

```
db.getCollection('restaurants').aggregate(
  [
    // добавляем оценки как поля в новые документы колллекции
    { $unwind: { path: '$grades' } },

    // группируем оценки по каждому ресторану
    {
      $group: {
        _id: '$restaurant_id',
        avgScore: { $avg: '$grades.score' },
        totalReviews: { $sum: 1 },
        grade: { $first: '$grades.grade' }
      }
    },

    // добавляем существующую коллекцию ресторанов в каждый документ в виде массива №restaurantInfo№
    {
      $lookup: {
        from: 'restaurants',
        localField: '_id',
        foreignField: 'restaurant_id',
        as: 'restaurantInfo'
      }
    },

    // превращаем массив "restaurantInfo№ в объект "restaurantInfo"
    { $unwind: { path: '$restaurantInfo' } },

    // добавляем новые поля статистика внутрь объекта "restaurantInfo"
    {
      $set: {
        'restaurantInfo.avgScore': '$avgScore',
        'restaurantInfo.totalReviews': '$totalReviews',
        'restaurantInfo.grade': '$grade'
      }
    },

    // делаем объект "restaurantInfo" основным документом
    {
      $replaceRoot: { newRoot: '$restaurantInfo' }
    },

    // сохраняем результат в новой коллекции restaurants_
    {
      $out: {
        db: 'sample_restaurants',
        coll: 'restaurants_'
      }
    }
  ]
);
```
