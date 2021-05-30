import os
import re
import asyncio
import objects
import heroku3
from SQL import SQL
from datetime import datetime
from telethon.sync import TelegramClient
# =================================================================================================================
stamp1 = objects.time_now()
Auth = objects.AuthCentre(ID_DEV=-1001312302092, TOKEN=os.environ['TOKEN'])


def start():
    d_client = None
    objects.environmental_files()
    session_file = f"{os.environ['username']}.session"
    if os.environ.get('local') is None:
        d_client = objects.GoogleDrive('google.json')
        d_client.download_file(os.environ['db_file_id'], 'logs.db')
        for file in d_client.files():
            if file['name'] == session_file:
                d_client.download_file(file['id'], session_file)
                Auth.dev.printer(f'Загружен {session_file}')
    return d_client


drive_client = start()
channel_id = int(os.environ['channel_id'])
message_id = int(os.environ['message_id'])
max_message_id = int(os.environ['max_message_id'])
telethon_merge_entities = {
    'MessageEntityCode': 'code',
    'MessageEntityBold': 'bold',
    'MessageEntityItalic': 'italic',
    'MessageEntityMention': 'mention',
    'MessageEntityTextUrl': 'text_link',
    'MessageEntityUnderline': 'underline',
    'MessageEntityStrike': 'strikethrough',
    'MessageEntityMentionName': 'text_mention'}
client = TelegramClient(os.environ['username'], int(os.environ['api_id']), os.environ['api_hash']).start()
# =================================================================================================================
db = SQL('logs.db')
if os.environ.get('local') is None:
    Auth.dev.start(stamp1)


def replace(_text):
    if 'https://t.me/MediaDump/' in _text:
        _text = re.sub('https://t.me/MediaDump/', 'https://t.me/c/1273330143/', _text)
    if 'https://t.me/devforward/' in _text:
        _text = re.sub('https://t.me/devforward/', 'https://t.me/c/1252666919/', _text)
    return _text


async def main():
    global message_id
    while True:
        try:
            ending = message_id + 300 if message_id + 300 <= max_message_id else max_message_id
            messages = await client.get_messages(channel_id, ids=list(range(message_id, ending)))
            stamp = datetime.now().timestamp()
            for message in messages:
                if message:
                    raw_entities = []
                    raw_text = message.message
                    if message.entities:
                        for entity in message.entities:
                            entity = entity.to_dict()
                            if entity.get('_'):
                                entity['type'] = telethon_merge_entities.get(entity.get('_'))
                                entity['tele-type'] = entity.get('_')
                                del entity['_']
                                if entity['type'] == 'text_mention':
                                    entity['user'] = {'id': entity['user_id']}
                            raw_entities.append(entity)
                    text = objects.iter_entities(raw_text, raw_entities)
                    update = {
                        'text': re.sub('\'', '"', replace(text)) if text else None,
                        'raw_text': re.sub('\'', '"', replace(raw_text)) if raw_text else None,
                        'entities': re.sub('\'', '"', replace(str(raw_entities))) if raw_entities else None}
                    db.update('logs', message.id, update)
            if drive_client:
                description = f'Last range: {message_id, ending-1}\nmax_message_id: {max_message_id}'
                drive_client.update_file(os.environ['db_file_id'], 'logs.db', description)
            delay = datetime.now().timestamp() - stamp
            Auth.dev.printer(f'Пройден {range(message_id, ending-1)} за {delay} сек.')
            await asyncio.sleep(61 - delay)
            if message_id % 300000 == 0:
                config = {'message_id': message_id-600}
                connection = heroku3.from_key(os.environ['api'])
                for app in connection.apps():
                    app.update_config(config)
                await asyncio.sleep(200)
            message_id += 300
        except IndexError and Exception:
            await Auth.dev.async_except()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
