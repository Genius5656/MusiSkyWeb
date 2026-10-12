##Миграция alembic
###Работа с консолью
```bash
cd app
alembic init -t async migration
```
заменить в alembic.ini и переместить в app
```python
script_location = migration
```
на
```python
script_location = app/migration
```
###Работа с файлом
В app/migration/emv.py заменить
```python
import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context


config = context.config


if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = None
```
на
```python
import sys
from os.path import dirname, abspath

sys.path.insert(0, dirname(dirname(abspath(__file__))))

import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from app.database import Base, database_url
from app.users.models import User
from app.chat.models import Message


config = context.config
config.set_main_option("sqlalchemy.url", database_url)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

    
target_metadata = Base.metadata
```

###Коммит и применение изменений
```bash
cd ../
alembic revision --autogenerate -m "Initial revision"
alembic upgrade head
```

###Запуск
```bash
uvicorn app.main:app --reload
```

