import json


class AnyType(str):
    """A special class that is always equal in not equal comparisons. Credit to pythongosssss"""

    def __ne__(self, __value: object) -> bool:
        return False

    def __eq__(self, __value: object) -> bool:
        return True


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
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (True,)
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("STRING",)

    FUNCTION = "json2string"

    def json2string(self, JSON):
        textOut = []
        for item in JSON:
            textOut.append(json.dumps(item))
        return {"ui": {"text": textOut}, "result": (textOut,)}


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
    INPUT_IS_LIST = True
    OUTPUT_IS_LIST = (True,)
    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("JSON",)

    FUNCTION = "string2json"

    def string2json(self, stringIn):
        jsonOut = []
        for item in stringIn:
            item = item.strip('```')
            item = item.strip('json')
            jsonOut.append(json.loads(item))
        return {"ui": {"json": jsonOut}, "result": (jsonOut,)}


class CreateListJSON:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "instance-0": ("JSON", {"forceInput": True}),
            },
        }

    CATEGORY = "utils"
    OUTPUT_IS_LIST = (True,)
    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("list",)

    FUNCTION = "create_list"

    def create_list(self, **kwargs):
        list = []

        # Collect all inputs from kwargs dynamically
        for _k, v in kwargs.items():
            if v is not None:
                list.append(v)
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
