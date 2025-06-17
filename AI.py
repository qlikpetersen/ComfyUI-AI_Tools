import os
import openai
import base64
import json
import numpy as np
from io import BytesIO
from PIL import Image, ImageOps
from dotenv import load_dotenv
from .utils import AnyType
from .runPython import RunPythonTool

load_dotenv()
MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
    "chatgpt-4o-latest",
    "gpt-4-turbo"
]


class Query_OpenAI:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "base_url": ("STRING", {"default": "https://api.openai.com/v1"}),
                "model": (MODELS, {"default": "gpt-4o-mini"}),
                "max_tokens": ("INT", {"default": 16384, "min": 1, "max": 1100000000}),
                "temperature": ("FLOAT", {"default": 0.5}),
                "system_prompt": ("STRING", {"default": ""}),
                "user_prompt": ("STRING", {"default": ""}),
            },
            "optional": {
                "attachments": ("JSON", {"forceInput": True}),
            },
        }

    CATEGORY = "openai"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("response",)
    FUNCTION = "queryAI"

    def queryAI(self, base_url, model, max_tokens, temperature, system_prompt, user_prompt, attachments=None):
        system_message = {"role": "system", "content": system_prompt}
        user_message = {"role": "user", "content": [{"type": "text", "text": user_prompt}]}

        print(type(attachments))
        # print(attachments)

        if attachments is not None:
            if isinstance(attachments, list):
                for attachment in attachments:
                    user_message["content"].append(attachment)
            else:
                user_message["content"].append(attachments)

        # Set up OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        client = openai.OpenAI(api_key=api_key, base_url=base_url)

        # Make API call to OpenAI
        response = client.chat.completions.create(
            model=model,
            messages=[system_message, user_message],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        if response.choices[0].message.content is None:
            raise ValueError("No content in response")

        # Extract and return the caption
        text_out = response.choices[0].message.content.strip()
        return (text_out,)


class Image_Attachment:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_in": ("IMAGE|PNGIMAGE", {}),
            }
        }

    CATEGORY = "openai"
    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("attachment",)
    FUNCTION = "image_attachment"

    def image_attachment(self, image_in):
        if isinstance(image_in, bytes):
            if not image_in.startswith(b'\x89PNG'):
                # If the input is not PNG byte string, convert it
                pil_image = ImageOps.exif_transpose(Image.open(BytesIO(image_in))).convert("RGB")
                buffered = BytesIO()
                pil_image.save(buffered, format="PNG")
                image_in = buffered.getvalue()
        else:
            # Convert tensor to PIL Image
            pil_image = Image.fromarray(np.clip(255. * image_in.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))
            # Convert PIL Image to PNG bytes
            buffered = BytesIO()
            pil_image.save(buffered, format="PNG")
            image_in = buffered.getvalue()
        img_str = base64.b64encode(image_in).decode("utf-8")

        jsonOut = {
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{img_str}"}
        }

        return {"ui": {"json": jsonOut}, "result": (jsonOut,)}


class JSON_Attachment:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "JSON_in": ("JSON", {"forceInput": True}),
            }
        }

    CATEGORY = "openai"
    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("attachment",)
    FUNCTION = "json_attachment"

    def json_attachment(self, JSON_in):
        jsonOut = {
            "type": "text",
            "text": f"Here is some JSON content:\n{json.dumps(JSON_in)}"
        }

        return {"ui": {"json": jsonOut}, "result": (jsonOut,)}


class String_Attachment:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text_in": ("STRING", {"forceInput": True}),
                "text_type": (["text", "markdown", "HTML", "JSON"], {"default": "text"}),
            },
            "optional": {
                "identifier": ("STRING", {"forceInput": True}),
            },
        }

    CATEGORY = "openai"
    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("attachment",)
    FUNCTION = "string_attachment"

    def string_attachment(self, text_in, text_type, identifier=None):
        extraText = ""
        if identifier is not None:
            extraText = f" from {identifier}"
        jsonOut = {
            "type": "text",
            "text": f"Here is some {text_type} content{extraText}:\n{text_in}"
        }

        return {"ui": {"json": jsonOut}, "result": (jsonOut,)}


class RunPythonGriptapeToolNode:
    """
    Griptape Tool to query Spider info
    """
    DESCRIPTION = "Griptape runPython."

    @classmethod
    def INPUT_TYPES(cls):  # pylint: disable = invalid-name, missing-function-docstring
        return {
            "required": {
                "off_prompt": (
                    "BOOLEAN",
                    {
                        "default": False,
                        "label_on": "True (Keep output private)",
                        "label_off": "False (Provide output to LLM)",
                    },
                ),
                "description": ("STRING", {"default": "Dynamic Python Tool"}),
                "llmQuery": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": '{"url": ("Valid HTTP URL",str)}',
                        "tooltip": 'Dictionary of tupples for what the LLM is to send: "name": ("description",type)\n  Can use Or() in type\nEx:\n[\n    "query": ("A natural language search query",str),\n    "content": (\n        None,\n        Or(\n            str,\n            [\n                ("memory_name",str),\n                ("artifact_namespace",str)\n            ]\n        )\n    )\n}'
                    },
                ),
                "script": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "def generated_function(input_data_1=None, input_data_2=None, llmQueries=None):\n\n    return input_data_1\n",
                    }
                ),
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

    CATEGORY = "openai"
    RETURN_TYPES = ("TOOL_LIST",)
    RETURN_NAMES = ("TOOL",)
    FUNCTION = "runIt"

    def parse_llm_query(self, llm_query):
        # default: '[("url": "Valid HTTP URL",str)]'
        # supports a dict of tuples: {name: (description, type)}
        # types are python types (str, int, etc) or Or(...)
        import ast
        from schema import Literal, Schema

        #params = ast.literal_eval(llm_query)
        params = eval(llm_query)
        schema_args = {}
        for name in params:
            desc, typ = params[name]
            schema_args[Literal(name, description=desc)] = typ
        return Schema(schema_args)

    def runIt(self, description, llmQuery, **kwargs):
        schema = self.parse_llm_query(llmQuery)
        tool = RunPythonTool(description=description, schema=schema, **kwargs)
        #tool = RunPythonTool.with_config(description=description, schema=schema, **kwargs)
        return ([tool],)
