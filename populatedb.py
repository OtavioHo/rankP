from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Categories, Base, Item

engine = create_engine('sqlite:///catalogdb.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()


# Menu for UrbanBurger
categorie1 = Categories(name="First Categorie")
session.add(categorie1)

item1 = Item(name="Item 1", description = "this is the first item", categorie_id = 1)
item2 = Item(name="Item 2", description = "this is the second item", categorie_id = 1)
item3 = Item(name="Item 3", description = "this is the third item", categorie_id = 1)

session.add(item1)
session.add(item2)
session.add(item3)
session.commit()
