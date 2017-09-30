# todobackend-aiohttp

Yet another [todo backend](http://todobackend.com) written in Python 3.5 with aiohttp. Original code [from alec.thoughts import \*](http://justanr.github.io/getting-start-with-aiohttpweb-a-todo-tutorial).

## Usage

Normal start up:
```
python3 -m aiohttp.web -P 8080 aiotodo:app_factory
```

Start up with table creation (When starting the application for the first time)
```
python3 -m aiohttp.web -P 8080 --tables-create aiotodo:app_factory
```

Start up and redo the tables (drops them an then recreates them)
```
python3 -m aiohttp.web -P 8080 --tables-redo aiotodo:app_factory
```

## Tests

You can run validate the application with http://www.todobackend.com/specs/.
