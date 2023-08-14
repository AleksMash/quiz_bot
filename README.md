# Описание проекта  
  
Настоящий проект сделан в процессе изучения Телеграм-ботов и ботов Вконтакте на курсе [devman](https://devman.org). Выполнено два бота (для Telegram и ВК соответственно), реализующие интерактивную игру-викторину в виде случайно задаваемых вопросов и ответов на них. Работающий пример можно протестировать в  [Telegram](https://t.me/MashukovBot) и группе  [ВКонтакте](https://vk.com/club218862065).  
  
# Установка  
  
Python должен быть предварительно установлен.  Скачайте исходный код из репозитария, создайте виртуальное окружение и установите необходимые зависимости.   
  
`pip install -r requirements.txt`  
  
# Настройка  
  
В корневом каталоге проекта создайте файл .env следующего содержания:  
  
  
```bash  
TG_BOT_TOKEN=<токен вашего Telegram-бота>
REDIS_HOST=<URL базы данных Redis>
REDIS_PORT=<порт базы данных Redis>
REDIS_PASSWORD=<пароль для доступка к базе данных Redis>
VK_GROUP_TOKEN=<токен для доступа к API к вашей группы в ВК>
QA_FILE=<путь к json файлу с вопросами и ответами>  
```  
  
json файл с вопросами и ответами должен быть сформирован  по следующему образцу:  
  
```json  
{    
    "question_1": {    
        "q": "Вопрос 1",    
        "a": "Ответ на вопрос 1"    
    },    
    "question_2": {    
        "q": "Вопрос 2",    
        "a": "Ответ на вопрос 2"    
    },    
    "question_N": {    
        "q": "Вопрос N",    
        "a": "Ответ на вопрос N"    
    },  
}  
```  

Вы можете подготовить такой файл путем автоматического парсинга текстовых файлов из каталога `raw_data`. Для парсинга используете скрипт `prepare_questions.py`. 
Запускается командой:

```python
python tg_bot.py [-d] <путь к каталогу с файлами *.txt (по умолчанию "raw_data/")> -c <число *.txt файлов случайным образом выбираемых дл парсинга>
```

Текстовый файл, подлежащий рарсингу должен быть сформирован из блоков вопрос - ответ по следующей схеме:

```text
Врпрос[любые символы]
Содержание вопроса

Ответ[любыесимволы]
Содержание ответа
```

т. е. слово "Вопрос" с последющими любыми символами, далее перенос строки и текст вопроса. После - двоной перенос строки и ключевое слово "Ответ", которое также может сопровождаться последущими любыми символами, после чего перенос строки и затем - текст ответа.
# Запуск ботов
  
Для запуса Telegram бота выполните команду:  
  
```python  
python tg_bot.py  
```  
  
Для запуска бота в контакте:   
  
```python  
python vk_bot.py  
```  
  
# Взаимодействие с ботом  
  
Для запуска Telegram-бота напишите команду `/start`. В диалоге с ботом Вконтакте напишите любое сообщение. В ответ на эти действия бот предложит интуитивно понятное кнопочное меню.   
  
Для сравнения ответа на заданный вопрос с ответом из БД используется библиотека `fuzzywuzzy`, реализующая алгоритм нечеткого сравнения строк.