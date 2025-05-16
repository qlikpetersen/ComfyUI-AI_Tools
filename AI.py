import io
import os
import openai
import base64
import numpy as np
from PIL import Image
from dotenv import load_dotenv
import json

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
                "model": (MODELS, {"default": "gpt-40-mini"}),
                "max_tokens": ("INT", {"default": 300}),
                "temperature": ("FLOAT", {"default": 0.5}),
                "system_prompt": ("STRING", {"default": ""}),
                "user_prompt": ("STRING", {"default": ""}),
            },
            "optional": {
                "attachments": ("JSON", {"forceInput": True}),
            },
        }

    CATEGORY = "openai"
    INPUT_IS_LIST = True
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("response",)
    FUNCTION = "queryAI"

    def queryAI(self, model, max_tokens, temperature, system_prompt, user_prompt, attachments=None):
        system_message = {"role": "system", "content": system_prompt[0]}
        user_message = {"role": "user", "content": [{"type": "text", "text": user_prompt[0]}]}

        print(type(attachments))
        print(attachments)

        if attachments is not None:
            if isinstance(attachments, list):
                for attachment in attachments:
                    user_message["content"].append(attachment)
            else:
                user_message["content"].append(attachments)

        # Set up OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        client = openai.OpenAI(api_key=api_key)

        # Make API call to OpenAI
        response = client.chat.completions.create(
            model=model[0],
            messages=[system_message, user_message],
            max_tokens=max_tokens[0],
            temperature=temperature[0],
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
                "image_in": ("IMAGE", {}),
            }
        }

    CATEGORY = "openai"
    RETURN_TYPES = ("JSON",)
    RETURN_NAMES = ("attachment",)
    FUNCTION = "image_attachment"

    def image_attachment(self, image_in):
        # Convert tensor to PIL Image
        pil_image = Image.fromarray(np.clip(255. * image_in.cpu().numpy().squeeze(), 0, 255).astype(np.uint8))

        # Convert PIL Image to base64
        buffered = io.BytesIO()
        pil_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

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
