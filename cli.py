import csv
from pathlib import Path
import typer

from parser.csv import csv_loader, csv_dumper
from translate.translator import Translator

cli = typer.Typer(help="Tools CLI")

@cli.command(help="翻译")
def translate(
    source_file: str = typer.Option(help="源文件路径"),
    dest_file: str = typer.Option(help="目标文件路径"),
    target_language: str = typer.Option(default="zh_CN", help="目标语种")
):
    assert Path(source_file).exists(), "源文件不存在"
    assert not Path(dest_file).exists(), "目标文件被占用"

    translate_client = Translator(
        target="zh-CN",
        source="en",
        # proxies={"http": "http://127.0.0.1:7890"}
    )

    values = csv_loader(source_file)

    writer = csv.writer(Path(dest_file).open(mode="w", encoding="utf-8-sig", newline=""))
    headers = next(values)
    column_count = len(headers)
    writer.writerows([headers])

    def translate_and_write(_rows):
        trans_responses = translate_client.translate(q=_rows)
        translated = [response.translatedText for response in trans_responses]
        for i in range(0, len(translated), column_count):
            writer.writerow([rows[i + bias] for bias in range(column_count)])
            writer.writerow([translated[i + bias] for bias in range(column_count)])

    rows = []
    for row in values:
        rows.extend(row)
        if len(rows) >= 5000:
            translate_and_write(_rows=rows)

    if rows:
        translate_and_write(_rows=rows)

    return "Success"


if __name__ == "__main__":
    cli()
