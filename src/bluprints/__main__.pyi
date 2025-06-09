import argparse
import msgspec
from _typeshed import Incomplete
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import TypeVar

PLATFORMDIRS: Incomplete
CONFIG_FOLDER: Incomplete
SAMPLE_FILE: Incomplete
DICT_FILE: Incomplete
DATA_PATH: Incomplete
EXAMPLE_DICT_PATH: Incomplete
EXAMPLE_SAMPLE_PATH: Incomplete
T = TypeVar('T')

class Category(msgspec.Struct, kw_only=True):
	Emp: str = ...
	Ent: str = ...
	PBay: str = ...

class Table(msgspec.Struct, kw_only=True):
	Nudity: str
	Images: str
	Extras: str
	Maximum: str
	Minimum: str
	Average: str
	Median: str
	Total: str

class Taglist(msgspec.Struct, kw_only=True):
	Action: str = ...
	Body: str = ...
	Comment: str = ...
	Costume: str = ...
	Date: str = ...
	Ethnic: str = ...
	File: str = ...
	Group: str = ...
	Location: str = ...
	Nation: str = ...
	Performer: str = ...
	Plot: str = ...
	Position: str = ...
	Qualifier: str = ...
	Resolution: str = ...
	Studio: str = ...

class Definitions(msgspec.Struct, kw_only=True):
	Action: dict[str, str]
	Body: dict[str, str]
	Costume: dict[str, str]
	Ethnic: dict[str, str]
	File: dict[str, str]
	Location: dict[str, str]
	Nation: dict[str, str]
	Plot: dict[str, str]
	Position: dict[str, str]
	Qualifier: dict[str, str]
	Resolution: dict[str, str]

class Sample(msgspec.Struct, kw_only=True):
	Action: list[str]
	Body: list[str]
	Comment: str
	Costume: list[str]
	Date: list[str]
	Ethnic: list[str]
	File: list[str]
	Location: list[str]
	Nation: list[str]
	Performer: list[str]
	Plot: list[str]
	Position: list[str]
	Qualifier: list[str]
	Resolution: list[str]
	Studio: list[str]
	Table: dict[str, str] | None
	Taglist: str | None

class TagsForm(msgspec.Struct, kw_only=True):
	Category: Category
	Collages: list[str]
	Cover: str
	Graph: str
	Poster: str
	Screens: list[str]
	Style: str
	Table: dict[str, str] | None = ...
	Taglist: Taglist
	Title: str

def decode_json(fpath: Path | Traversable, model: type[T]) -> T: ...
def save_json(data: Definitions | Sample | TagsForm, fpath: Path, indent: int = 4, sort_keys: bool = False) -> None: ...
def ensure_data_files() -> tuple[Definitions, Sample]: ...

DICTIONARY: Incomplete
SAMPLE: Incomplete

def parse_bluprints() -> argparse.ArgumentParser: ...
def provide_path(ftype: str, item: Path) -> Path: ...
def update_dict(subkey: str, tag: str) -> Definitions: ...
def validate_tags(fpath: Path, subkey: str, tags: list[str]) -> list[str]: ...
def import_tags(optional_keys: list[str], subkey: str, tags: list[str], fpath: Path) -> str | None: ...
def build_sentence(subkey: str, tag: str, index: int) -> str: ...
def organize_tags(subkey: str, tags_form: TagsForm) -> list[str]: ...
def build_desc(fpath: Path) -> dict[str, str | dict[str, str]]: ...
def main() -> None: ...
