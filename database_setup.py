import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, TIMESTAMP, UniqueConstraint, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Users(Base):
	__tablename__ = 'users'
	id = Column(Integer, primary_key=True)
	username = Column(String(250))
	email  = Column(String, nullable = False)
	picture = Column(String)
	password = Column(String)
	academic = Column(Boolean)

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


class Item(Base):
	__tablename__ = 'items'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	description = Column(String(250))
	categorie_id = Column(Integer, ForeignKey('categories.id'))
	categorie = relationship(Categories)
	user_id = Column(Integer, ForeignKey('users.id'))
	user = relationship(Users)
	author = Column(String(250))
	pub_year = Column(Integer)
	ptype = Column(Integer)
	link = Column(String(250))
	hot_score = Column(Float)
	date = Column(Integer)

	@property
	def serialize(self):
		return {
			'name': self.name,
			'description': self.description,
			'categorie': self.categorie.name,
			'creator': self.user.username,
			'id': self.id,
		}

class Tags(Base):
	__tablename__ = 'tags'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)


class TagsItems(Base):
	__tablename__ = 'tagsitems'

	id = Column(Integer, primary_key=True)
	item_id = Column(Integer, ForeignKey('items.id'))
	item = relationship(Item)
	categorie_id = Column(Integer, ForeignKey('categories.id'))
	categorie = relationship(Categories)
	tags_id = Column(Integer, ForeignKey('tags.id'))
	tag = relationship(Tags)

class Upvotes(Base):
	__tablename__ = 'upvotes'

	id = Column(Integer, primary_key=True)
	item_id = Column(Integer, ForeignKey('items.id'))
	item = relationship(Item)
	user_id = Column(Integer, ForeignKey('users.id'))
	user = relationship(Users)

class Downvotes(Base):
	__tablename__ = 'downvotes'

	id = Column(Integer, primary_key=True)
	item_id = Column(Integer, ForeignKey('items.id'))
	item = relationship(Item)
	user_id = Column(Integer, ForeignKey('users.id'))
	user = relationship(Users)

class Comments(Base):
	__tablename__ = 'comments'

	id = Column(Integer, primary_key=True)
	content = Column(String(500), nullable=False)
	item_id = Column(Integer, ForeignKey('items.id'))
	item = relationship(Item)
	academic = Column(Boolean)
		
##

engine = create_engine('sqlite:///catalogdb.db')


Base.metadata.create_all(engine)