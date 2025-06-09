from pathlib import Path
from rich import print_json
from rich.logging import RichHandler
from typing import cast, Tuple, Type, TypeVar
import argparse
from importlib import resources
from importlib.resources.abc import Traversable
import os
import json
import logging
import msgspec
import platformdirs
import random
import regex
import sys
#tag correction not removing old tag kept 2x?

PLATFORMDIRS = platformdirs.PlatformDirs(appname='bluprints', appauthor=False)
CONFIG_FOLDER = PLATFORMDIRS.user_config_path
SAMPLE_FILE = CONFIG_FOLDER / 'bluprints_sample.json'
DICT_FILE = CONFIG_FOLDER / 'bluprints_dict.json'
DATA_PATH = resources.files('bluprints').joinpath('_data')
EXAMPLE_DICT_PATH = DATA_PATH / 'bluprints_dict.json'
EXAMPLE_SAMPLE_PATH = DATA_PATH / 'bluprints_sample.json'
T = TypeVar('T')
logging.basicConfig(
	level=logging.INFO, format='%(message)s', datefmt='[%X]', handlers=[RichHandler()]
)


class Category(msgspec.Struct, kw_only=True):
	Emp: str
	Ent: str
	PBay: str


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
	Action: str
	Body: str
	Comment: str
	Costume: str
	Date: str
	Ethnic: str
	File: str
	Group: str
	Location: str
	Nation: str
	Performer: str
	Plot: str
	Position: str
	Qualifier: str
	Resolution: str
	Studio: str


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
	Style: str
	Title: str
	Category: Category
	Taglist: Taglist
	Table: dict[str, str] | None = None
	Cover: str
	Collages: list[str]
	Graph: str
	Poster: str
	Screens: list[str]


def decode_json(fpath: Path | Traversable, model: Type[T]) -> T:
	raw_bytes = fpath.read_bytes()
	edit = msgspec.json.decode(raw_bytes, type=model)

	return edit


def save_json(
	data: Definitions | Sample | TagsForm,
	fpath: Path,
	indent: int = 4,
	sort_keys: bool = False,
) -> None:
	json_str = msgspec.to_builtins(data)

	with open(fpath, 'w', encoding='utf8') as json_file:
		json.dump(json_str, json_file, indent=indent, sort_keys=sort_keys)


def ensure_data_files() -> Tuple[Definitions, Sample]:
	example_dict = decode_json(EXAMPLE_DICT_PATH, Definitions)
	example_sample = decode_json(EXAMPLE_SAMPLE_PATH, Sample)
	CONFIG_FOLDER.mkdir(parents=True, exist_ok=True)

	if not DICT_FILE.exists():
		save_json(example_dict, DICT_FILE, indent=4, sort_keys=True)

	if not SAMPLE_FILE.exists():
		save_json(example_sample, SAMPLE_FILE, indent=4, sort_keys=True)

	return decode_json(DICT_FILE, Definitions), decode_json(SAMPLE_FILE, Sample)


DICTIONARY, SAMPLE = ensure_data_files()


def parse_bluprints() -> argparse.ArgumentParser:
	parser = argparse.ArgumentParser(
		prog='bluprints', description='Presentation generator'
	)
	parser.add_argument('filepath', help='Path(s) to the tag file')

	return parser


def provide_path(ftype: str, item: Path) -> Path:
	while not item.exists():
		item = Path(input(f'{ftype} not found please provide path:')).resolve()

	return item


def update_dict(subkey: str, tag: str) -> Definitions:
	value = ''

	while not value:
		value = input(f'Please enter word group value related to the tag{os.linesep}')

	getattr(DICTIONARY, subkey)[tag] = value
	save_json(DICTIONARY, DICT_FILE, indent=4, sort_keys=True)

	return decode_json(DICT_FILE, Definitions)


