import os
from PIL import Image, ImageDraw, ImageFont
import base64
import io

def create_icon():
    """Создает иконку для браузера"""
    # Создаем изображение 256x256 для иконки
    img = Image.new('RGBA', (256, 256), (30, 58, 95, 0))  # #1e3a5f фон
    draw = ImageDraw.Draw(img)
    
    # Рисуем глобус/планету
    center_x, center_y = 128, 128
    radius = 80
    
    # Основной круг планеты
    draw.ellipse([center_x - radius, center_y - radius, 
                  center_x + radius, center_y + radius], 
                 fill=(79, 195, 247, 255))  # #4fc3f7
    
    # Континенты (упрощенные)
    draw.ellipse([center_x - 30, center_y - 40, 
                  center_x + 20, center_y - 10], 
                 fill=(76, 175, 80, 255))  # зеленый
    
    draw.ellipse([center_x + 10, center_y - 20, 
                  center_x + 50, center_y + 30], 
                 fill=(76, 175, 80, 255))
    
    # Кольца вокруг планеты
    for i in range(3):
        r = radius + 20 + i * 15
        draw.ellipse([center_x - r, center_y - r//3, 
                      center_x + r, center_y + r//3], 
                     outline=(100, 181, 246, 100), width=2)
    
    # Название
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    text = "NEXUS"
    text_width = draw.textlength(text, font=font)
    text_x = (256 - text_width) // 2
    draw.text((text_x, 220), text, fill=(255, 255, 255, 255), font=font)
    
    # Сохраняем как ICO
    img.save('installer/icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    print("Created installer/icon.ico")

def create_wizard_image():
    """Создает большое изображение для мастера установки (164x314)"""
    img = Image.new('RGB', (164, 314), (30, 58, 95))  # #1e3a5f фон
    draw = ImageDraw.Draw(img)
    
    # Градиентный фон
    for y in range(314):
        color_value = 30 + (y * 50 // 314)
        draw.line([(0, y), (164, y)], fill=(color_value, 58 + y//10, 95 + y//8))
    
    # Логотип
    center_x, center_y = 82, 100
    radius = 40
    
    draw.ellipse([center_x - radius, center_y - radius, 
                  center_x + radius, center_y + radius], 
                 fill=(79, 195, 247))
    
    # Кольца
    for i in range(2):
        r = radius + 10 + i * 10
        draw.ellipse([center_x - r, center_y - r//3, 
                      center_x + r, center_y + r//3], 
                     outline=(100, 181, 246, 150), width=2)
    
    # Текст
    try:
        title_font = ImageFont.truetype("arial.ttf", 18)
        text_font = ImageFont.truetype("arial.ttf", 10)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    draw.text((82, 160), "NEXUS", fill=(255, 255, 255), font=title_font, anchor="mm")
    draw.text((82, 180), "Browser", fill=(179, 229, 252), font=text_font, anchor="mm")
    draw.text((82, 200), "Version 1.0.0", fill=(100, 181, 246), font=text_font, anchor="mm")
    
    # Нижняя декоративная линия
    draw.line([(20, 280), (144, 280)], fill=(79, 195, 247), width=2)
    
    img.save('installer/wizard_image.bmp', format='BMP')
    print("Created installer/wizard_image.bmp")

def create_wizard_small_image():
    """Создает маленькое изображение для мастера (55x58)"""
    img = Image.new('RGB', (55, 58), (30, 58, 95))
    draw = ImageDraw.Draw(img)
    
    # Простая версия логотипа
    center_x, center_y = 27, 29
    radius = 15
    
    draw.ellipse([center_x - radius, center_y - radius, 
                  center_x + radius, center_y + radius], 
                 fill=(79, 195, 247))
    
    # Кольцо
    draw.ellipse([center_x - radius - 5, center_y - (radius + 5)//3, 
                  center_x + radius + 5, center_y + (radius + 5)//3], 
                 outline=(100, 181, 246), width=1)
    
    img.save('installer/wizard_small.bmp', format='BMP')
    print("Created installer/wizard_small.bmp")

def create_banner():
    """Создает баннер (57x28)"""
    img = Image.new('RGB', (57, 28), (30, 58, 95))
    draw = ImageDraw.Draw(img)
    
    # Аббревиатура
    try:
        font = ImageFont.truetype("arial.ttf", 8)
    except:
        font = ImageFont.load_default()
    
    draw.text((28, 14), "NB", fill=(79, 195, 247), font=font, anchor="mm")
    
    img.save('installer/banner.bmp', format='BMP')
    print("Created installer/banner.bmp")

if __name__ == "__main__":
    # Создаем директорию installer если нет
    os.makedirs('installer', exist_ok=True)
    
    try:
        create_icon()
        create_wizard_image()
        create_wizard_small_image()
        create_banner()
        print("\nAll images created successfully!")
    except Exception as e:
        print(f"Error creating images: {e}")
        print("Please install Pillow: pip install Pillow")