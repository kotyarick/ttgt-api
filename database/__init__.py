from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.database import Base

engine = create_engine("sqlite:///database.sqlite")

Session = sessionmaker(bind=engine)

Session.expire_on_commit = False

Base.metadata.create_all(engine)
