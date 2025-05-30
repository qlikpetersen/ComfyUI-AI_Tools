import json


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
        if not isinstance(stringIn, list):
            stringIn = stringIn.strip()
            stringIn = stringIn.strip('```')
            stringIn = stringIn.strip('json')
            return json.dumps(stringIn)
        jsonOut = []
        for item in stringIn:
            item = item.strip()
            item = item.strip('```')
            item = item.strip('json')
            jsonOut.append(json.loads(item))
        return (jsonOut,)


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
            return json.dumps(JSON)
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
