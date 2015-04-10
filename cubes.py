import itertools
import operator
import math

class SC:

  def __init__(self, configs):
    self.configs = configs

    self.top_layer = []

    self.atoms = {}
    self.atom_per_position = {}
    self.atom_type = {}

    self.neighborhood = {}

  def calculate(self):
    i = j = -1
    # deltas = [[0, 0], [0, 1], [1, 0], [1, 1]]

    for row in self.configs['cells']:
      j = -1
      i += 1

      for cell in row:
        j += 1 #Cell i,j
        point = [i, j]

        if cell == 1:
          self.top_layer.append(tuple(point))
          # for delta in deltas:
          #   atom = tuple(map(operator.add, point, delta))
          #   self.top_layer.append(atom)


    # Remove duplicates
    self.top_layer = sorted(set(self.top_layer))

    # Add Z position to atoms
    atom_id = -1

    for z in xrange(self.configs['layers']):
      for atom in self.top_layer:
        atom += z, # add Z position

        atom_id += 1 #increment atom_id
        atom_key = "_".join(str(x) for x in atom)

        self.atoms[str(atom_id)] = atom
        self.atom_per_position[atom_key] = atom_id
        self.atom_type[atom_key] = 'vertex'

    self.find_neighborhood()

  def find_neighborhood(self):
    deltas = [[-1,0,0], [1,0,0], [0,-1,0], [0,1,0],[0,0,-1],[0,0,1]]

    for atom_id, atom in self.atoms.iteritems():
      neighbors = []
      for delta in deltas:
        neighbor = tuple(map(operator.add, atom, delta))
        neighbor_key = "_".join(str(x) for x in neighbor)

        if neighbor_key in self.atom_per_position.keys():
          neighbors.append(self.atom_per_position[neighbor_key])

      self.neighborhood[atom_id] = neighbors


class BCC:

  def __init__(self, configs):
    self.configs = configs

    self.top_layer = []
    self.intermediate_layer = []

    self.atoms = {}
    self.atom_per_position = {}
    self.atom_type = {}

    self.neighborhood = {}

  def calculate(self):
    i = j = -1
    #deltas = [[0, 0], [0, 1], [1, 0], [1, 1]]
    cells = self.configs['cells']

    for row in cells:
      j = -1
      i += 1

      for cell in row:
        j += 1 #Cell i,j
        point = [i, j]

        if cell == 1:
          self.top_layer.append(tuple(point))

          try:
            if cells[i+1][j] == 1 and cells[i][j+1] == 1 and cells[i+1][j+1] == 1:
              self.intermediate_layer.append((i+0.5, j+0.5))
          except:
            pass
          # for delta in deltas:
          #   atom = tuple(map(operator.add, point, delta))
          #   self.top_layer.append(atom)


    # Remove duplicates
    self.top_layer = sorted(set(self.top_layer))

    # Add Z position to atoms
    atom_id = -1

    for z in xrange(int(math.ceil(float(self.configs['layers']) / 2))):
      for atom in self.top_layer:
        atom += z, # add Z position

        atom_id += 1 #increment atom_id
        atom_key = "_".join(str(x) for x in atom)

        self.atoms[atom_id] = atom
        self.atom_per_position[atom_key] = atom_id
        self.atom_type[atom_key] = 'vertex'

    for z in xrange(int(math.floor(float(self.configs['layers']) / 2))):
      for atom in self.intermediate_layer:
        atom += (z + 0.5), # add Z position

        atom_id += 1 #increment atom_id
        atom_key = "_".join(str(x) for x in atom)

        self.atoms[atom_id] = atom
        self.atom_per_position[atom_key] = atom_id
        self.atom_type[atom_key] = 'body'

    self.find_neighborhood()

  def find_neighborhood(self):
    deltas = [
    [0.5, 0.5, 0.5], [0.5, -0.5, 0.5], [-0.5, 0.5, 0.5], [-0.5, -0.5, 0.5],
    [0.5, 0.5, -0.5], [0.5, -0.5, -0.5], [-0.5, 0.5, -0.5], [-0.5, -0.5, -0.5]]

    for atom_id, atom in self.atoms.iteritems():
      neighbors = []
      for delta in deltas:
        neighbor = [int(x) if int(x) == x else x for x in tuple(map(operator.add, atom, delta))]

        neighbor_key = "_".join(str(x) for x in neighbor)

        if neighbor_key in self.atom_per_position.keys():
          neighbors.append(self.atom_per_position[neighbor_key])

      self.neighborhood[atom_id] = neighbors

