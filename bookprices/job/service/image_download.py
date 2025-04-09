from bookprices.shared.db.database import Database


class ImageDownloadService:
    def __init__(self, db: Database) -> None:
        self._db = db