def validate_tags(fpath: Path, subkey: str, tags: list[str]) -> list[str]:
	global DICTIONARY
	keyset = 'Group', 'Date', 'Comment', 'Performer', 'Studio'
	pattern = '^\\d{1,4}p'
	final_tags = tags
	edit = decode_json(fpath, TagsForm)

	for tag in tags:
		rgx = regex.findall(pattern, tag)
		removed = False

		if hasattr(DICTIONARY, subkey) or subkey in keyset:
			if hasattr(DICTIONARY, subkey):
				subdict_tag = getattr(DICTIONARY, subkey).get(tag.lower())

			if subkey in keyset:
				subdict_tag = None

			if not subdict_tag and not rgx and subkey not in keyset:
				for key in DICTIONARY.__annotations__.keys():
					field_dict = getattr(DICTIONARY, key)

					if field_dict is not None and tag.lower() in field_dict:
						logging.warning(
							f'The tag [{tag.lower()}] already exists for the following category: [{key.upper()}]\nRemoving from taglist subkey [{subkey.upper()}].'
						)
						input('Press Enter to continue')
						final_tags.remove(tag)
						temp_list = getattr(getattr(edit, 'Taglist'), subkey).split()
						temp_list.remove(tag)
						setattr(getattr(edit, 'Taglist'), subkey, ' '.join(temp_list))
						save_json(edit, fpath, indent=4)
						removed = True

						break

				if not removed:
					answer = 0
					logging.warning(
						f'The following tag(s) do not exist in the dictionary: [{tag.lower()}]{os.linesep}'
					)

					try:
						while answer not in (1, 2, 3):
							answer = int(
								input(
									f'Would you like to correct it (1), update the [{subkey.upper()}] subkey (2) or dismiss it (3)?{os.linesep}'
								)
							)

					except ValueError:
						logging.error('Invalid input. Please enter a valid integer.')

					match answer:
						case 1:
							replacement = ''

							while not replacement:
								replacement = input(
									f'Please enter valid replacement{os.linesep}'
								)

								try:
									logging.info(
										f'Replacement value: {getattr(DICTIONARY, subkey)[replacement]}'
									)

								except KeyError:
									logging.info(
										f'Replacement: {replacement} does not exist in dictionnary.'
									)
									replacement = ''

							final_tags[tags.index(tag)] = replacement
							temp_list = getattr(getattr(edit, 'Taglist'), subkey).split()
							temp_list.remove(tag)
							temp_list.append(replacement)
							temp_list = list(set(temp_list))
							temp_list.sort()
							setattr(getattr(edit, 'Taglist'), subkey, ' '.join(temp_list))
							save_json(edit, fpath, indent=4)
							logging.info('The taglist was corrected.')

						case 2:
							DICTIONARY = update_dict(subkey, tag)
							logging.warning('The dictionnary was updated.')

						case 3:
							final_tags.remove(tag)
							temp_list = getattr(getattr(edit, 'Taglist'), subkey).split()
							temp_list.remove(tag)
							setattr(getattr(edit, 'Taglist'), subkey, ' '.join(temp_list))
							save_json(edit, fpath, indent=4)
							logging.warning(
								'The key/value pair was not added to the dictionary'
							)

	return final_tags


def import_tags(
	optional_keys: list[str],
	subkey: str,
	tags: list[str],
	fpath: Path,
) -> str | None:
	desc = []

	if not tags and subkey not in optional_keys:
		while not tags:
			tags = input(f'Please input missing tag(s) for [{subkey.upper()}]').split()

	tags = validate_tags(fpath, subkey, tags)

	if tags:
		for index, tag in enumerate(tags):
			if tag not in tags[-2:]:
				number = index

			elif tag is tags[-1] or len(tags) == 1:
				number = -1

			elif tag is tags[-2]:
				number = -2

			desc.append(build_sentence(subkey, tag, number))

		return ''.join(desc)

	else:
		return None


def build_sentence(subkey: str, tag: str, index: int) -> str:
	sep = (
		' ',
		'.',
		', ',
		'/',
		' up to ',
		' and ',
		' along with ',
		' as well as ',
		' together with ',
	)
	res_pattern = '^\\d{1,4}p$'
	keyset = 'Date', 'Performer', 'Studio'

	if hasattr(DICTIONARY, subkey):
		subkey_attr = getattr(DICTIONARY, subkey)

	match index:
		case -2:
			if keyset[0] is subkey:
				return str(tag.replace(sep[1], sep[3]) + sep[4])

			elif subkey in keyset or regex.match(res_pattern, tag):
				return str(tag.replace(sep[1], sep[0]) + random.choice(sep[5:8]))

			else:
				return str(subkey_attr[tag] + random.choice(sep[5:8]))

		case -1:
			if keyset[0] is subkey:
				return str(
					tag.replace(sep[1], sep[3])
				)

			elif subkey in keyset or regex.match(res_pattern, tag.lower()):
				return str(tag.replace(sep[1], sep[0]))

			elif subkey is keyset[1]:
				return str(tag)

			else:
				return str(subkey_attr[tag.lower()])

		case _:
			if subkey in keyset or regex.match(res_pattern, tag):
				return str(tag.replace(sep[1], sep[0]) + sep[2])

			else:
				return str(subkey_attr[tag.lower()] + sep[2])


