import json
import torch
import numpy as np
from io import BytesIO
from PIL import ImageOps, Image


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


class SaveSpiderData:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "filename": ("STRING", {"forceInput": True}),
                "data": ("SPIDERDATA", {"forceInput": True}),
            },
        }

    CATEGORY = "utils"
    RETURN_TYPES = ()
    RETURN_NAMES = ()
    FUNCTION = "save_data"
    OUTPUT_NODE = True

    def save_data(self, filename, data):
        outputData = {}
        for page in data:
            if data[page]['url'] == page:
                outputData[page] = {
                    "url": data[page]['url'],
                    "data": data[page]['data'],
                    "screenshot": data[page]['screenshot'],
                    "links": {},
                    "rev_links": {},
                    "depths_found": data[page]['depths_found'],
                }
                for link in data[page]['links']:
                    outputData[page]['links'][link] = None
                for link in data[page]['rev_links']:
                    outputData[page]['rev_links'][link] = None
            else:
                outputData[page] = None
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(repr(outputData))
