import csv
from typing import Iterator
from pathlib import Path


def csv_loader(file_path: str) -> Iterator[list[str]]:
    reader = csv.reader(Path(file_path).open())
    for row in reader:
        yield row


def csv_dumper(file_path: str, rows: list[list[str]], mode: str = "w") -> None:
    writer = csv.writer(Path(file_path).open(mode=mode, encoding="utf-8-sig"))
    writer.writerows(rows)
