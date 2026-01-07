import base64
from io import BytesIO

from PIL import Image
from dotenv import load_dotenv

from clients.openai_client import OpenAIClient

load_dotenv()
DEFAULT_DIM = 768

def shrink_image(
        image_bytes: bytes, 
        new_width: int = DEFAULT_DIM, 
        new_height: int = DEFAULT_DIM
    ) -> bytes:
    img = Image.open(BytesIO(image_bytes))
    img.thumbnail((new_width, new_height))
    buf = BytesIO()
    img.save(buf, format="PNG", quality=80)
    return buf.getvalue()

openai_client = OpenAIClient()

def generate_caption(transcription: str, image_bytes: bytes):
    small_image = shrink_image(image_bytes)
    base64_image = base64.b64encode(small_image).decode('utf-8')

    messages = [
        {
            "role": "user",
            "content": [
                { "type": "input_text", "text": transcription },
                {
                    "type": "input_image",
                    "image_url": f"data:image/jpeg;base64,{base64_image}",
                },
            ],
        }
    ]

    return openai_client.chat(messages, "gpt-4.1-mini")