import os
import json
import torch
import numpy as np
from io import BytesIO
from PIL import ImageOps, Image
import comfy.utils


class AnyType(str):
    """A special class that is always equal in not equal comparisons. Credit to pythongosssss"""

    def __ne__(self, __value: object) -> bool:
        return False


class String2Json:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "stringIn": ("STRING", {"forceInput": True}),
            },
        }

    CATEGORY = "utils/string"
    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("JSON",)
    FUNCTION = "string2json"

    def string2json(self, stringIn):
        jsonOut = []
        wasList = True
        if not isinstance(stringIn, list):
            wasList = False
            stringIn = [stringIn]
        for item in stringIn:
            item = item.strip()
            item = item.strip('```')
            item = item.strip('json')
            jsonOut.append(json.loads(item))
        if wasList:
            return (jsonOut,)
        else:
            # If the input was not a list, return a single JSON object
            return (jsonOut[0],) if jsonOut else None


class Json2String:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "JSON": ("JSON", {"forceInput": True}),
            },
        }

    CATEGORY = "utils/string"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)
    FUNCTION = "json2string"

    def json2string(self, JSON):
        if not isinstance(JSON, list):
            return (json.dumps(JSON),)
        textOut = []
        for item in JSON:
            textOut.append(json.dumps(item))
        return (textOut,)


class CreateListJSON:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "instance-0": ("JSON", {"forceInput": True}),
            },
        }

    CATEGORY = "utils"
    INPUT_IS_LIST = True
    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("list",)

    FUNCTION = "create_list"

    def create_list(self, **kwargs):
        list = []

        # Collect all inputs from kwargs dynamically
        for _k, v in kwargs.items():
            if v is not None:
                for item in v:
                    list.append(item)
        return (list,)


class CreateListString(CreateListJSON):
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "instance-0": ("STRING", {"forceInput": True}),
            },
        }
    RETURN_TYPES = ("STRING",)


class PNGtoImage:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("PNG",),
            },
        }

    CATEGORY = "utils/image"
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    FUNCTION = "png_to_image"

    def png_to_image(self, image):
        image = ImageOps.exif_transpose(Image.open(BytesIO(image))).convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        return (image,)


class TextMultiSave:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "directory": ("STRING", {"default": "./", "label": "Directory"}),
                "file_prefix": ("STRING", {"default": "TextFile", "label": "Filename Prefix"}),
                "concat": ("BOOLEAN", {"default": True, "label": "Concatenate Data"}),
                "data": ("STRING", {"forceInput": True}),
            },
        }

    CATEGORY = "utils"
    INPUT_IS_LIST = (False, True, True, False)
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("filename", "concatinated_data")
    FUNCTION = "save_data"
    OUTPUT_NODE = True

    def save_data(self, directory, file_prefix, concat, data):
        pbar = comfy.utils.ProgressBar(len(data))
        concatData = ""

        base_filename = os.path.join(directory[0], file_prefix[0])
        extension = "txt"

        filename = f"{base_filename}.{extension}"
        for i, page in enumerate(data):
            if concat[0]:
                if i == 0:
                    print(f"Saving page {i} to {filename}")
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(page)
                else:
                    print(f"Appending page {i} to {filename}")
                    with open(filename, 'a', encoding='utf-8') as f:
                        f.write("\n\n" + page)
            else:
                if len(file_prefix) > 1:
                    filename = os.path.join(directory[0], f"{file_prefix[i]}.{extension}")
                else:
                    filename = f"{base_filename}-{i+1}.{extension}"
                print(f"Saving page {i} to {filename}")
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(page)
            if i == 0:
                concatData = page
            else:
                concatData += "\n\n" + page
            pbar.update(i+1)

        return (filename, concatData)
