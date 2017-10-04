from aiohttp import web
from dbhelper import connect_db, redo_tables, create_todo_tables, close_db
from dbobjects import Todo, Tag
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from sqlalchemy import func
import aiohttp_cors


async def get_all_todos(request):
    session = request.app['dbsession']()
    if 'tag' in request.query:
        try:
            tag = session.query(Tag).filter_by(tag_id=request.query['tag']).one()
        except MultipleResultsFound:
            return web.json_response({'error': 'More then one Tag with the same id'}, status=500)
        except NoResultFound:
            return web.json_response({'error': 'Tag not found'}, status=404)

        rows = session.query(Todo).filter(Todo.tags.contains(tag))
    else:
        rows = session.query(Todo).all()

    todos = [row.toDict() for row in rows]
    return web.json_response(todos)


async def remove_all_todos(request):
    session = request.app['dbsession']()
    session.query(Todo).delete()
    session.commit()

    return web.Response(status=204)


async def get_one_todo(request):
    session = request.app['dbsession']()
    id = int(request.match_info['id'])

    try:
        row = session.query(Todo).filter_by(todo_id=id).one()
    except MultipleResultsFound:
        return web.json_response({'error': 'More then one Todo with the same id'}, status=500)
    except NoResultFound:
        return web.json_response({'error': 'Todo not found'}, status=404)

    return web.json_response(row.toDict())


async def create_todo(request):
    session = request.app['dbsession']()
    data = await request.json()

    if not 'title' in data:
        return web.json_response({'error': '"title" is a required field'})
    title = data['title']
    if not isinstance(title, str) or not len(title):
        return web.json_response({'error': '"title" must be a string with at least one character'})

    data['completed'] = bool(data.get('completed', False))
    order_nbr = int(data.get('display_order', session.query(func.max(Todo.display_order)).first()[0] + 1))
    todo = Todo(title=title, display_order=order_nbr, completed=data['completed'])

    data['url'] = str(request.url.join(request.app.router['one_todo'].url_for(id=todo.todo_id)))

    session.add(todo)
    session.commit()
    return web.Response(
        headers={'Location': data['url']},
        status=303
    )


async def update_todo(request):
    session = request.app['dbsession']()
    id = int(request.match_info['id'])

    try:
        row = session.query(Todo).filter_by(todo_id=id).one()
    except NoResultFound:
        return web.json_response({'error': 'Todo not found'}, status=404)

    data = await request.json()

    if 'title' in data:
        row.title = data['title']
    if 'order' in data:
        row.display_order = data['order']
    if 'completed' in data:
        row.completed = data['completed']

    session.commit()

    return web.json_response(row.toDict())


async def remove_todo(request):
    session = request.app['dbsession']()
    id = int(request.match_info['id'])

    try:
        row = session.query(Todo).filter_by(todo_id=id).one()
    except NoResultFound:
        return web.json_response({'error': 'Todo not found'}, status=404)

    session.delete(row)
    session.commit()

    return web.Response(status=204)


# new functionality
async def all_tags_of_todo(request):
    session = request.app['dbsession']()
    id = int(request.match_info['id'])

    try:
        row = session.query(Todo).filter_by(todo_id=id).one()
    except MultipleResultsFound:
        return web.json_response({'error': 'More then one Tag with the same id'}, status=500)
    except NoResultFound:
        return web.json_response({'error': 'Tag not found'}, status=404)

    return web.json_response(row.toDict())


async def add_tag_to_todo(request):
    session = request.app['dbsession']()
    data = await request.json()
    id = int(request.match_info['id'])

    try:
        row = session.query(Todo).filter_by(todo_id=id).one()
    except MultipleResultsFound:
        return web.json_response({'error': 'More then one Todo with the same id'}, status=500)
    except NoResultFound:
        return web.json_response({'error': 'Todo not found'}, status=404)

    try:
        tag = session.query(Tag).filter_by(tag_id=data['id']).one()
    except MultipleResultsFound:
        return web.json_response({'error': 'More then one Tag with the same id'}, status=500)
    except NoResultFound:
        return web.json_response({'error': 'Tag not found'}, status=404)

    row.tags.append(tag)
    session.commit()

    return web.json_response(row.toDict())


