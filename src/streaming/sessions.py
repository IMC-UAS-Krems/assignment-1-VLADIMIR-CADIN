class ListeningSession:
    def __init__(
        self,
        session_id: str,
        user,
        track,
        timestamp,
        duration_listened_seconds: int,
    ) -> None:
        self.session_id = session_id
        self.user = user
        self.track = track
        self.timestamp = timestamp
        self.duration_listened_seconds = duration_listened_seconds

    def duration_listened_minutes(self) -> float:
        return self.duration_listened_seconds / 60