class FCC:

  def __init__(self, configs):
    self.configs = configs

    self.top_vertex_layer = []
    self.top_face_layer = []
    self.intermediate_layer = []

    self.atoms = {}
    self.atom_per_position = {}
    self.atom_type = {}

    self.neighborhood = {}

  def calculate(self):
    i = j = -1
    # top_vertex_deltas = [[0, 0], [0, 1], [1, 0], [1, 1]]

    cells = self.configs['cells']

    for row in cells:
      j = -1
      i += 1

      for cell in row:
        j += 1 #Cell i,j
        point = [i, j]

        if cell == 1:
          self.top_vertex_layer.append(tuple(point))
          # for delta in top_vertex_deltas:
          #   atom = tuple(map(operator.add, point, delta))
          #   self.top_vertex_layer.append(atom)

          try:
            if cells[i+1][j+1]:
              self.top_face_layer.append((i + 0.5, j + 0.5))
          except:
            pass

          try:
            if cells[i+1][j-1]:
              self.top_face_layer.append((i + 0.5, j - 0.5))
          except:
            pass

          try:
            if cells[i][j+1]:
              self.intermediate_layer.append((i, j + 0.5))
          except:
            pass

          try:
            if cells[i + 1][j]:
              self.intermediate_layer.append((i + 0.5, j))
          except:
            pass

    # Remove duplicates
    self.top_vertex_layer = sorted(set(self.top_vertex_layer))
    self.top_face_layer = sorted(set(self.top_face_layer))
    self.intermediate_layer = sorted(set(self.intermediate_layer))

    # Add Z position to atoms
    atom_id = -1

    for z in xrange(int(math.ceil(float(self.configs['layers']) / 2))):
      for atom in self.top_vertex_layer:
        atom += z, # add Z position

        atom_id += 1 #increment atom_id
        atom_key = "_".join(str(x) for x in atom)

        self.atoms[atom_id] = atom
        self.atom_per_position[atom_key] = atom_id
        self.atom_type[atom_key] = 'vertex'

      for atom in self.top_face_layer:
        atom += z, # add Z position

        atom_id += 1 #increment atom_id
        atom_key = "_".join(str(x) for x in atom)

        self.atoms[atom_id] = atom
        self.atom_per_position[atom_key] = atom_id
        self.atom_type[atom_key] = 'face'

    for z in xrange(int(math.floor(float(self.configs['layers']) / 2))):
      for atom in self.intermediate_layer:
        atom += (z + 0.5), # add Z position

        atom_id += 1 #increment atom_id
        atom_key = "_".join(str(x) for x in atom)

        self.atoms[atom_id] = atom
        self.atom_per_position[atom_key] = atom_id
        self.atom_type[atom_key] = 'face'

    self.find_neighborhood()

  def find_neighborhood(self):
    deltas = [
    [0, 0.5, 0.5], [0, 0.5, -0.5], [0, -0.5, 0.5], [0, -0.5, -0.5],
    [0.5, 0, 0.5], [0.5, 0, -0.5], [-0.5, 0, 0.5], [-0.5, 0, -0.5],
    [0.5, 0.5, 0], [0.5, -0.5, 0], [-0.5, 0.5, 0], [-0.5, -0.5, 0]]

    for atom_id, atom in self.atoms.iteritems():
      neighbors = []
      for delta in deltas:
        neighbor = [int(x) if int(x) == x else x for x in tuple(map(operator.add, atom, delta))]

        neighbor_key = "_".join(str(x) for x in neighbor)

        if neighbor_key in self.atom_per_position.keys():
          neighbors.append(self.atom_per_position[neighbor_key])

      self.neighborhood[atom_id] = neighbors