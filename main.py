from google import genai
from google.genai import types # type: ignore
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
import base64
import os
import time
import streamlit as st


# streamlit run .\Text2Img\main.py  <-- run streamlit app

st.title("Text to Image Generator")

# Input for query
input_query = st.text_input("Enter you query here.")

# input for image
input_image = st.file_uploader("upload an image to edit it", type=["png"])
if input_image is not None:
    st.image(input_image, caption="Uploaded Image", width=100)

button = st.button("Enter")


load_dotenv()
api = os.getenv(key="GEMINI_API_KEY")
client = genai.Client(api_key=api)


# show and save the image
def show_n_save(response):
    for part in response.candidates[0].content.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = Image.open(BytesIO((part.inline_data.data)))
            img_path = f"Text2Img/downloads/{time.ctime().replace(' ', '-').replace(':', '-')}.png"
            image.save(img_path)
            st.image(image, caption="Your Image", width=500)
            st.success(f"Image is saved at {img_path}")


# get response from the model here
def get_response(input_query, img):

    if img == None:
        contents = [f''' 'You are an image generator'
                    'Carefully read the user input query, and generate the image if you can else if more information is needed ask for it through text'
                    'Use a realistic or artistic style as specified by the user. If no style is provided, default to photorealistic rendering.'
                    'If image dimension is specified by user, then generate in that dimension else default dimension is 720 x 1080'
                    'Generate an image of {input_query}'
                    ''']

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=contents,
            config=types.GenerateContentConfig(
            response_modalities=['Text', 'Image']
            )
        )
        return response
    else:
        contents = f'''
                    'You are an image editor'
                    'Carefully read the user input query and the image provided, and edit the image if you can else if more information is needed ask for it through text'
                    '{input_query}'
                    '''

        response = client.models.generate_content(
            model="gemini-2.0-flash-exp-image-generation",
            contents=[
                contents,
                Image.open(img)
            ],
            config=types.GenerateContentConfig(
                response_modalities=['Text', 'Image']
            )
        )
        return response

if button:
    if input_image is not None:
        response = get_response(input_query, input_image)
    else:
        response = get_response(input_query, None)
    show_n_save(response)



