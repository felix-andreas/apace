import os
import re
from .classes import Drift, Bend, Quad, Sext, Line, Mainline


def read_lattice_file(filepath):
    latticename = os.path.basename(filepath)
    with open(filepath) as file:
        lines = re.sub('[ \t]', '', file.read()).splitlines()
        lines = [line for line in lines if line and line[0] != '#']

        # devide lines into elementname, type, parameter and comment
        length = len(lines)
        objectname = [''] * length
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
                objectname[i] = _split[0]
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
            del objectname[i]
            del comments[i]
            del parameters[i]

        # create and execute string
        lis = [f'{objectname[i]} = {type[i]}("{objectname[i]}", {parameters[i]}, comment="{comments[i]}")' for i in
               range(len(objectname))]
        string = '\n'.join(lis)
        # print(string)
        exec(string)
        return list(locals().values())[-1]

def save_lattice_file(line, filepath):
    elements_dict = dict()
    for x in line.elements:
        if type(x) in elements_dict:
            elements_dict[type(x)].append(x)
        else:
            elements_dict[type(x)] = [x]
    outputlist = []
    for key, value in elements_dict.items():
        outputlist.append(f"##### {key}s #####")
        outputlist.extend([])

    # with open(filepath, 'w') as file:
    #
    #     file.write()
    #     file.write("\n".join())


if __name__ == '__main__':
    filepath = os.getcwd() + '/lattices/BII_2016-06-10_user_Sym_noID_DesignLattice1996.lte'
    filepath2 = "test.lte"
    line = read_lattice_file(filepath)
    save_lattice_file(line, filepath2)