# FastAPI Messenger — серверная часть мессенджера

## Цель проекта

Учебный проект, демонстрирующий создание безопасного REST API на FastAPI с регистрацией,
аутентификацией по JWT (RS256), refresh-токенами, работой с PostgreSQL.

---

## Структура проекта

```text
messenger-backend/
├── main.py                 # Точка входа FastAPI, CORS
├── router.py               # Роуты /login, /register, /check_token
├── config.py               # Настройки через pydantic-settings (БД, JWT)
├── dependencies.py         # Pydantic-схемы (UserSchema, Access_Token)
├── jwt_utils.py            # Утилиты работы с JWT (RS256), refresh
├── orm_utils.py            # SQLAlchemy сессия, CRUD, создание таблиц
├── model_table.py          # Декларативная база, модель Users
├── model_T.py              # Модель Workers (задел для чатов)
├── user_models.py          # Альтернативные Pydantic-схемы (дубликат)
├── password_utils.py       # Хеширование и проверка паролей (bcrypt)
├── certs/                  # Ключи для RS256
│   ├── jwt-private.pem
│   └── jwt-public.pem
├── .env                    # Переменные окружения (не включён в репозиторий)
├── requirements.txt        # Зависимости Python
└── README.md
```

---

## Запуск проекта

### 1. Клонируйте репозиторий и перейдите в папку
```bash
git clone https://github.com/ngrave1/messenger_min.git
cd messenger-backend
```

### 2. Установите зависимости

```bash
pip install -r requirements.txt
```

Основные зависимости: `fastapi`, `uvicorn`, `sqlalchemy`, `asyncpg`, `pydantic-settings`, `pyjwt`, `bcrypt`, `passlib`.

### 3. Настройте переменные окружения

Создайте файл `.env` в корне проекта:

```ini
db_host=localhost
db_port=5432
db_user=postgres
db_password=yourpassword
db_name=messenger
```

### 4. Сгенерируйте RSA-ключи для JWT

```bash
mkdir -p certs
openssl genrsa -out certs/jwt-private.pem 2048
openssl rsa -in certs/jwt-private.pem -pubout -out certs/jwt-public.pem
```

### 5. Запустите PostgreSQL

Убедитесь, что сервер PostgreSQL запущен и база данных создана.

### 6. Инициализируйте таблицы

При первом запуске приложение можно настроить на создание таблиц автоматически (см. `create_tables()` в `orm_utils.py`).

### 7. Запустите сервер

```bash
uvicorn main:app --reload --port 8000
```

Приложение будет доступно по адресу `http://127.0.0.1:8000`.

---

## Ключевые реализованные фичи

### 1. Централизованная конфигурация
- `config.py` использует `pydantic-settings` для загрузки настроек из `.env`.
- Настройки разделены на вложенные модели: `DatabaseSettings` и `AuthJWT`.
- Префиксы переменных окружения (`db_*`) обеспечивают чистоту конфигурации.
- Поддерживаются свойства для формирования строк подключения (asyncpg / psycopg2).

### 2. JWT-аутентификация (RS256)
- Асимметричные ключи (`private.pem` / `public.pem`) для подписи и проверки токенов.
- Два типа токенов:
  - `access_token` (короткоживущий, 15 минут)
  - `refresh_token` (долгоживущий, 30 дней)
- Refresh-токен хранится в cookie и автоматически используется для выпуска нового access-токена через эндпоинт `/check_token/`.
- Токены передаются в httpOnly cookie, что снижает риск XSS.

### 3. Хеширование паролей
- Пароли хранятся в БД в виде bcrypt-хеша (через `password_utils.py`).
- Проверка пароля при логине не выдаёт дополнительной информации – только 401/403.

### 4. Работа с базой данных
- SQLAlchemy Core + сессии (`sessionmaker`).
- Модель `Users`  хранит email и хеш пароля.
- Модель `Workers` для функционала контактов/чатов.
- Утилиты CRUD: `get_user_by_email`, `get_user_by_id`, `add_user`, `create_user`.

### 5. Безопасность и удобство
- CORS настроен только для доверенного источника (`http://localhost:3000`).
- Проверка токена в фоне: если access-токен истёк, но refresh-токен валиден, клиент получает новый access-токен без перелогина.
- Все ошибки аутентификации возвращают обобщённое `"invalid token"` или `"Token release failed"`.

---

## Примеры использования API

### Регистрация нового пользователя

```bash
curl -X POST http://localhost:8000/register/ \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "secret"}'
```

Ответ:

```json
{"return": "user added, id alice@example.com"}
```

### Логин (получение токенов)

```bash
curl -X POST http://localhost:8000/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "alice@example.com", "password": "secret"}'
```

Ответ (токены также будут записаны в cookie):

```json
{
  "refresh_token": "eyJ...",
  "access_token": "eyJ...",
  "token_type": "Bearer"
}
```

### Проверка токена (автообновление)

```bash
curl -X PATCH http://localhost:8000/check_token/ \
  --cookie "access_token=<access>; refresh_token=<refresh>"
```

При валидном access-токене:

```json
{"result": true}
```

При истёкшем access, но валидном refresh:

```json
{"access_token": "new_token..."}
```

И новый access-токен обновляется в cookie автоматически.

---

## Лицензия

MIT — проект учебный. Файл `.env` с реальными паролями должен быть добавлен в `.gitignore`. Ключи `certs/` так же не должны попадать в репозиторий.
