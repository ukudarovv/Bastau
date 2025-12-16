# Bastau - Медицинский Telegram бот

Проект состоит из Django REST API backend и Telegram бота для поиска врачей, просмотра отзывов и рейтингов.

## Структура проекта

```
Bastau/
├── bot/                    # Telegram бот (aiogram 3.x)
│   ├── handlers/          # Обработчики команд и сообщений
│   ├── keyboards/         # Клавиатуры для бота
│   ├── middlewares/      # Middleware (логирование, throttling)
│   ├── services/         # Сервисы (API клиент)
│   ├── states/           # FSM состояния
│   ├── utils/            # Утилиты
│   ├── config.py         # Конфигурация бота
│   └── main.py           # Точка входа бота
├── med/                   # Django backend
│   ├── api/              # API приложение
│   │   ├── models.py     # Модели данных
│   │   ├── views.py      # API views
│   │   ├── serializers.py # Сериализаторы
│   │   └── management/commands/fill_db.py # Команда заполнения БД
│   ├── med/              # Настройки Django
│   │   └── settings.py   # Конфигурация Django
│   └── manage.py         # Django management
├── requirements.txt       # Зависимости Python
└── run_bot.py           # Скрипт запуска бота
```

## Требования

- Python 3.8 или выше
- pip (менеджер пакетов Python)
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))

## Установка и настройка

### 1. Клонирование репозитория

```bash
git clone <repository-url>
cd Bastau
```

### 2. Создание виртуального окружения

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка переменных окружения

Создайте файл `.env` в корне проекта:

```env
# Telegram Bot Token (обязательно)
BOT_TOKEN=your_bot_token_here

# URL API backend (по умолчанию: http://127.0.0.1:8000/api)
API_BASE_URL=http://127.0.0.1:8000/api

# Telegram ID администратора (опционально)
ADMIN_TELEGRAM_ID=your_telegram_id
```

**Как получить BOT_TOKEN:**
1. Откройте Telegram и найдите [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в файл `.env`

**Как узнать свой Telegram ID:**
- Найдите бота [@userinfobot](https://t.me/userinfobot) в Telegram
- Отправьте команду `/start`
- Скопируйте ваш ID

### 5. Настройка Django (Backend)

#### 5.1. Переход в директорию Django проекта

```bash
cd med
```

#### 5.2. Применение миграций

```bash
python manage.py makemigrations
python manage.py migrate
```

#### 5.3. Создание суперпользователя (опционально, для доступа к админ-панели)

```bash
python manage.py createsuperuser
```

Следуйте инструкциям для создания администратора Django.

#### 5.4. Заполнение базы данных тестовыми данными (опционально)

```bash
python manage.py fill_db
```

Эта команда создаст:
- 8 категорий врачей
- 5 геопозиций (городов)
- 5 клиник
- 5 пациентов
- 8 врачей
- 14 отзывов
- 4 запроса в поддержку

#### 5.5. Возврат в корневую директорию

```bash
cd ..
```

## Запуск проекта

### Запуск Backend (Django API)

Откройте первый терминал:

```bash
cd med
python manage.py runserver
```

Backend будет доступен по адресу: `http://127.0.0.1:8000/`

**Проверка работы API:**
- API endpoints: `http://127.0.0.1:8000/api/`
- Админ-панель Django: `http://127.0.0.1:8000/admin/`

### Запуск Telegram бота

Откройте второй терминал (backend должен быть запущен):

```bash
# Из корневой директории проекта
python run_bot.py
```

Или альтернативный способ:

```bash
cd bot
python main.py
```

После успешного запуска вы увидите сообщение: `Bot started`

## Использование

### Telegram бот

1. Найдите вашего бота в Telegram по имени, которое вы указали при создании
2. Отправьте команду `/start`
3. Следуйте инструкциям бота для регистрации и использования

### API Endpoints

Backend предоставляет следующие API endpoints:

- `GET /api/categories/` - Список категорий
- `GET /api/geopositions/` - Список геопозиций
- `GET /api/clinics/` - Список клиник
- `GET /api/users/` - Список пользователей
- `GET /api/reviews/` - Список отзывов
- `GET /api/support-requests/` - Список запросов в поддержку

Подробную документацию API можно получить через Django REST Framework:
`http://127.0.0.1:8000/api/`

## Настройки

### Настройки бота

Файл `bot/config.py`:
- `BOT_TOKEN` - токен бота (из переменных окружения)
- `API_BASE_URL` - URL API backend
- `ADMIN_TELEGRAM_ID` - ID администратора
- `ITEMS_PER_PAGE` - количество элементов на странице (по умолчанию: 10)
- `REVIEW_COOLDOWN_HOURS` - время между отзывами для одного врача (по умолчанию: 24 часа)

### Настройки Django

Файл `med/med/settings.py`:
- `DEBUG = True` - режим отладки (для продакшена установите `False`)
- `ALLOWED_HOSTS` - список разрешенных хостов (для продакшена добавьте ваш домен)
- `SECRET_KEY` - секретный ключ Django (для продакшена используйте переменную окружения)
- `DATABASES` - настройки базы данных (по умолчанию SQLite)

## Разработка

### Структура бота

- **handlers/** - обработчики команд и сообщений
  - `start.py` - команда /start
  - `registration.py` - регистрация пользователей
  - `menu.py` - главное меню
  - `categories.py` - работа с категориями
  - `ratings.py` - просмотр рейтингов
  - `reviews.py` - отзывы
  - `support.py` - поддержка
  - `common.py` - общие обработчики

- **keyboards/** - клавиатуры
  - `inline.py` - inline клавиатуры
  - `reply.py` - reply клавиатуры

- **middlewares/** - middleware
  - `logging.py` - логирование запросов
  - `throttling.py` - ограничение частоты запросов

- **states/** - FSM состояния
  - `registration.py` - состояния регистрации
  - `review.py` - состояния создания отзыва
  - `support.py` - состояния запроса в поддержку

### Структура API

- **models.py** - модели данных (Category, GeoPosition, Clinic, User, Review, SupportRequest)
- **views.py** - API views (ViewSet для каждой модели)
- **serializers.py** - сериализаторы для API
- **urls.py** - маршрутизация API

## Устранение неполадок

### Бот не запускается

1. Проверьте, что `BOT_TOKEN` установлен в файле `.env`
2. Убедитесь, что backend запущен и доступен по адресу `API_BASE_URL`
3. Проверьте логи на наличие ошибок

### Ошибки миграций

```bash
cd med
python manage.py migrate --run-syncdb
```

### Ошибки подключения к API

1. Убедитесь, что backend запущен (`python manage.py runserver`)
2. Проверьте значение `API_BASE_URL` в `.env`
3. Проверьте настройки CORS в `med/med/settings.py`

### Очистка базы данных

```bash
cd med
python manage.py flush
python manage.py migrate
python manage.py fill_db
```

## Производственное развертывание

⚠️ **Важно:** Перед развертыванием в продакшене:

1. Установите `DEBUG = False` в `med/med/settings.py`
2. Настройте `ALLOWED_HOSTS` в `med/med/settings.py`
3. Используйте переменные окружения для секретных ключей
4. Настройте PostgreSQL или другую production БД вместо SQLite
5. Настройте правильные CORS настройки
6. Используйте веб-сервер (nginx + gunicorn/uwsgi) для Django
7. Настройте SSL/TLS сертификаты
8. Используйте систему управления процессами (systemd, supervisor) для бота

## Лицензия

См. файл [LICENSE](LICENSE)

## Поддержка

При возникновении проблем создайте issue в репозитории проекта.

