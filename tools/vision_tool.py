import base64
from openai import OpenAI
import os

def analyze_image(uploaded_file):
    """
    Send an image to GPT-4.1-mini for analysis.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    bytes_data = uploaded_file.getvalue()
    base64_image = base64.b64encode(bytes_data).decode("utf-8")

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "What is shown in this image? If it is a historical vehicle or object from WW2, identify it specifically (e.g., 'Panzer II'). Provide a brief description."},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=300,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Could not analyze image: {str(e)}"