from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models.database import Base


FILES_PATH = "database/files"

engine = create_engine("sqlite:///database/database.sqlite")

Session = sessionmaker(bind=engine)

Session.expire_on_commit = False

Base.metadata.create_all(engine)
