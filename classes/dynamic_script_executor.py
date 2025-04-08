import importlib.util
import os

class DynamicScriptExecutor:
    def __init__(self, __self, script_directory):
        self.__self = __self
        self.script_directory = script_directory

    async def execute(self, file_name, function_name):
        if not file_name.endswith('.py'):
            file_name += '.py'
        
        module_path = os.path.join(self.script_directory, file_name)
        module_name = os.path.splitext(file_name)[0]

        spec = importlib.util.spec_from_file_location(module_name, module_path)
        if spec is None:
            raise ImportError(f"Module {module_name} not found at {module_path}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        func = getattr(module, function_name, None)
        if func is None:
            raise AttributeError(f"Function {function_name} not found in module {module_name}")

        result = await func(self.__self)
        return result