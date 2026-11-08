import asyncio
import os
from aiohttp import web
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

TELEGRAM_TOKEN = "9168733991:AAGhGE5LFUxkeM0ARkWDbvClKb1A4NlWzEI"
GEMINI_API_KEY = "AQ.Ab8RN6IcuGDEqwzpHKBcvshB8DzLZLAgo3APNmpNe-3PjLvQPA"

client = genai.Client(api_key=GEMINI_API_KEY)

SYSTEM_PROMPT = """
تۆ یارمەتیدەرێکی زیرەکی کۆلێژیت بە ناوی Education BOT.
وەڵامی قوتابیان بە زمانی کوردی (سۆرانی) بدەرەوە، زۆر ڕێزدار، دۆستانە و کورت و پوخت.

ئەم زانیارییانەی خوارەوە بەکاربهێنە بۆ وەڵامەکانت:
١. دەوامی فەرمی: یەکشەممە تا پێنجشەممە لە کاتژمێر ٨:٣٠ی بەیانی تا ١:٣٠ی پاشنیوەڕۆ.
٢. بەشەکان: بایۆلۆجی، فیزیا، کیمیا، ماتماتیک، پەروەردەی کوردی.
٣. پشتگیری خوێندن: هۆبەی تۆماری کۆلێژ (نهۆمی یەکەم). پێداویستی: وێنەیەکی ڕەنگاوڕەنگ و کارتی نیشتمانی یان پێناس.
٤. تاقیکردنەوەکان: لە مانگی پێنج بەڕێوەدەچێت و خشتە لە کەناڵی فەرمی ڕادەگەیەنرێت.
٥. ئەگەر پرسیارێک پەیوەندی بە کۆلێژەوە نەبوو، بە ڕێزەوە داوای لێبکە کە تەنها پرسیاری پەیوەندیدار بە کۆلێژ بکات.
٦. هەر زانیارییەکت نەزانی، ڕێنماییان بکە سەردانی هۆبەی تۆماری کۆلێژ بکەن.
"""

def get_gemini_reply(prompt_text):
    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt_text,
        config=dict(system_instruction=SYSTEM_PROMPT)
    )
    return response.text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سڵاو! من بۆتی زیرەکی Education BOT ـم.\n"
        "هەر پرسیارێکت هەیە سەبارەت بە کۆلێژ، لێرەدا دەتوانیت لێم بپرسیت."
    )

async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        reply_text = await asyncio.to_thread(get_gemini_reply, user_text)
        await update.message.reply_text(reply_text)
    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("ببورە، کێشەیەک لە وەرگرتنی وەڵامدا هەیە.")

async def handle_ping(request):
    return web.Response(text="Bot is running!")

async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply_message))

    # بەستنەوەی وێب سێرڤەر بۆ ئەوەی Render بە خۆڕایی قبووڵی بکات
    server = web.Application()
    server.router.add_get('/', handle_ping)
    runner = web.AppRunner(server)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

    async with app:
        await app.start()
        await app.updater.start_polling()
        print("بۆتەکە ئێستا کار دەکات...")
        while True:
            await asyncio.sleep(3600)

if __name__ == '__main__':
    asyncio.run(main())