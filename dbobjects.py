from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship

global Base
Base = declarative_base()

todo_tag_connection = Table("todo_tag_connection", Base.metadata,
    Column('todo_id', Integer, ForeignKey('todos.todo_id')),
    Column('tag_id', Integer, ForeignKey('tags.tag_id'))

)

class Todo(Base):
    __tablename__ = 'todos'

    todo_id = Column(Integer, primary_key=True)
    title = Column(String)
    display_order = Column(Integer)
    completed = Column(Boolean)
    tags = relationship("Tag",
                        secondary=todo_tag_connection,
                        backref="todos")

    def toDict(self):
        return {"title": self.title,
                "order": self.display_order,
                "completed": self.completed,
                "tags": [tag.tag_id for tag in self.tags]}



class Tag(Base):
    __tablename__ = 'tags'

    tag_id = Column(Integer, primary_key=True)
    name = Column(String)

    def toDict(self):
        return {'id': self.tag_id, 'name': self.name}