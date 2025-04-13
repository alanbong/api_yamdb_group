![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

Cтек: `Python`, `python-dotenv`, `Django`, `DRF`, `Simple-JWT`

# api_yamdb
REST API для платформы YaMDb, где пользователи оставляют отзывы на фильмы, книги и музыку. Сервис формирует рейтинг произведений на основе пользовательских оценок.
### Описание:

- Админ добавляет произведения, категории и жанры.
- Каждое произведение относится к одной категории и нескольким жанрам.
- Рейтинг считается как средняя оценка пользователей (0–10), округлённая до целого.
- Анонимные пользователи могут только просматривать контент.
- Авторизованные — писать отзывы (по одному на произведение), ставить оценки и комментарии, редактировать и удалять свои.
- Модераторы могут управлять любыми отзывами и комментариями.
- Администраторы имеют полный доступ, включая управление ролями.
- Суперпользователь Django обладает правами администратора.


### Как запустить проект:

1. Клонируйте репозиторий и перейдите в него в командной строке:

  ```
  git clone git@github.com:Dauletnazarr/api_yamdb.git
  ```

  ```
  cd api_yamdb
  ```

2. Cоздайте и активируйте виртуальное окружение:

  #### Windows
  ```
  python -m venv venv
  . venv/Scripts/activate
  ```
  #### Linux/MacOS
  ```
  python3 -m venv venv
  source venv/bin/activate
  ```

3. Обновите версию pip
  #### Windows
  ```
  python -m pip install --upgrade pip
  ```
  #### Linux/MacOS
  ```
  python3 -m pip install --upgrade pip
  ```

4. Установите зависимости из файла requirements.txt:
  ```
  pip install -r requirements.txt
  ```

5. Выполните миграции:

  ```
  python manage.py migrate
  ```

6. Загрузите .CSV файлы:

  ```
 python manage.py import_all
  ```

7. Запустите проект:

  ```
  python manage.py runserver
  ```
  
8. Опционально. После запуска сервера полная версия документации доступна будет доступна [здесь](http://127.0.0.1:8000/redoc/)

### Примеры запросов к API:

Получить список всех произведений:
(Выводится список всех произведений, разбитый на страницы.
Доступна фильтрация по наименованию, жанру, категории, году)

```
GET http://127.0.0.1:8000/api/v1/titles/
```

Создание произведения и параметры:

```
POST http://127.0.0.1:8000/api/v1/titles/
```
```
{
  "name": "string",
  "year": 0,
  "description": "string",
  "genre": [
    "string"
  ],
  "category": "string"
}
```

Получение произведения по id:

```
GET http://127.0.0.1:8000/api/v1/titles/{titles_id}/
```

Удаление произведения:

```
DELETE http://127.0.0.1:8000/api/v1/titles/{titles_id}/
```

Получение списка всех отзывов:

```
GET http://127.0.0.1:8000/api/v1/titles/{title_id}/reviews/
```

## Авторы
Проект разработан:
* [Dauletnazar Mambetnazarov.](https://github.com/Dauletnazarr/)
* [Denis Bochkarev.](https://github.com/alanbong)
* [Ludmila Usacheva](https://github.com/Lusya4400)
* [Danil Tyapugin](https://github.com/DanilTyapugin)
