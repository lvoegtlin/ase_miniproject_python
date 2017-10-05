from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from dbobjects import Todo, Tag, Base, todo_tag_connection
from sqlalchemy.orm import sessionmaker


async def connect_db(app):
    app['db'] = create_engine("sqlite:///todo.db")
    app['dbsession'] = sessionmaker(bind=app['db'])


def close_db(app):
    app['dbsession'].close_all()
    app['dbsession'] = None


def initial_values(app):
    session = app['dbsession']()
    session.add_all([
        Todo(title="build an API", display_order=1, completed=0),
        Todo(title="?????", display_order=2, completed=0),
        Todo(title="profit!", display_order=3, completed=0),
        Tag(name="Work"),
        Tag(name="Private"),
        Tag(name="Miscellaneous"),
        Tag(name="Advanced Software Engineering")
    ])
    session.commit()


def create_tables(engine):
    Base.metadata.create_all(engine)


def drop_tables(engine):
    Base.metadata.drop_all(engine)


def redo_tables(app):
    drop_tables(app['db'])
    create_todo_tables(app)


async def create_todo_tables(app):
    create_tables(app['db'])
    initial_values(app)
