"""
诗歌归档模块
"""
import json
import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from .config import config


@dataclass
class PoemEntry:
    """保存一次打印结果"""
    poem: str
    caption: str
    image_path: Path
    poem_path: Path
    created_at: datetime

    def to_record(self) -> dict:
        try:
            poem_path = self.poem_path.relative_to(config.project_root)
        except ValueError:
            poem_path = self.poem_path

        try:
            image_path = self.image_path.relative_to(config.project_root)
        except ValueError:
            image_path = self.image_path

        return {
            "poem_file": str(poem_path),
            "image": str(image_path),
            "caption": self.caption,
            "created_at": self.created_at.isoformat(timespec="seconds")
        }


class PoemArchive:
    """管理诗歌归档"""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.archive_dir = config.poems_dir
        self.archive_dir.mkdir(exist_ok=True)
        self.index_path = self.archive_dir / "poems.jsonl"

    def save(self, poem: str, caption: str, image_path: Path) -> Optional[PoemEntry]:
        """保存诗歌文本和元数据"""
        try:
            timestamp = datetime.now()
            identifier = timestamp.strftime("%Y%m%d_%H%M%S_%f")
            poem_file = self.archive_dir / f"poem_{identifier}.txt"
            poem_file.write_text(poem, encoding="utf-8")

            entry = PoemEntry(
                poem=poem,
                caption=caption,
                image_path=image_path,
                poem_path=poem_file,
                created_at=timestamp
            )

            with self.index_path.open("a", encoding="utf-8") as fh:
                json.dump(entry.to_record(), fh, ensure_ascii=False)
                fh.write("\n")

            self.logger.info("诗歌已归档: %s", poem_file.name)
            return entry
        except Exception:
            self.logger.exception("保存诗歌归档失败")
            return None