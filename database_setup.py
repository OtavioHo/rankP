import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, TIMESTAMP, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

##
class Categories(Base):
	__tablename__ = 'categories'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False, unique=True)

	@property
	def serialize(self):
		return{
			'name': self.name,
			'id': self.id,
		}

class Users(Base):
	__tablename__ = 'users'
	username = Column(String(250))
	email  = Column(String, nullable = False, primary_key = True)
	picture = Column(String)


class Item(Base):
	__tablename__ = 'items'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	description = Column(String(250))
	img = Column(String(250))
	categorie_id = Column(Integer, ForeignKey('categories.id'))
	categorie = relationship(Categories)
	user_email = Column(String, ForeignKey('users.email'))
	user = relationship(Users)

	@property
	def serialize(self):
		return {
			'name': self.name,
			'description': self.description,
			'id': self.id,
		}

##

engine = create_engine('sqlite:///catalogdb.db')


Base.metadata.create_all(engine)