async def delete_tag_to_todo(request):
    session = request.app['dbsession']()
    todo_id = int(request.match_info['todo_id'])
    tag_id = int(request.match_info['tag_id'])

    try:
        row = session.query(Todo).filter_by(todo_id=todo_id).one()
    except MultipleResultsFound:
        return web.json_response({'error': 'More then one Todo with the same id'}, status=500)
    except NoResultFound:
        return web.json_response({'error': 'Todo not found'}, status=404)

    try:
        tag = session.query(Tag).filter_by(tag_id=tag_id).one()
    except MultipleResultsFound:
        return web.json_response({'error': 'More then one Tag with the same id'}, status=500)
    except NoResultFound:
        return web.json_response({'error': 'Tag not found'}, status=404)

    row.tags.remove(tag)
    session.commit()

    return web.Response(status=200)


# tags section
async def get_all_tags(request):
    session = request.app['dbsession']()
    rows = session.query(Tag).all()
    tags = [row.toDict() for row in rows]
    return web.json_response(tags)


async def create_tag(request):
    session = request.app['dbsession']()
    data = await request.json()

    if not 'name' in data:
        return web.json_response({'error': '"name" is a required field'})
    name = data['name']
    if not isinstance(name, str) or not len(name):
        return web.json_response({'error': '"name" must be a string with at least one character'})

    tag = Tag(name=name)

    data['url'] = str(request.url.join(request.app.router['one_todo'].url_for(id=tag.tag_id)))

    session.add(tag)
    session.commit()
    return web.Response(
        headers={'Location': data['url']},
        status=303
    )


def get_one_tag(request):
    session = request.app['dbsession']()
    id = int(request.match_info['id'])

    try:
        row = session.query(Tag).filter_by(tag_id=id).one()
    except MultipleResultsFound:
        return web.json_response({'error': 'More then one Tag with the same id'}, status=500)
    except NoResultFound:
        return web.json_response({'error': 'Tag not found'}, status=404)

    return web.json_response(row.toDict())


async def update_one_tag(request):
    session = request.app['dbsession']()
    id = int(request.match_info['id'])

    try:
        row = session.query(Tag).filter_by(tag_id=id).one()
    except NoResultFound:
        return web.json_response({'error': 'Tag not found'}, status=404)

    data = await request.json()

    if not 'name' in data:
        return web.json_response({'error': '"name" is a required field'})
    name = data['name']
    if not isinstance(name, str) or not len(name):
        return web.json_response({'error': '"name" must be a string with at least one character'})

    row.name = data['name']

    session.commit()

    return web.json_response(row.toDict())


def delete_one_tag(request):
    session = request.app['dbsession']()
    id = int(request.match_info['id'])

    try:
        row = session.query(Tag).filter_by(tag_id=id).one()
    except NoResultFound:
        return web.json_response({'error': 'Tag not found'}, status=404)

    session.delete(row)
    session.commit()

    return web.Response(status=204)


def app_factory(args=()):
    app = web.Application()

    # Configure default CORS settings.
    cors = aiohttp_cors.setup(app, defaults={
        "*": aiohttp_cors.ResourceOptions(
            allow_credentials=True,
            expose_headers="*",
            allow_headers="*",
        )
    })

    app.on_startup.append(connect_db)

    if '--tables-create' in args:
        app.on_startup.append(create_todo_tables)
    if '--tables-redo' in args:
        app.on_startup.append(redo_tables)

    app.on_shutdown.append(close_db)

    cors.add(app.router.add_get('/todos/', get_all_todos, name='all_todos'))
    cors.add(app.router.add_delete('/todos/', remove_all_todos, name='remove_todos'))
    cors.add(app.router.add_post('/todos/', create_todo, name='create_todo'))
    cors.add(app.router.add_get('/todos/{id:\d+}', get_one_todo, name='one_todo'))
    cors.add(app.router.add_patch('/todos/{id:\d+}', update_todo, name='update_todo'))
    cors.add(app.router.add_delete('/todos/{id:\d+}', remove_todo, name='remove_todo'))

    # new functionality
    cors.add(app.router.add_get('/todos/{id:\d+}/tags/', all_tags_of_todo, name='todo_tags'))
    cors.add(app.router.add_post('/todos/{id:\d+}/tags/', add_tag_to_todo, name='add_tag_todo'))
    cors.add(app.router.add_delete('/todos/{todo_id:\d+}/tags/{tag_id:\d+}', delete_tag_to_todo, name='delete_tag_todo'))

    # tags
    cors.add(app.router.add_get('/tags/', get_all_tags, name='all_tags'))
    cors.add(app.router.add_post('/tags/', create_tag, name='create_tag'))
    cors.add(app.router.add_get('/tags/{id:\d+}', get_one_tag, name='get_one_tag'))
    cors.add(app.router.add_patch('/tags/{id:\d+}', update_one_tag, name='update_one_tag'))
    cors.add(app.router.add_delete('/tags/{id:\d+}', delete_one_tag, name='delete_one_tag'))

    return app
