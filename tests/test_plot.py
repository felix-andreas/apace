import elements as el
from elements.plotting import plot_lattice

def test_plot():
    file_path = 'tests/data/lattices/FODO-lattice.json'
    line = el.read_lattice_file_json(file_path)
    fodo = line.cells['fodo']
    print(fodo.length)
    Q1 = line.elements['Q1']
    B1 = line.elements['B1']
    lin = el.LinBeamDyn(line)

    plot_lattice(lin.get_twiss(), line, eta_x_scale=1, path='out.pdf')


