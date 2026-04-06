class Album:
    def __init__(self, album_id: str, title: str, artist, release_year: int) -> None:
        self.album_id = album_id
        self.title = title
        self.artist = artist
        self.release_year = release_year
        self.tracks = []

    def add_track(self, track) -> None:
        track.album = self
        self.tracks.append(track)
        self.tracks.sort(key=lambda t: t.track_number)

    def track_ids(self) -> set[str]:
        ids = set()
        for track in self.tracks:
            ids.add(track.track_id)
        return ids

    def duration_seconds(self) -> int:
        total = 0
        for track in self.tracks:
            total += track.duration_seconds
        return total