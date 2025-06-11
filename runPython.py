import traceback
import numpy as np
from .utils import AnyType
from custom_nodes.anynode.nodes.any import AnyNode
from attrs import Factory, define, field
from schema import Literal, Schema
from griptape.artifacts import ErrorArtifact, ListArtifact
from griptape.chunkers import TextChunker
from griptape.loaders import WebLoader
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


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
    web_loader: WebLoader = field(default=Factory(lambda: WebLoader()), kw_only=True)
    text_chunker: TextChunker = field(default=Factory(lambda: TextChunker(max_tokens=400)), kw_only=True)

    @activity(
        config={
            "description": "Can be used to browse a web page and load its content",
            "schema": Schema({Literal("url", description="Valid HTTP URL"): str}),
        },
    )
    def get_content(self, params: dict) -> ListArtifact | ErrorArtifact:
        url = params["values"]["url"]

        try:
            result = self.web_loader.load(url)
            chunks = self.text_chunker.chunk(result)

            return ListArtifact(chunks)
        except Exception as e:
            return ErrorArtifact("Error getting page content: " + str(e))
