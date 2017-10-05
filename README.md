# todobackend-aiohttp

Yet another [todo backend](http://todobackend.com) written in Python 3.5 with aiohttp. Original code [from alec.thoughts import \*](http://justanr.github.io/getting-start-with-aiohttpweb-a-todo-tutorial).

## Usage

Normal start up:
```
python3 -m aiohttp.web -P 8080 aiotodo:app_factory
```

Start up with table creation. You can also use the --tables-create addition if you want to have a fresh database with the inital values.
```
python3 -m aiohttp.web -P 8080 --tables-create aiotodo:app_factory
```

## Tests

You can run validate the application with http://www.todobackend.com/specs/.
