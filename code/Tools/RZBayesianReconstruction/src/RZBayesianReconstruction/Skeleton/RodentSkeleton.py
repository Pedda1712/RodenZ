import numpy as np
from .ParameterMap import SkeletonParameterMaps

"""
Converting skeletal definitions into trees of local coordinate systems.
"""

class ISkeletonNode:
    """Base Class for a skeleton node."""
    def __init__(self, my_index: int, absolute_points: np.ndarray, connections: list[tuple[int, int]]):
        return
    def from_absolute_coordinates(self, absolute_points: list[np.ndarray]) -> any:
        return
    def reassemble(self) -> list[tuple[int, np.ndarray]]:
        return
    def parameters(self, l: list[any]):
        return
    def get_parameters(self) -> list[any]:
        return
    def compile_reassembly(self) -> tuple[str, list[tuple[int, str]], list[tuple[int, list[str]]]]:
        compiled_children = [c.compile_reassembly() for c in self.children]
        code_to_now = sum([cc[0] for cc in compiled_children], [])
        variable_names_children = sum([cc[1] for cc in compiled_children], [])
        parameter_names_children = sum([cc[2] for cc in compiled_children], [])
        return code_to_now, variable_names_children, parameter_names_children

class RelativeCartesianNode(ISkeletonNode):
    """A simple relative coordinate system with only offset (no rotation)."""
    
    index: int
    children: list[ISkeletonNode] # children coordinate systems
    position: np.ndarray
    relevant_connections: list[tuple[int, int]]
    def __init__(self, my_index: int, connections: list[tuple[int, int]], children_constructor):
        self.index = my_index
        self.relevant_connections = [c for c in connections if c[0] == my_index]
        self.children = [
            children_constructor(
                connection[1],
                connections,
                children_constructor
            )
            for connection in self.relevant_connections
        ]
    def from_absolute_coordinates(self, absolute_points: list[np.ndarray]):
        self.position = absolute_points[self.index]
        absolute_points = [a - self.position for a in absolute_points]
        for c in self.children:
            c.from_absolute_coordinates(absolute_points)
        return self
    def reassemble(self):
        return [(self.index, self.position)] + [(e[0], e[1] + self.position) for c in self.children for e in c.reassemble()]
    def compile_reassembly(self) -> tuple[str, list[str]]:
        return "", []
    def parameters(self, parameters: list[any]):
        for c in self.children:
            c.parameters(parameters)
        self.position = parameters[self.index]
    def get_parameters(self):
        dicts = [c.get_parameters() for c in self.children]
        mine  = {
            self.index: self.position
        }
        for d in dicts:
            mine = mine | d
        return mine
    def compile_reassembly(self) -> tuple[str, list[str], list[tuple[int, list[str]]]]:
        code_to_now, children_variable_names, method_parameters = super().compile_reassembly()
        var_names = {
            "x": f"_{self.index}_x",
            "y": f"_{self.index}_y",
            "z": f"_{self.index}_z"
        }
        _code = [
            f"_t{self.index} = np.array([{var_names['x']}, {var_names['y']}, {var_names['z']}])"
        ]
        transformed_var_names = [(v[0], f"_{self.index}_{v[1]}") for v in children_variable_names] + [(self.index, f"_{self.index}_o")]
        _code.extend([f"{transformed[1]} = {_in[1]} + _t{self.index}" for transformed, _in in zip(transformed_var_names, children_variable_names + [(self.index, "np.zeros(3)")])])
        code_to_now.extend(_code)
        method_parameters.append((self.index, list(var_names.values())))
        return code_to_now, transformed_var_names, method_parameters

class RodentSkeleton():
    root: RelativeCartesianNode
    def __init__(self, start_index: int, n_points: int, connections: list[tuple[int, int]]):
        self.start_index = start_index
        self.connections = connections
        self.root = RelativeCartesianNode(start_index, connections, RelativeCartesianNode)
        self.n_points = n_points

    def to_absolute_coordinates(self, parameters):
        self.root.parameters(parameters)
        l = self.root.reassemble()
        o = np.zeros((self.n_points, 3))
        for index, c in l:
            o[index, :] = c
        return o

    def from_absolute_coordinates(self, absolute_points):
        return self.root.from_absolute_coordinates(absolute_points).get_parameters()

    def compile(self, parameter_maps: SkeletonParameterMaps) -> tuple[str, str]:
        """
        Generate a python function that takes in skeleton parameters
        and outputs absolute world positions for each keypoint in order
        of node indices.

        Return
        ------
        code : str
          code for a python function as described above, can be eval'd
        function_name : str
          the name of the function, can be eval'd after code to obtain a callable
        """
        code_list, variable_names, parameters = self.root.compile_reassembly()

        ordered_parameters = [[]] * len(parameters)
        for p in parameters:
            ordered_parameters[p[0]] = p[1]
        ordered_parameters = sum(ordered_parameters, [])

        premap = [f"    {c}" for c in parameter_maps.generate("arr", "outputs", ordered_parameters)]

        ordered_variable_names = [[]] * len(variable_names)
        for v in variable_names:
            ordered_variable_names[v[0]] = v[1]

        code = f"def _skeleton_relative_to_absolute(arr):\n" + "\n".join(premap) + "\n" + "\n".join([f"    {c}" for c in code_list]) + f"\n    return np.concatenate(({', '.join(ordered_variable_names)}))"

        return code, "_skeleton_relative_to_absolute"
