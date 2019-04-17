from sqlalchemy import Column,Integer,String, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
from passlib.apps import custom_app_context as pwd_context
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(250))
    provider = Column(String(250))
    email = Column(String(250))
    image = Column(String(250))


class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    @property
    def serialize(self):
        return {
            'id' : self.id,
            'name' : self.name
        }

class Item(Base):
    __tablename__ = 'item'
    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    description = Column(String(250))
    date_created = Column(DateTime, default=datetime.datetime.utcnow)
    user_id = Column(Integer, ForeignKey('user.id'))
    category_id = Column(Integer, ForeignKey('category.id'))
    user = relationship(User)
    category = relationship(Category)
    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id' : self.id,
            'name' : self.name,
            'description' : self.description,
            'category_id' : self.category_id
            }

engine = create_engine('sqlite:///catalog.db')
 

Base.metadata.create_all(engine)

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

session.add_all([
    Category(name='Soccer'),
    Category(name='Basketball'),
    Category(name='Baseball'),
    Category(name='Frisbee'),
    Category(name='Snowboarding'),
    Category(name='Rock Climbing'),
    Category(name='Foosball'),
    Category(name='Skating'),
    Category(name='Hockey')
])
session.commit()