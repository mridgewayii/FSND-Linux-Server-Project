import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, User, Category, Item

engine = create_engine('postgresql://catalog:catalog@localhost/catalog')


Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

# Build some initial users.  These might be administrators in a real project
default_user1 = User(name='Movie Expert',
                     email='xpert@something.com',
                     picture='https://upload.wikimedia.org/wikipedia/en/8/8d/My_Gamer_pic.png')
session.add(default_user1)
default_user2 = User(name='Movie Queen',
                     email='queen@something.com',
                     picture='https://en.wikipedia.org/wiki/File:Queen_Elizabeth_II_in_March_2015.jpg')
session.add(default_user2)
session.commit()

# Create the categories of movies to be seen.
category1 = Category(name="Drama")
session.add(category1)
session.commit()
category2 = Category(name="SciFi")
session.add(category2)
session.commit()
category3 = Category(name="Action")
session.add(category3)
session.commit()
category4 = Category(name="Mystery")
session.add(category4)
session.commit()
category5 = Category(name="Romance")
session.add(category5)
session.commit()
category6 = Category(name="Documentary")
session.add(category6)
session.commit()
category7 = Category(name="Suspense")
session.add(category7)
session.commit()

# Add a few movies and the information for these movies into the database
item_1 = Item(name="Home Again",
              description="Set in Los Angeles, this romantic comedy follows "
                          "a recently divorced single mother as she defies "
                          "common sense and takes in three young male "
                          "boarders -- who become part of her unconventional "
                          "family.",
              stars="Reese Witherspoon",
              created_at=datetime.datetime.now(),
              updated_at=datetime.datetime.now(),
              category=category1,
              user=default_user2)
session.add(item_1)

item_2 = Item(name="The Mummy",
              description="A tale that never gets old is transported to "
                          "modern times when an ancient princess whose "
                          "destiny was stolen from her millennia ago awakens "
                          "from her tomb eager to take revenge -- unleashing "
                          "a torrent of terror in London's underground "
                          "labyrinths.",
              stars="Tom Cruise",
              created_at=datetime.datetime.now(),
              updated_at=datetime.datetime.now(),
              category=category2,
              user=default_user1)
session.add(item_2)

item_3 = Item(name="Predator",
              description="Two real-life governors -- Arnold Schwarzenegger "
                          "(Dutch) and Jesse Ventura (Sgt. Blain) -- use their"
                          " muscled intellects to pursue a force more sinister"
                          " than state budget crises: an otherworldly creature"
                          " deep in the jungle. Adept at slaughtering well-"
                          "trained fighters, the beast is practically "
                          "invisible. Special effects, dizzying camera work "
                          "and a sci-fi bent elevate John McTiernan's gory "
                          "horror-actioner, which spawned several sequels.",
              stars="Arnold Schwarzenegger",
              created_at=datetime.datetime.now(),
              updated_at=datetime.datetime.now(),
              category=category3,
              user=default_user1)
session.add(item_3)

item_4 = Item(name="Riddick",
              description="In this extraterrestrial sequel to The Chronicles "
                          "of Riddick, Vin Diesel returns as the grim "
                          "antihero, who finds himself marooned on a lonely "
                          "planet. Hoping an emergency beacon will save him, "
                          "Riddick instead attracts deadly aliens and "
                          "mercenaries.",
              stars="Vin Diesel",
              created_at=datetime.datetime.now(),
              updated_at=datetime.datetime.now(),
              category=category2,
              user=default_user1)
session.add(item_4)

item_5 = Item(name="The Wall",
              description="A crumbling concrete wall is all that stands "
                          "between an American sharpshooter and the Iraqi "
                          "sniper intent on killing him and his spotter. As"
                          " the enemies converse over their radios, they know "
                          "just one thing: Not all of them will come out "
                          "alive.",
              stars="Aaron Taylor-Johnson",
              created_at=datetime.datetime.now(),
              updated_at=datetime.datetime.now(),
              category=category3,
              user=default_user2)
session.add(item_5)

item_6 = Item(name="World War Z",
              description="A U.N. employee races against time and fate as he "
                          "travels the world trying to stop the spread of a "
                          "deadly zombie pandemic. As the undead hordes gain "
                          "strength across the globe, governments topple and "
                          "Earth stands on the brink of total social "
                          "collapse.",
              stars="Brad Pitt",
              created_at=datetime.datetime.now(),
              updated_at=datetime.datetime.now(),
              category=category7,
              user=default_user2)
session.add(item_6)

item_7 = Item(name="Patriots Day",
              description="A tragic bombing near the finish line at the 2013 "
                          "Boston Marathon sets off a citywide manhunt for "
                          "the perpetrators. With residents devastated by the"
                          " events, Sgt. Tommy Saunders and the Boston Police"
                          " Department zero in on two suspects.",
              stars="Mark Wahlberg",
              created_at=datetime.datetime.now(),
              updated_at=datetime.datetime.now(),
              category=category4,
              user=default_user1)
session.add(item_7)

item_8 = Item(name="Me Before You",
              description="Planning to stay just six months, Lou Clark takes "
                          "on the job of looking after rich but depressed "
                          "Will Traynor, who's been left a quadriplegic by an"
                          " accident. Despite Will's disillusionment, Lou is "
                          "determined to show him that his life is worth "
                          "living.",
              stars="Emilia Clarke",
              created_at=datetime.datetime.now(),
              updated_at=datetime.datetime.now(),
              category=category5,
              user=default_user2)
session.add(item_8)


item_9 = Item(name="History of the Eagles",
              description="This sweeping documentary chronicles the evolution"
                          " and influence of rock legends The Eagles. Stories"
                          " from band members and music industry insiders "
                          "paint a vivid picture of one of America's most "
                          "successful bands.",
              stars="Glenn Frey",
              created_at=datetime.datetime.now(),
              updated_at=datetime.datetime.now(),
              category=category6,
              user=default_user2)
session.add(item_9)


item_10 = Item(name="End of Watch",
               description="Officers Taylor and Zavala patrol the streets of "
                           "South Central Los Angeles, an area of the city "
                           "ruled by gangs and riddled with drug violence. "
                           "Their perilous beat is captured on security "
                           "footage and with the HD cameras of cops, "
                           "criminals and victims.",
               stars="Jake Gyllenhaal",
               created_at=datetime.datetime.now(),
               updated_at=datetime.datetime.now(),
               category=category7,
               user=default_user2)
session.add(item_10)

session.commit()

print "Added Database Items"
