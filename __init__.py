"""
@author: kierdran
@title: AI_Tools
@nickname: ai_tools
@description: Tools for agentic testing
"""

from .webInteraction import DoLogin, HttpRequest
from .utils import Json2String, String2Json, CreateListString, CreateListJSON, PNGtoImage, TextMultiSave
from .AI import Query_OpenAI, Image_Attachment, JSON_Attachment, String_Attachment, RunPythonGriptapeToolNode
from .runPython import RunPython
from .spider import SpiderCrawl, SaveSpiderData, LoadSpiderData, SpiderSplit, IncludeInSpiderData, RemoveCircularReferences, FixLinksAndRevLinks

# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "DoLogin": DoLogin,
    "HttpRequest": HttpRequest,
    "SpiderCrawl": SpiderCrawl,

    "Json2String": Json2String,
    "String2Json": String2Json,
    "CreateListString": CreateListString,
    "CreateListJSON": CreateListJSON,
    "PNGtoImage": PNGtoImage,
    "SaveSpiderData": SaveSpiderData,
    "LoadSpiderData": LoadSpiderData,
    "SpiderSplit": SpiderSplit,
    "IncludeInSpiderData": IncludeInSpiderData,
    "RemoveCircularReferences": RemoveCircularReferences,
    "FixLinksAndRevLinks": FixLinksAndRevLinks,
    "TextMultiSave": TextMultiSave,

    "Query_OpenAI": Query_OpenAI,
    "Image_Attachment": Image_Attachment,
    "JSON_Attachment": JSON_Attachment,
    "String_Attachment": String_Attachment,
    "RunPythonGriptapeTool": RunPythonGriptapeToolNode,

    "RunPython": RunPython,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "DoLogin": "Login Webpage",
    "HttpRequest": "HTTP Request",
    "SpiderCrawl": "Spider Crawl",

    "Json2String": "Json to String",
    "String2Json": "String to Json",
    "CreateListString": "CreateList(String)",
    "CreateListJSON": "CreateList(JSON)",
    "PNGtoImage": "PNG to Image",
    "SaveSpiderData": "Save Spider Data",
    "LoadSpiderData": "Load Spider Data",
    "SpiderSplit": "Spider Split",
    "IncludeInSpiderData": "Include in Spider Data",
    "RemoveCircularReferences": "Remove Circular References",
    "FixLinksAndRevLinks": "Fix Links and Rev Links",
    "TextMultiSave": "Text Multi Save",

    "Query_OpenAI": "Query OpenAI",
    "Image_Attachment": "Image Attachment",
    "JSON_Attachment": "JSON Attachment",
    "String_Attachment": "String Attachment",
    "RunPythonGriptapeTool": "Run Python Griptape Tool",

    "RunPython": "Run Python",
}

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]

WEB_DIRECTORY = "./js"
