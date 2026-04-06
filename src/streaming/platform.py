from datetime import datetime, timedelta
from streaming.users import PremiumUser, FreeUser, FamilyAccountUser, FamilyMember
from streaming.tracks import Song
from streaming.playlists import CollaborativePlaylist

class StreamingPlatform:
    def __init__(self, name: str) -> None:
        self.name = name
        self.catalogue = {}
        self.users = {}
        self.artists = {}
        self.albums = {}
        self.playlists = {}
        self.sessions = []

    def add_track(self, track) -> None:
        self.catalogue[track.track_id] = track

    def add_user(self, user) -> None:
        self.users[user.user_id] = user

    def add_artist(self, artist) -> None:
        self.artists[artist.artist_id] = artist

    def add_album(self, album) -> None:
        self.albums[album.album_id] = album

    def add_playlist(self, playlist) -> None:
        self.playlists[playlist.playlist_id] = playlist

    def record_session(self, session) -> None:
        self.sessions.append(session)
        session.user.add_session(session)

    def get_track(self, track_id: str):
        return self.catalogue.get(track_id)

    def get_user(self, user_id: str):
        return self.users.get(user_id)

    def get_artist(self, artist_id: str):
        return self.artists.get(artist_id)

    def get_album(self, album_id: str):
        return self.albums.get(album_id)

    def all_users(self) -> list:
        return list(self.users.values())

    def all_tracks(self) -> list:
        return list(self.catalogue.values())

    def total_listening_time_minutes(self, start, end) -> float:
        total_seconds = 0

        for session in self.sessions:
            if start <= session.timestamp <= end:
                total_seconds += session.duration_listened_seconds

        return total_seconds / 60

    def avg_unique_tracks_per_premium_user(self, days: int = 30) -> float:
        premium_users = []

        for user in self.users.values():
            if isinstance(user, PremiumUser):
                premium_users.append(user)

        if len(premium_users) == 0:
            return 0.0

        cutoff = datetime.now() - timedelta(days=days)
        total_unique_count = 0

        for user in premium_users:
            unique_track_ids = set()

            for session in user.sessions:
                if session.timestamp >= cutoff:
                    unique_track_ids.add(session.track.track_id)

            total_unique_count += len(unique_track_ids)

        return total_unique_count / len(premium_users)

    def track_with_most_distinct_listeners(self):
        if len(self.sessions) == 0:
            return None

        listeners_by_track = {}

        for session in self.sessions:
            track_id = session.track.track_id
            user_id = session.user.user_id

            if track_id not in listeners_by_track:
                listeners_by_track[track_id] = set()

            listeners_by_track[track_id].add(user_id)

        best_track = None
        best_count = -1

        for track_id, user_ids in listeners_by_track.items():
            if len(user_ids) > best_count:
                best_count = len(user_ids)
                best_track = self.get_track(track_id)

        return best_track

    def avg_session_duration_by_user_type(self) -> list[tuple[str, float]]:
        user_types = {
            "FreeUser": [],
            "PremiumUser": [],
            "FamilyAccountUser": [],
            "FamilyMember": [],
        }

        for user in self.users.values():
            type_name = type(user).__name__

            if type_name in user_types:
                for session in user.sessions:
                    user_types[type_name].append(session.duration_listened_seconds)

        result = []

        for type_name, durations in user_types.items():
            if len(durations) == 0:
                average = 0.0
            else:
                average = sum(durations) / len(durations)

            result.append((type_name, float(average)))

        result.sort(key=lambda item: item[1], reverse=True)
        return result

    def total_listening_time_underage_sub_users_minutes(self, age_threshold: int = 18) -> float:
        total_seconds = 0

        for user in self.users.values():
            if isinstance(user, FamilyMember) and user.age < age_threshold:
                for session in user.sessions:
                    total_seconds += session.duration_listened_seconds

        return total_seconds / 60

    def top_artists_by_listening_time(self, n: int = 5) -> list[tuple]:
        artist_minutes = {}

        for session in self.sessions:
            track = session.track

            if isinstance(track, Song):
                artist = track.artist

                if artist.artist_id not in artist_minutes:
                    artist_minutes[artist.artist_id] = 0

                artist_minutes[artist.artist_id] += session.duration_listened_seconds / 60

        result = []

        for artist_id, total_minutes in artist_minutes.items():
            artist = self.get_artist(artist_id)
            result.append((artist, float(total_minutes)))

        result.sort(key=lambda item: item[1], reverse=True)
        return result[:n]

    def user_top_genre(self, user_id: str):
        user = self.get_user(user_id)

        if user is None:
            return None

        if len(user.sessions) == 0:
            return None

        genre_seconds = {}
        total_seconds = 0

        for session in user.sessions:
            genre = session.track.genre
            seconds = session.duration_listened_seconds

            if genre not in genre_seconds:
                genre_seconds[genre] = 0

            genre_seconds[genre] += seconds
            total_seconds += seconds

        top_genre = None
        top_seconds = -1

        for genre, seconds in genre_seconds.items():
            if seconds > top_seconds:
                top_seconds = seconds
                top_genre = genre

        percentage = (top_seconds / total_seconds) * 100
        return (top_genre, float(percentage))

    def collaborative_playlists_with_many_artists(self, threshold: int = 3) -> list:
        result = []

        for playlist in self.playlists.values():
            if isinstance(playlist, CollaborativePlaylist):
                artist_ids = set()

                for track in playlist.tracks:
                    if isinstance(track, Song):
                        artist_ids.add(track.artist.artist_id)

                if len(artist_ids) > threshold:
                    result.append(playlist)

        return result

    def avg_tracks_per_playlist_type(self) -> dict[str, float]:
        playlist_counts = []
        collaborative_counts = []

        for playlist in self.playlists.values():
            if isinstance(playlist, CollaborativePlaylist):
                collaborative_counts.append(len(playlist.tracks))
            else:
                playlist_counts.append(len(playlist.tracks))

        if len(playlist_counts) == 0:
            playlist_average = 0.0
        else:
            playlist_average = sum(playlist_counts) / len(playlist_counts)

        if len(collaborative_counts) == 0:
            collaborative_average = 0.0
        else:
            collaborative_average = sum(collaborative_counts) / len(collaborative_counts)

        return {
            "Playlist": float(playlist_average),
            "CollaborativePlaylist": float(collaborative_average),
        }

    def users_who_completed_albums(self) -> list[tuple]:
        result = []

        for user in self.users.values():
            listened_track_ids = user.unique_tracks_listened()
            completed_albums = []

            for album in self.albums.values():
                album_track_ids = album.track_ids()

                if len(album_track_ids) == 0:
                    continue

                if album_track_ids.issubset(listened_track_ids):
                    completed_albums.append(album.title)

            if len(completed_albums) > 0:
                result.append((user, completed_albums))

        return result