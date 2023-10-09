import datetime
import gzip
import os
import platform
import re
from pathlib import Path
from typing import Annotated, Optional

import pytz
import typer
from tqdm import tqdm

FILENAME_REGEX = re.compile(r"^(\d+)-(\d+)-(\d+)(?:-\d+)?\.log\.gz")
LOG_LINE_REGEX = re.compile(r"^\[(?:[^\]]+ )?(\d+):(\d+):(\d+)(?:\.\d+)?\]")


app = typer.Typer()


@app.command()
def main(
    instances: Annotated[Optional[list[Path]], typer.Argument()] = None,
    default_root: bool = True,
    timezone: Optional[str] = None,
):
    if not instances:
        instances = []

    if default_root:
        instances.insert(0, Path(default_minecraft_root()))

    if timezone is not None:
        tzinfo = pytz.timezone(timezone)
    else:
        tzinfo = None

    total_playtime = datetime.timedelta()

    instances_bar = tqdm(instances, leave=False)
    for instance in instances_bar:
        instance = instance.resolve()
        logs = instance / "logs"
        instances_bar.set_postfix_str(str(logs))

        instance_playtime = datetime.timedelta()

        files = list(logs.glob("*.gz")) + [logs / "latest.log"]
        files_bar = tqdm(files, leave=False)

        for path in files_bar:
            files_bar.set_postfix_str(path.name)

            if playtime := get_log_playtime(path, tzinfo):
                instance_playtime += playtime

        total_playtime += instance_playtime
        short_path = Path("...", *instance.parts[-2:])
        instances_bar.write(f"{short_path} --- {print_playtime(instance_playtime)}")

    print(f"\nTotal: {print_playtime(total_playtime)}\n")


def print_playtime(playtime: datetime.timedelta) -> str:
    hours = playtime.total_seconds() / 60 / 60
    return f"{playtime} ({hours:.2f} hours)"


def get_log_playtime(path: Path, tzinfo: datetime.tzinfo | None):
    # make sure this is a log file
    if not path.is_file():
        return

    try:
        if path.name == "latest.log":
            date = datetime.date.fromtimestamp(path.stat().st_mtime)
            lines = decode_log(path.read_bytes()).splitlines()
        else:
            date = get_log_date(path)
            if not date:
                return

            with gzip.open(path) as f:
                lines = decode_log(f.read()).splitlines()
    except Exception as e:
        e.add_note(f"  File: {path}")
        raise

    for line in lines:
        if min_dt := get_log_line_dt(date, line, tzinfo):
            break
    else:
        return

    for line in reversed(lines):
        if max_dt := get_log_line_dt(date, line, tzinfo):
            return max_dt - min_dt


def decode_log(data: bytes) -> str:
    exceptions = list[Exception]()

    for encoding in ["utf-8", "cp1252"]:
        try:
            return data.decode(encoding)
        except UnicodeDecodeError as e:
            exceptions.append(e)

    raise ExceptionGroup("Failed to decode file contents", exceptions)


def get_log_date(path: Path):
    match = FILENAME_REGEX.match(path.name)
    if not match:
        return

    return datetime.date(
        year=int(match[1]),
        month=int(match[2]),
        day=int(match[3]),
    )


def get_log_line_dt(date: datetime.date, line: str, tzinfo: datetime.tzinfo | None):
    match = LOG_LINE_REGEX.match(line)
    if not match:
        return

    time = datetime.time(
        hour=int(match[1]),
        minute=int(match[2]),
        second=int(match[3]),
        tzinfo=tzinfo,
    )
    return datetime.datetime.combine(date, time)


def default_minecraft_root() -> str:
    match platform.system():
        case "Windows":
            appdata = os.getenv("appdata", "~/AppData/Roaming")
            return f"{appdata}/.minecraft"
        case "Darwin":
            return "~/Library/Application Support/minecraft"
        case _:
            return "~/.minecraft"


if __name__ == "__main__":
    app()
