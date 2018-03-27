from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


# Establish a user table
class User(Base):

    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


# Establish a category table
class Category(Base):

    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'id': self.id,
            'name': self.name
        }


# Establish a item table
class Item(Base):

    __tablename__ = 'item'

    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    description = Column(String(550))
    stars = Column(String(120), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    updated_at = Column(TIMESTAMP)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship(User)

# Establish a serialization of the data for JSON
    @property
    def serialize(self):
        # Returns object data in easily serializeable format
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category_id
        }


# Create the database
engine = create_engine('postgresql://catalog:catalog@localhost/catalog')
Base.metadata.create_all(engine)
