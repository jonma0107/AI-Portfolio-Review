import asyncio
from io import BytesIO
from django.shortcuts import render
import boto3
from playwright.sync_api import sync_playwright
import requests
import json
from django.http import JsonResponse
from .models import Review
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, csrf_protect
import markdown
from dotenv import load_dotenv
from django.conf import settings
import os


# === Configuración S3 ===
AWS_ACCESS_KEY_ID = os.getenv('ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('REGION', default='us-east-1')
AWS_BUCKET_NAME = os.getenv('BUCKET_NAME')



# === Subir imagen a S3 ===
def upload_to_s3(image_data, file_name):
    s3 = boto3.client('s3',
                      aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                      region_name=AWS_REGION)

    s3.upload_fileobj(
        BytesIO(image_data),
        AWS_BUCKET_NAME,
        file_name,
        ExtraArgs={'ContentType': 'image/png'}
    )
    url = f"https://{AWS_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{file_name}"
    print("Imagen subida a:", url)
    return url


# === Tomar screenshot con Playwright ===
def take_screenshot_with_playwright(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        screenshot = page.screenshot(full_page=True)
        browser.close()
        return screenshot

def get_openai_review(s3_url):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Take a good look at the image, it is a full screenshot of a portfolio website. "
                            "Analyse the image I have provided and give me a full detailed review of the portfolio website. "
                            "Everything from the good and bad, and also things to improve on. Go into details. "
                            "Do it in the Spanish language."
                        )
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": s3_url
                        }
                    }
                ]
            }
        ],
        "max_tokens": 500
    }

    response = requests.post(url, headers=headers, json=payload)

    print("Status code:", response.status_code)
    print("Response:", response.text)

    if response.status_code == 200:
        result = response.json()
        # Convertir el texto Markdown a HTML
        markdown_text = result["choices"][0]["message"]["content"]
        html_content = markdown.markdown(markdown_text, extensions=['extra', 'codehilite', 'toc'])
        return html_content
    else:
        return f"Error: {response.text}"


# @csrf_exempt
@csrf_protect
@require_http_methods(["POST"])
def submit_url(request):
    data = json.loads(request.body)
    domain = data.get('domain')

    if not domain.startswith("http"):
        domain = "https://" + domain

    # 1. Tomar screenshot
    screenshot_bytes = take_screenshot_with_playwright(domain)

    # 2. Subir a S3 y obtener URL pública
    file_name = f"screenshots/{domain.replace('https://', '').replace('.', '_')}.png"
    s3_url = upload_to_s3(screenshot_bytes, file_name)

    # 3. Obtener review desde OpenAI
    website_review = get_openai_review(s3_url)

    # 4. Guardar en base de datos
    new_review_object = Review.objects.create(
        site_url=domain,
        site_image_url=s3_url,
        feedback=website_review,
    )

    # 5. Enviar respuesta
    response_data = {
        'website_screenshot': s3_url,
        'website_review': website_review,
        'review_id': new_review_object.id,
    }

    return JsonResponse(response_data)


# === Vista principal de Django ===
def index(request):
    return render(request, 'index.html')
