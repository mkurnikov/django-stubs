import itertools
import shutil
import subprocess
import sys
from argparse import ArgumentParser
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Pattern, Union

import importlib_metadata
from git import Repo

from scripts.enabled_test_modules import (
    EXTERNAL_MODULES, IGNORED_ERRORS, IGNORED_MODULES, MOCK_OBJECTS,
)

DJANGO_COMMIT_REFS = {
    '2.2': 'e8b0903976077b951795938b260211214ed7fe41',
    '3.0': '7ec5962638144cbf4c2e47ea7d8dc02d1ce44394'
}
PROJECT_DIRECTORY = Path(__file__).parent.parent
DJANGO_SOURCE_DIRECTORY = PROJECT_DIRECTORY / 'django-sources'  # type: Path


def get_unused_ignores(ignored_message_freq: Dict[str, Dict[Union[str, Pattern], int]]) -> List[str]:
    unused_ignores = []
    for root_key, patterns in IGNORED_ERRORS.items():
        for pattern in patterns:
            if (ignored_message_freq[root_key][pattern] == 0
                    and pattern not in itertools.chain(EXTERNAL_MODULES, MOCK_OBJECTS)):
                unused_ignores.append(f'{root_key}: {pattern}')
    return unused_ignores


def is_pattern_fits(pattern: Union[Pattern, str], line: str):
    if isinstance(pattern, Pattern):
        if pattern.search(line):
            return True
    else:
        if pattern in line:
            return True
    return False


def is_ignored(line: str, test_folder_name: str, *, ignored_message_freqs: Dict[str, Dict[str, int]]) -> bool:
    if 'runtests' in line:
        return True

    if test_folder_name in IGNORED_MODULES:
        return True

    for pattern in IGNORED_ERRORS.get(test_folder_name, []):
        if is_pattern_fits(pattern, line):
            ignored_message_freqs[test_folder_name][pattern] += 1
            return True

    for pattern in IGNORED_ERRORS['__common__']:
        if is_pattern_fits(pattern, line):
            ignored_message_freqs['__common__'][pattern] += 1
            return True

    return False


def replace_with_clickable_location(error: str, abs_test_folder: Path) -> str:
    raw_path, _, error_line = error.partition(': ')
    fname, _, line_number = raw_path.partition(':')

    try:
        path = abs_test_folder.joinpath(fname).relative_to(PROJECT_DIRECTORY)
    except ValueError:
        # fail on travis, just show an error
        return error

    clickable_location = f'./{path}:{line_number or 1}'
    return error.replace(raw_path, clickable_location)


def get_installed_django_version() -> str:
    return importlib_metadata.version('Django')


def get_django_repo_object() -> Repo:
    if not DJANGO_SOURCE_DIRECTORY.exists():
        DJANGO_SOURCE_DIRECTORY.mkdir(exist_ok=True, parents=False)
        return Repo.clone_from('https://github.com/django/django.git', DJANGO_SOURCE_DIRECTORY)
    else:
        repo = Repo(DJANGO_SOURCE_DIRECTORY)
        return repo


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--django_version', choices=['2.2', '3.0'], required=True)
    args = parser.parse_args()

    # installed_django_version = get_installed_django_version()
    # if not installed_django_version.startswith(args.django_version):
    #     raise ValueError(f'Install Django {args.django_version!r} to run script with this set of parameters.')

    commit_sha = DJANGO_COMMIT_REFS[args.django_version]
    repo = get_django_repo_object()
    if repo.head.commit.hexsha != commit_sha:
        repo.git.fetch('origin')
        repo.git.checkout(commit_sha)

    mypy_config_file = (PROJECT_DIRECTORY / 'scripts' / 'mypy.ini').absolute()
    mypy_cache_dir = Path(__file__).parent / '.mypy_cache'
    tests_root = DJANGO_SOURCE_DIRECTORY / 'tests'
    global_rc = 0

    try:
        mypy_options = ['--cache-dir', str(mypy_config_file.parent / '.mypy_cache'),
                        '--config-file', str(mypy_config_file),
                        '--show-traceback',
                        '--no-error-summary',
                        '--hide-error-context'
                        ]
        mypy_options += [str(tests_root)]

        import distutils.spawn

        mypy_executable = distutils.spawn.find_executable('mypy')
        mypy_argv = [mypy_executable, *mypy_options]
        completed = subprocess.run(
            mypy_argv,
            env={'PYTHONPATH': str(tests_root)},
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        output = completed.stdout.decode()

        ignored_message_freqs = defaultdict(lambda: defaultdict(int))

        sorted_lines = sorted(output.splitlines())
        for line in sorted_lines:
            try:
                path_to_error = line.split(':')[0]
                test_folder_name = path_to_error.split('/')[2]
            except IndexError:
                test_folder_name = 'unknown'

            if not is_ignored(line, test_folder_name,
                              ignored_message_freqs=ignored_message_freqs):
                global_rc = 1
                print(line)

        unused_ignores = get_unused_ignores(ignored_message_freqs)
        if unused_ignores:
            print('UNUSED IGNORES ------------------------------------------------')
            print('\n'.join(unused_ignores))

        sys.exit(global_rc)

    except BaseException as exc:
        shutil.rmtree(mypy_cache_dir, ignore_errors=True)
        raise exc
