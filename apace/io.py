import os
import re
import json

from . import classes
from .classes import Lattice
import latticejson


def load_lattice(file_path, file_format='json') -> Lattice:
    """Read lattice file into lattice object.

    :param str file_path: Path to lattice file.
    :param str file_format: Format of the lattice file.
    :return: The root lattice of the lattice.
    """
    if file_format == 'json':
        return read_lattice_file_json(file_path)
    elif file_format == 'fle':
        return read_lattice_file_fle(file_path)
    else:
        raise NotImplementedError


def save_lattice(lattice, file_path, file_format='json'):
    """Save lattice object to lattice file.

    :param Lattice lattice: lattice object to be saved.
    :param str file_path: File path to which the lattice is saved.
    :param str file_format: Format of the lattice file.
    """
    if file_format == 'json':
        save_lattice_file_json(lattice, file_path)
    else:
        raise NotImplementedError


def read_lattice_file_fle(file_path):  # TODO: check and update
    lattice_name = os.path.basename(file_path)
    with open(file_path) as file:
        lines = re.sub('[ \t]', '', file.read()).splitlines()
        lines = [line for line in lines if line and line[0] != '#']

        # divide lines into object_name, type, parameter and comment
        length = len(lines)
        object_name = [''] * length
        type = [''] * length
        parameters = [''] * length
        comments = [''] * length
        following_lines = []
        starting_line = 0
        for i, line in enumerate(lines):
            # save comments
            _split = line.split('#')
            if len(_split) > 1:
                comments[i] = _split[1]
            _split = _split[0]

            # divide into starting and following lines
            _split = _split.split(':')
            if len(_split) > 1:
                starting_line = i
                object_name[i] = _split[0]
                _split = _split[1].split(',', maxsplit=1)
                type[i] = _split[0]
                parameters[i] = _split[1]
            else:
                following_lines.append(i)
                parameters[starting_line] += _split[0]
                if comments[i]:
                    comments[starting_line] += ' ' + comments[i]

        # delete following lines (in reverse order)
        for i in following_lines[::-1]:
            del object_name[i]
            del comments[i]
            del parameters[i]

        # create and execute string
        lis = [f'{object_name[i]} = {type[i]}("{object_name[i]}", {parameters[i]}, comment="{comments[i]}")' for i in
               range(len(object_name))]
        string = '\n'.join(lis)
        # print(string)
        exec(string)
        return list(locals().values())[-1]


def read_lattice_file_json(file_path):
    with open(file_path) as file:
        lattice_dict = json.load(file)

    latticejson.validate(lattice_dict)
    return Lattice.from_dict(lattice_dict)


def save_lattice_file_json(lattice, file_path):
    lattice_dict = lattice.as_dict()
    latticejson.validate(lattice_dict)
    with open(file_path, 'w') as outfile:
        json.dump(lattice.as_dict(), outfile, indent=2)
