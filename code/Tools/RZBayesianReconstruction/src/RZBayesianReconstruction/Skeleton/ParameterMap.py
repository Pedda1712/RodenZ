class IParameterMap:
    def get_input_parameter_names(self) -> list[str]:
        return
    def get_output_parameter_names(self) -> list[str]:
        return
    def generate(self, input_array_name: str, output_array_name: str, input_parameters: list[str]) -> str:
        return

class SkeletonParameterMaps:
    maps: list[IParameterMap]
    point_names: list[str]
    def __init__(self, point_names: list[str]):
        self.maps = []
        self.point_names = point_names
    def generate(self, input_array_name: str, output_array_name: str, parameter_names: str):
        """Generate code to translate skeletal parameters into coordinate system parameters."""
        declared_input_parameters = sum([m.get_input_parameter_names() for m in self.maps], [])
        declared_output_parameters = sum([m.get_output_parameter_names() for m in self.maps], [])
        undeclared_output_parameters = [m for m in parameter_names if not m in declared_output_parameters]
        input_parameters = [m for m in declared_input_parameters if not m in parameter_names] + [m for m in parameter_names if m in declared_input_parameters or m in undeclared_output_parameters]

        code_lines = [pm.generate(input_array_name, output_array_name, input_parameters) for pm in self.maps] + [f"{op} = {input_array_name}[{input_parameters.index(op)}]" for op in undeclared_output_parameters]
        
        return code_lines
