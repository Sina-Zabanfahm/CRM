
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Generic, TypeVar

import sqlite3

from src.config.app_config import get_app_config
from src.persistence.resource_record import ResourceRecord
from src.states.web_resources import ResourceKind

TKey = TypeVar("TKey")
TValue = TypeVar("TValue")

class BaseRepository(ABC, Generic[TKey, TValue]):
    @abstractmethod
    def get(self, key: TKey) -> TValue | None :
        raise NotImplementedError
    
    @abstractmethod
    def upsert(self, value:TValue) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def delete(self, key: TKey) -> None:
        raise NotImplementedError
    

class ResourceRepository(BaseRepository[str, ResourceRecord]):

    def __init__(self, db_path: str | None = None):
        config = get_app_config()
        if db_path is not None:
            self.db_path = Path(db_path)
        else:
            self.db_path = Path(config.resource_db)
        self._init_db()

    
    def get(self, key:str) -> ResourceRecord | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                 """
                SELECT url, final_url, kind, content_type, last_crawled_at, 
                body_sha256, text_sha256, simhash
                FROM resource_records
                WHERE url = ?
                """,
                (key, ),
            ).fetchone()
        
        if row is None:
            return None
        return ResourceRecord(
            url=row["url"],
            final_url=row["final_url"],
            kind=ResourceKind(row["kind"]),
            content_type=row["content_type"],
            last_crawled_at=datetime.fromisoformat(row["last_crawled_at"])
            if row["last_crawled_at"]
            else None,
            body_sha256=row["body_sha256"],
            text_sha256=row["text_sha256"],
            simhash=row["simhash"],
        )
    
    def upsert(self, value: ResourceRecord) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
            """
            INSERT INTO resource_records 
            (
                url, final_url, kind, content_type, last_crawled_at,
                body_sha256, text_sha256, simhash
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                final_url=excluded.final_url,
                kind = excluded.kind,
                content_type = excluded.content_type,
                last_crawled_at = excluded.last_crawled_at,
                body_sha256 = excluded.body_sha256,
                text_sha256 = excluded.text_sha256,
                simhash = excluded.simhash
            """,
            (
                    value.url,
                    value.final_url,
                    value.kind.value,
                    value.content_type,
                    value.last_crawled_at.isoformat() if value.last_crawled_at else None,
                    value.body_sha256,
                    value.text_sha256,
                    value.simhash,
                ),
            )
            conn.commit()

    def delete(self, key: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "DELETE FROM resource_records WHERE url = ?",
                (key,),
            )
            conn.commit()

    def _init_db(self):
        if not self.db_path.exists():
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                             """
                            CREATE TABLE IF NOT EXISTS resource_records (
                                url TEXT PRIMARY KEY,
                                final_url TEXT,
                                kind TEXT NOT NULL,
                                content_type TEXT,
                                last_crawled_at TEXT,
                                body_sha256 TEXT,
                                text_sha256 TEXT,
                                simhash TEXT
                            )
                            """
                )
                conn.commit()
