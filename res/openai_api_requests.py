import openai
# import configparser


# Generate meme text using OpenAI API
def generate_meme_text(prompt):
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        temperature=0.7,
        max_tokens=300,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    out_text = response.choices[0].text.strip()
    out_text = out_text.replace('\n', '')
    out_text = out_text.replace('"', '')
    out_text = out_text.lstrip('.')
    return out_text


# Generate meme image using OpenAI API
def generate_meme_image_openai(text):
    response = openai.Image.create(
        prompt=text,
        n=1,
        size="1024x1024"
    )
    image_url = response['data'][0]['url']

    return image_url