class Playlist:
    def __init__(self, playlist_id: str, name: str, owner) -> None:
        self.playlist_id = playlist_id
        self.name = name
        self.owner = owner
        self.tracks = []

    def add_track(self, track) -> None:
        if track not in self.tracks:
            self.tracks.append(track)

    def remove_track(self, track_id: str) -> None:
        for track in self.tracks:
            if track.track_id == track_id:
                self.tracks.remove(track)
                break

    def total_duration_seconds(self) -> int:
        total = 0
        for track in self.tracks:
            total += track.duration_seconds
        return total


class CollaborativePlaylist(Playlist):
    def __init__(self, playlist_id: str, name: str, owner) -> None:
        super().__init__(playlist_id, name, owner)
        self.contributors = [owner]

    def add_contributor(self, user) -> None:
        if user not in self.contributors:
            self.contributors.append(user)

    def remove_contributor(self, user) -> None:
        if user != self.owner and user in self.contributors:
            self.contributors.remove(user)