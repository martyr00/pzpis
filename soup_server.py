# soap_server.py

import traceback
from wsgiref.simple_server import make_server

from spyne import (
    Application, rpc, ServiceBase,
    Integer, Unicode, Date, DateTime, Boolean as SpyneBool, Array, ComplexModel
)
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

from db import (
    SessionLocal,
    Artist, Album, Track,
    User, Playlist, PlaylistTrack, TrackArtist
)


# === 1. Определяем все Spyne-модели (ComplexModel) ===

class ArtistModel(ComplexModel):
    __namespace__ = "tns"
    id         = Integer
    nickname   = Unicode
    real_name  = Unicode
    country    = Unicode
    debut_year = Integer

class AlbumModel(ComplexModel):
    __namespace__ = "tns"
    id           = Integer
    title        = Unicode
    release_date = Date
    artist_id    = Integer
    genre        = Unicode
    label        = Unicode

class TrackModel(ComplexModel):
    __namespace__ = "tns"
    id       = Integer
    title    = Unicode
    duration = Integer
    album_id = Integer

class UserModel(ComplexModel):
    __namespace__ = "tns"
    id                = Integer
    username          = Unicode
    email             = Unicode
    registration_date = Date

class PlaylistModel(ComplexModel):
    __namespace__ = "tns"
    id         = Integer
    name       = Unicode
    user_id    = Integer
    created_at = DateTime

class PlaylistTrackModel(ComplexModel):
    __namespace__ = "tns"
    playlist_id = Integer
    track_id    = Integer
    added_at    = DateTime

class TrackArtistModel(ComplexModel):
    __namespace__ = "tns"
    track_id   = Integer
    artist_id  = Integer
    is_primary = SpyneBool

# Обёртка для содержимого всей БД
class DBContent(ComplexModel):
    __namespace__ = "tns"
    artists         = Array(ArtistModel)
    albums          = Array(AlbumModel)
    tracks          = Array(TrackModel)
    users           = Array(UserModel)
    playlists       = Array(PlaylistModel)
    playlist_tracks = Array(PlaylistTrackModel)
    track_artists   = Array(TrackArtistModel)


# === 2. SOAP-сервис ===

class MusicService(ServiceBase):

    @rpc(_returns=DBContent)
    def getDatabase(ctx):
        session = SessionLocal()
        out = DBContent()
        out.artists         = session.query(Artist).all()
        out.albums          = session.query(Album).all()
        out.tracks          = session.query(Track).all()
        out.users           = session.query(User).all()
        out.playlists       = session.query(Playlist).all()
        out.playlist_tracks = session.query(PlaylistTrack).all()
        out.track_artists   = session.query(TrackArtist).all()
        session.close()
        return out

soap_app = Application(
    [MusicService],
    tns='tns',
    in_protocol=Soap11(),
    out_protocol=Soap11(),
)
wsgi_soap = WsgiApplication(soap_app)


def application(environ, start_response):
    path   = environ.get('PATH_INFO', '').rstrip('/')
    method = environ.get('REQUEST_METHOD', 'GET').upper()

    # 2) GET /all   — отдаём HTML-таблицы
    if method == 'GET' and path == '/all':
        try:
            session = SessionLocal()
            data = {
                "artists": [ ... ],     # как в вашем коде
                "albums":  [ ... ],
                "tracks":  [ ... ],
                "users":   [ ... ],
                "playlists":[ ... ],
            }
            session.close()

            # Генерация HTML — копипаст вашего блока
            html = ['<!DOCTYPE html><html><head><meta charset="utf-8">', ...]
            # … и т.д.
            body = '\n'.join(html).encode('utf-8')
            start_response('200 OK', [
                ('Content-Type', 'text/html; charset=utf-8'),
                ('Content-Length', str(len(body)))
            ])
            return [body]

        except Exception as e:
            tb = traceback.format_exc()
            err = f"<pre>Error: {e}\n\n{tb}</pre>".encode('utf-8')
            start_response('500 Internal Server Error', [
                ('Content-Type', 'text/html; charset=utf-8'),
                ('Content-Length', str(len(err)))
            ])
            return [err]

    # 3) Всё остальное — 404
    start_response('404 Not Found', [('Content-Type', 'text/plain')])
    return [b'Not Found']


if __name__ == '__main__':
    print("Server listening on http://0.0.0.0:8000")
    make_server('0.0.0.0', 8000, application).serve_forever()