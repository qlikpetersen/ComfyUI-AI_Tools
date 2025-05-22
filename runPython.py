import traceback
import numpy as np
from custom_nodes.anynode.nodes.any import AnyNode


class AnyType(str):
    """A special class that is always equal in not equal comparisons. Credit to pythongosssss"""

    def __ne__(self, __value: object) -> bool:
        return False


any_type = AnyType("*")


class RunPython(AnyNode):
    @classmethod
    def INPUT_TYPES(cls):  # pylint: disable = invalid-name, missing-function-docstring
        return {
            "required": {
                "script": ("STRING", {
                    "multiline": True,
                    "default": "",
                }),
            },
            "optional": {
                "any": (any_type,),
                "any2": (any_type,),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }
    CATEGORY = "utils"
    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ('any',)
    FUNCTION = "doit"

    def doit(self, script, any=None, any2=None, unique_id=None, extra_pnginfo=None):
        print(f"\nRUN-{unique_id}", any, any2, "\n")

        if script == "":
            return (any,)

        result = None
        # Generate a unique function name
        function_name = self.generate_function_name()

        if script.strip() == "":
            raise ValueError("You need to enter a script.")

        self.script = self.extract_imports(script)

        # Modify the script to use the unique function name
        modified_script = self.script.replace('def generated_function', f'def {function_name}')

        # Execute the stored script to define the unique function
        try:
            # Define a dictionary to store globals and locals,
            # updating it with imported libs from script and built-in functions
            globals_dict = {"__builtins__": __builtins__}
            self._prepare_globals(globals_dict)
            globals_dict.update({"np": np})
            locals_dict = {}
            self.safe_exec(modified_script, globals_dict, locals_dict)
        except Exception as e:
            print("--- Exception During Exec ---")
            raise e

        # Assuming the generated code defines a function named 'generated_function'
        if function_name in locals_dict:
            try:
                # Call the generated function and get the result
                result = locals_dict[function_name](any, input_data_2=any2)
                print(f"Function result: {result}")
            except Exception as e:
                print(f"Error calling the function: {e}")
                traceback.print_exc()
                raise e
        else:
            print(f"Function '{function_name}' not found in entered code.")

        return (result,)
