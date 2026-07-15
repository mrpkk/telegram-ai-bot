#!/bin/bash
# Скрипт для создания скриншотов для портфолио
# Требуется: wkhtmltoimage или chromium-browser

echo "📸 Создание скриншотов для портфолио..."

# Проверяем наличие инструментов
if command -v wkhtmltoimage &> /dev/null; then
    TOOL="wkhtmltoimage"
elif command -v chromium-browser &> /dev/null; then
    TOOL="chromium"
elif command -v google-chrome &> /dev/null; then
    TOOL="chrome"
else
    echo "❌ Установите wkhtmltoimage или chromium-browser"
    echo "   sudo apt install wkhtmltopdf"
    echo "   или"
    echo "   sudo apt install chromium-browser"
    exit 1
fi

echo "✅ Используем: $TOOL"

# Создаём папку для скриншотов
mkdir -p screenshots

# 1. Обложка
echo "📸 Создаём обложку..."
if [ "$TOOL" = "wkhtmltoimage" ]; then
    wkhtmltoimage --width 1200 --height 630 cover.html screenshots/cover.png
elif [ "$TOOL" = "chromium" ] || [ "$TOOL" = "chrome" ]; then
    $TOOL --headless --screenshot=screenshots/cover.png --window-size=1200,630 --disable-gpu file://$(pwd)/cover.html
fi

# 2. Админ-панель
echo "📸 Создаём скриншот админки..."
if [ "$TOOL" = "wkhtmltoimage" ]; then
    wkhtmltoimage --width 1200 --height 630 demo_admin.html screenshots/admin.png
elif [ "$TOOL" = "chromium" ] || [ "$TOOL" = "chrome" ]; then
    $TOOL --headless --screenshot=screenshots/admin.png --window-size=1200,630 --disable-gpu file://$(pwd)/demo_admin.html
fi

# 3. Чат
echo "📸 Создаём скриншот чата..."
if [ "$TOOL" = "wkhtmltoimage" ]; then
    wkhtmltoimage --width 1200 --height 630 demo_chat.html screenshots/chat.png
elif [ "$TOOL" = "chromium" ] || [ "$TOOL" = "chrome" ]; then
    $TOOL --headless --screenshot=screenshots/chat.png --window-size=1200,630 --disable-gpu file://$(pwd)/demo_chat.html
fi

echo ""
echo "✅ Скриншоты готовы!"
echo "📁 Папка: screenshots/"
echo ""
echo "Файлы:"
echo "  - cover.png (1200x630) — обложка для Kwork/FL.ru"
echo "  - admin.png (1200x630) — скриншот админ-панели"
echo "  - chat.png (1200x630) — скриншот диалога с ботом"
