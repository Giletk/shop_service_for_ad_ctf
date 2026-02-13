# Shop Platform

Веб-сервис магазина с логической уязвимостью для A/D CTF.

## Описание

Платформа для продажи товаров, где пользователи могут:
- Регистрироваться и входить в систему
- Покупать товары
- Читать секреты после покупки товаров

## Структура

```
my_service/
├── service/
│   ├── .env
│   ├── docker-compose.yml
│   ├── Dockerfile
│   └── app/
│       ├── static/
│           ├── images/
│           ├── style.css
│       ├── templates/
│       ├── app.py
│       └── requirements.txt
├── checker/
│   ├── .env
│   ├── checker.py
│   └── requirements.txt
└── sploit/
    ├── .env
    ├── sploit.py
    └── requirements.txt
```

## Запуск
Перед запуском необходимо указать порт, по которому сервис будет доступен из игровой сети (заодно изменим порты для `checker` и `sploit`)
```bash
echo 'PORT=12345' > ./service/.env
echo 'PORT=12345' > ./checker/.env
echo 'PORT=12345' > ./sploit/.env
```


```bash
cd service
docker-compose up --build
```

Сервис будет доступен на `http://localhost:PORT`

## Проверка

```bash
pip install -r checker/requirements.txt
cd checker
python checker.py check localhost
python checker.py put localhost flag_id FLAG{test}
python checker.py get localhost flag_id FLAG{test}
```
`flag_id` я не использовал, оставил для совместимости.
## Эксплоит

```bash
pip install -r sploit/requirements.txt
cd sploit
python sploit.py localhost 5000
```

## Уязвимость



## Исправление уязвимости

Добавить валидацию цены в `app.py`:

```python
if price < 0:
    return render_template_string(ADD_ITEM_PAGE, error="Price must be positive!")
```
