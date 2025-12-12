import base64
from openai import OpenAI
import os

def analyze_image(uploaded_file):
    """
    Stuurt een afbeelding naar GPT-4o voor analyse.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Encode afbeelding naar base64
    bytes_data = uploaded_file.getvalue()
    base64_image = base64.b64encode(bytes_data).decode('utf-8')

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Wat staat er op deze afbeelding? Als het een historisch voertuig of object uit WO2 is, identificeer het specifiek (bijv. 'Panzer II'). Geef een korte beschrijving."},
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
        return f"Kon afbeelding niet analyseren: {str(e)}"