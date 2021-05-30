# Telegram-Channel-Parser
Парсинг текстовых сообщений любого канала с помощью библиотеки Telethon. 
Необходимо быть подписанным на канал, а также иметь заранее созданный и загруженный в Google Drive файл сессии Telegram.
В sqlite базу сохраняется ID сообщения, исходный текст сообщения, все entities текста и html версия текста на основе 
entities. База хранится и синхронизируется с Google Drive.

Запрос на создание базы данных для сохранения логов:
```

CREATE TABLE IF NOT EXISTS logs (id INTEGER DEFAULT 0 UNIQUE, raw_text TEXT, entities BLOB, text TEXT)

```

## Change Log

`30.05.2021` - Initial commit.