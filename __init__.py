from .webInteraction import DoLogin, HttpRequest, SpiderCrawl
from .utils import Json2String, String2Json, CreateListString, CreateListJSON, PNGtoImage, SaveSpiderData, LoadSpiderData
from .AI import Query_OpenAI, Image_Attachment, JSON_Attachment, String_Attachment
from .runPython import RunPython


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
    "Query_OpenAI": Query_OpenAI,
    "Image_Attachment": Image_Attachment,
    "JSON_Attachment": JSON_Attachment,
    "String_Attachment": String_Attachment,
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
    "Query_OpenAI": "Query OpenAI",
    "Image_Attachment": "Image Attachment",
    "JSON_Attachment": "JSON Attachment",
    "String_Attachment": "String Attachment",
    "RunPython": "Run Python",
}

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
]

WEB_DIRECTORY = "./js"
