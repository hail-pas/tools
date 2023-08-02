import csv
from pathlib import Path
from typing import Iterator


def csv_loader(file_path: str) -> Iterator[list[str]]:
    reader = csv.reader(Path(file_path).open())
    for row in reader:
        yield row


def csv_dumper(file_path: str, rows: list[list[str]]) -> None:
    writer = csv.writer(Path(file_path).open(mode="w", encoding="utf-8-sig"))
    writer.writerows(rows)
