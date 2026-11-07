import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from google import genai

TELEGRAM_TOKEN = "9168733991:AAGhGE5LFUxkeM0ARkWDbvClKb1A4NlWzEI"
GEMINI_API_KEY = "AQ.Ab8RN6IcuGDEqwzpHKBcvshB8DzLZLAgo3APNmpNe-3PjLvQPA"

# دروستکردنی پەیوەندی بە API بە شێوازی فەرمی
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
        config=dict(
            system_instruction=SYSTEM_PROMPT
        )
    )
    return response.text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سڵاو! من بۆتی زیرەکی Education BOT ـم.\n"
        "هەر پرسیارێکت هەیە سەبارەت بە کۆلێژ، لێرەدا دەتوانیت لێم بپرسیت."
    )

async def reply_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    print(f"نامە هات: {user_text}")
    
    # دۆخی نووسین نیشان دەدات
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    
    try:
        # ئەنجامدانی پرۆسەکە لەسەر ڕێڕەوی جیاواز تا بۆتەکە لە کار نەکەوێت
        reply_text = await asyncio.to_thread(get_gemini_reply, user_text)
        await update.message.reply_text(reply_text)
        print("وەڵامەکە نێردرا!")
    except Exception as e:
        print(f"هەڵە: {e}")
        await update.message.reply_text("ببورە، کێشەیەک لە وەرگرتنی وەڵامدا هەیە.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), reply_message))

    print("بۆتەکە ئێستا کار دەکات...")
    app.run_polling()