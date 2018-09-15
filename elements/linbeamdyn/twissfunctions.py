from elements.utils import AttrDict




def get_twissdata(line):
    twissdata = AttrDict()
    for element in line.lattice:
