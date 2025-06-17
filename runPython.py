import traceback
import numpy as np
from .utils import AnyType
from custom_nodes.anynode.nodes.any import AnyNode
from attrs import define
from griptape.utils.decorators import activity
from griptape.artifacts import ErrorArtifact, ListArtifact, TextArtifact
from griptape.tools import BaseTool
from textwrap import dedent
from schema import Literal, Schema


class RunPython(AnyNode):
    @classmethod
    def INPUT_TYPES(cls):  # pylint: disable = invalid-name, missing-function-docstring
        return {
            "required": {
                "script": ("STRING", {
                    "multiline": True,
                    "default": "def generated_function(input_data_1=None, input_data_2=None):\n    return input_data_1\n",
                }),
            },
            "optional": {
                "any": (AnyType("*"),),
                "any2": (AnyType("*"),),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }
    CATEGORY = "utils"
    RETURN_TYPES = (AnyType("*"),)
    RETURN_NAMES = ('any',)
    FUNCTION = "doit"

    def doit(self, script, any=None, any2=None, unique_id=None, extra_pnginfo=None, params=None):
        print(f"\nRUN-{unique_id}", "\n")

        if script == "":
            return (any,)

        result = None
        function_name = self.generate_function_name()

        if script.strip() == "":
            raise ValueError("You need to enter a script.")

        self.script = self.extract_imports(script)
        modified_script = self.script.replace('def generated_function', f'def {function_name}')

        try:
            globals_dict = {"__builtins__": __builtins__}
            self._prepare_globals(globals_dict)
            globals_dict.update({"np": np})
            locals_dict = {}
            self.safe_exec(modified_script, globals_dict, locals_dict)
        except Exception as e:
            print("--- Exception During Exec ---")
            raise e

        if function_name in locals_dict:
            try:
                result = locals_dict[function_name](any, input_data_2=any2)
            except Exception as e:
                print(f"Error calling the function: {e}")
                traceback.print_exc()
                raise e
        else:
            print(f"Function '{function_name}' not found in entered code.")

        return (result,)


@define
class RunPythonTool(BaseTool):
    _dynamic_activity = None

    def __init__(self, off_prompt, description, schema, script, any=None, any2=None, *args, **kwargs):
        super().__init__(*args)
        self.off_prompt = off_prompt
        self.description = description
        self.schema = schema
        self.script = script
        self.any_input = any
        self.any2_input = any2
        print(f"RunPythonTool: {self.description}, {self.schema}, {self.script}")
        self.DynamicRunPythonTool = self.with_config(self.description, schema=self.schema, script=self.script, any=any, any2=any2)

    @classmethod
    def with_config(cls, description, script, schema=None, any=None, any2=None):

        def new_activity(self, params: dict):
            """
            Run Supplied Python code with provided parameters.
            :param params["script"]: The Python code to execute.
            :param params["any"]: Optional additional input data to python script.
            :param params["any2"]: Optional second input data to python script.
            """
            try:
                run_python = RunPython()
                result_tuple = run_python.doit(script, any=any, any2=params, params=params)
                return TextArtifact(repr(result_tuple[0]))
            except Exception as e:
                return ErrorArtifact("Python code error: " + str(e))

        cls.new_activity = activity(
            config={
                "description": description,
                "schema": schema,
            }
        )(new_activity)

        # Build a dynamic subclass so each instance gets its own activity
        subclass = type("DynamicRunPythonTool", (cls,), {"query": new_activity})
        return subclass
