import traceback
import numpy as np
from .utils import AnyType
from custom_nodes.anynode.nodes.any import AnyNode
from attrs import define
from griptape.utils.decorators import activity
from griptape.artifacts import ErrorArtifact, ListArtifact
from griptape.tools import BaseTool


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

    def doit(self, script, any=None, any2=None, unique_id=None, extra_pnginfo=None):
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

    @classmethod
    def with_config(cls, description, schema, **kwargs):
        # Create a new activity with the given config
        # Returns a dynamically subclassed tool
        def new_activity(self, params: dict):
            # Minimal logic for demo; real code exec can go here
            # This example returns the params wrapped in a ListArtifact
            try:
                # your python code tool logic here, now uses params
                return ListArtifact([params])
            except Exception as e:
                return ErrorArtifact("Python code error: " + str(e))

        new_activity = activity(
            config={
                "description": description,
                "schema": schema,
            }
        )(new_activity)

        # Build a dynamic subclass so each instance gets its own activity
        subclass = type("DynamicRunPythonTool", (cls,), {"query": new_activity})
        return subclass(**kwargs)