def organize_tags(subkey: str, tags_form: TagsForm) -> list[str]:
	tags = []

	if hasattr(tags_form.Taglist, subkey) and subkey != 'Comment':
		tags = getattr(tags_form.Taglist, subkey).split()
		tags = list(set(tags))
		tags.sort()

	return tags


def build_desc(fpath: Path) -> dict[str, str | dict[str, str]]:
	optional_keys = [
		'Body',
		'Comment',
		'Costume',
		'Date',
		'Ethnic',
		'Group',
		'Location',
		'Nation',
		'Plot',
		'Position',
		'Qualifier',
	]
	dict_keys = ['Action', 'File', 'Performer', 'Resolution', 'Studio']
	dict_keys.extend(optional_keys)
	dict_keys.sort()
	desc: dict[str, str | dict[str, str]] = {}
	tags_form = decode_json(fpath, TagsForm)

	for subkey in dict_keys:
		tags = organize_tags(subkey, tags_form)

		match subkey:
			case 'Comment':
				desc[subkey] = getattr(SAMPLE, subkey).replace(
					f'{{{subkey}}}', getattr(tags_form.Taglist, 'Comment')
				)

			case 'Date':
				tags_import = import_tags(optional_keys, subkey, tags, fpath)

				if tags_import:
					desc[subkey] = random.choice(getattr(SAMPLE, subkey)).replace(
						f'{{{subkey}}}', tags_import
					)

			case _:
				if subkey != 'Group' and tags:
					tags_import = import_tags(optional_keys, subkey, tags, fpath)

					if tags_import:
						desc[subkey] = random.choice(getattr(SAMPLE, subkey)).replace(
							f'{{{subkey}}}', tags_import
						)

	updated_tags_form = decode_json(fpath, TagsForm)
	final_taglist = []

	for subkey in dict_keys:
		updated_tags = organize_tags(subkey, updated_tags_form)

		if updated_tags:
			final_taglist.extend(updated_tags)

	final_taglist.sort()
	desc['Title'] = tags_form.Title
	desc['Style'] = tags_form.Style
	desc['Category'] = msgspec.to_builtins(tags_form.Category)
	desc['Comment'] = tags_form.Taglist.Comment
	desc['Taglist'] = ' '.join(final_taglist).lower()

	if hasattr(tags_form, 'Table'):
		desc['Table'] = getattr(tags_form, 'Table')

	desc['Cover'] = tags_form.Cover

	if hasattr(tags_form, 'Collages'):
		collages = getattr(tags_form, 'Collages')
		collage_count = len(collages)

		if collage_count == 1:
			desc['Collages'] = ''.join(collages)

		elif collage_count > 1:
			desc['Collages'] = f'[spoiler=Collages]{"".join(collages)}[/spoiler]'

	if hasattr(tags_form, 'Graph'):
		desc['Graph'] = getattr(tags_form, 'Graph')

	if hasattr(tags_form, 'Poster'):
		desc['Poster'] = getattr(tags_form, 'Poster')

	if hasattr(tags_form, 'Screens'):
		screens = getattr(tags_form, 'Screens')
		screens_count = len(screens)

		if screens_count == 1:
			desc['Screens'] = ''.join(screens)

		elif screens_count > 1:
			desc['Screens'] = f'[spoiler=Screens]{"".join(screens)}[/spoiler]'

	return desc


def main() -> None:
	parser = parse_bluprints()
	args = parser.parse_args(sys.argv[1:])
	fpath = Path(args.filepath)

	while not fpath.exists():
		fpath = provide_path('tag_file', fpath)

	try:
		desc = build_desc(fpath)

	except FileNotFoundError as e:
		logging.error(f'{type(e).__name__}: {e}')
		logging.shutdown()
		sys.exit(1)

	json_str = msgspec.json.encode(desc).decode('utf-8')
	print_json(json_str)


if __name__ == '__main__':
	main()
