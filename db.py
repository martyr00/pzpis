import os
from sqlalchemy import (
    create_engine, Column, Integer, String, Date, Boolean, ForeignKey, TIMESTAMP
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_HOST = os.getenv("PG_HOST", "localhost")
DB_PORT = os.getenv("PG_PORT", "6969")
DB_USER = os.getenv("PG_USER", "martyr")
DB_PASS = os.getenv("PG_PASSWORD", "123321")
DB_NAME = os.getenv("PG_DATABASE", "postgres")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASS}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# ORM-модели
class Artist(Base):
    __tablename__ = "artist"
    id         = Column(Integer, primary_key=True)
    nickname   = Column(String(100))
    real_name  = Column(String(255))
    country    = Column(String(100))
    debut_year = Column(Integer)

class Album(Base):
    __tablename__ = "album"
    id           = Column(Integer, primary_key=True)
    title        = Column(String(255))
    release_date = Column(Date)
    artist_id    = Column(Integer, ForeignKey("artist.id"))
    genre        = Column(String(100))
    label        = Column(String(255))

class Track(Base):
    __tablename__ = "track"
    id       = Column(Integer, primary_key=True)
    title    = Column(String(255))
    duration = Column(Integer)
    album_id = Column(Integer, ForeignKey("album.id"))

class User(Base):
    __tablename__ = "users"
    id                = Column(Integer, primary_key=True)
    username          = Column(String(100))
    email             = Column(String(255))
    registration_date = Column(Date)

class Playlist(Base):
    __tablename__ = "playlist"
    id         = Column(Integer, primary_key=True)
    name       = Column(String(255))
    user_id    = Column(Integer, ForeignKey("users.id"))
    created_at = Column(TIMESTAMP)

class PlaylistTrack(Base):
    __tablename__ = "playlist_track"
    playlist_id = Column(Integer, ForeignKey("playlist.id"), primary_key=True)
    track_id    = Column(Integer, ForeignKey("track.id"), primary_key=True)
    added_at    = Column(TIMESTAMP)

class TrackArtist(Base):
    __tablename__ = "track_artist"
    track_id   = Column(Integer, ForeignKey("track.id"), primary_key=True)
    artist_id  = Column(Integer, ForeignKey("artist.id"), primary_key=True)
    is_primary = Column(Boolean)
