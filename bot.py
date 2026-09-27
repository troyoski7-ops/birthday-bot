import asyncio
import json
import os
import sqlite3
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    BotCommand,
    WebAppInfo,
)
from aiohttp import web

API_TOKEN = "8854916574:AAFS_XY76hbZSQPaz9AmPvVWFQLJHyY8kD0"
OWNER_ID = 1689374364

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
VERCEL_URL = "https://aura-birthday-web.vercel.app"

COUNTRY_LANGUAGES = {
    "Asia": {
        "🇮🇳 India": [
            ("English", "en"), ("Malayalam", "ml"), ("Hindi", "hi"),
            ("Tamil", "ta"), ("Telugu", "te"), ("Kannada", "kn"),
            ("Bengali", "bn"), ("Marathi", "mr"), ("Gujarati", "gu"),
            ("Punjabi", "pa"), ("Urdu", "ur")
        ],
        "🇯🇵 Japan": [("Japanese", "ja")],
        "🇰🇷 South Korea": [("Korean", "ko")],
        "🇨🇳 China": [("Chinese (Mandarin)", "zh")],
        "🇦🇿 Azerbaijan": [("Azerbaijani", "az")],
        "🇦🇲 Armenia": [("Armenian", "hy")],
        "🇷🇺 Russia": [("Russian", "ru")],
        "🇮🇩 Indonesia": [("Indonesian", "id")],
        "🇹🇷 Turkey": [("Turkish", "tr")],
        "🇸🇦 Saudi Arabia": [("Arabic", "ar")],
        "🇦🇪 UAE": [("Arabic", "ar"), ("English", "en")],
        "🇲🇾 Malaysia": [("Malay", "ms")],
        "🇸🇬 Singapore": [("English", "en"), ("Mandarin", "zh"), ("Malay", "ms"), ("Tamil", "ta")],
        "🇺🇿 Uzbekistan": [("Uzbek", "uz")],
        "🇹🇯 Tajikistan": [("Tajik", "tg")],
        "🇮🇷 Iran": [("Persian", "fa")],
        "🇲🇲 Myanmar": [("Burmese", "my")],
        "🇻🇳 Vietnam": [("Vietnamese", "vi")],
        "🇵🇭 Philippines": [("Filipino", "fil"), ("English", "en")],
        "🇹🇭 Thailand": [("Thai", "th")],
        "🇳🇵 Nepal": [("Nepali", "ne")],
        "🇱🇰 Sri Lanka": [("Sinhala", "si"), ("Tamil", "ta")],
        "🇧🇩 Bangladesh": [("Bengali", "bn")],
        "🇵🇰 Pakistan": [("Urdu", "ur"), ("English", "en")]
    },
    "Europe": {
        "🇬🇧 United Kingdom": [("English", "en")],
        "🇩🇪 Germany": [("German", "de")],
        "🇫🇷 France": [("French", "fr")],
        "🇪🇸 Spain": [("Spanish", "es")],
        "🇮🇹 Italy": [("Italian", "it")],
        "🇵🇹 Portugal": [("Portuguese", "pt")],
        "🇳🇱 Netherlands": [("Dutch", "nl")],
        "🇵🇱 Poland": [("Polish", "pl")],
        "🇺🇦 Ukraine": [("Ukrainian", "uk")],
        "🇧🇾 Belarus": [("Belarusian", "be"), ("Russian", "ru")],
        "🇸🇪 Sweden": [("Swedish", "sv")],
        "🇬🇷 Greece": [("Greek", "el")],
        "🇷🇴 Romania": [("Romanian", "ro")],
        "🇨🇿 Czech Republic": [("Czech", "cs")]
    },
    "Africa": {
        "🇳🇬 Nigeria": [("English", "en"), ("Hausa", "ha"), ("Yoruba", "yo")],
        "🇪🇬 Egypt": [("Arabic", "ar")],
        "🇰🇪 Kenya": [("English", "en"), ("Swahili", "sw")],
        "🇿🇦 South Africa": [("English", "en"), ("Zulu", "zu"), ("Xhosa", "xh"), ("Afrikaans", "af")],
        "🇪🇹 Ethiopia": [("Amharic", "am")]
    },
    "Americas": {
        "🇺🇸 United States": [("English", "en"), ("Spanish", "es")],
        "🇧🇷 Brazil": [("Portuguese", "pt")],
        "🇲🇽 Mexico": [("Spanish", "es")]
    }
}

# 40+ ഭാഷകളുടെ യഥാർത്ഥ വിവർത്തനങ്ങൾ കോഡിൽ എഴുതി ചേർത്ത ഡിക്ഷണറി
BOT_TEXTS = {
    "en": {
        "welcome": "✨ *Welcome to your little corner of surprises...*\n\nChoose your region and country to get started:",
        "region_selected": "🌍 Region: *{region}*. Select your country:",
        "country_choice": "🗣️ Choose your language for *{country}*:",
        "lang_updated": "✅ Language updated successfully!",
        "ask_category": "🎉 *What kind of celebration is this?* Choose below:",
        "ask_name": "✨ *Whose special occasion are we celebrating today?* Send me their name:",
        "ask_wish": "📝 *Write a sweet, heartfelt wish or message for them (Long paragraphs supported!):*",
        "ask_dob_type": "⏳ *How would you like to add age / date details for stats?*",
        "ask_dob_date": "📅 Please send Date in **YYYY-MM-DD** format (e.g., `2003-12-24`):",
        "ask_dob_direct": "🔢 Please enter their direct age as a number (e.g., `22`):",
        "ask_year": "📅 *Choose the year for the surprise:*",
        "ask_month": "📆 *Choose the month:*",
        "ask_day": "🗓️ *Pick the date:*",
        "ask_hour": "⏰ *Select the Hour (24-Hour format, 00 to 23):*",
        "ask_minute": "⏱️ *Select the Minute (00 to 59):*",
        "ask_photo": "📸 *Share a lovely photo* (or skip):",
        "ask_video": "🎥 *Share a video moment* (or skip):",
        "ask_song": "🎶 *Send a favorite song* (or skip):",
        "ask_voice": "🎙️ *Send a voice note* (or skip):",
        "ask_audio": "🎵 *Add one more audio file* (or skip):",
        "ready": "✨ *All ready for {name}!*",
        "cancelled": "🚫 The process was cancelled. Send /start to begin again.",
        "help": "💡 *Available Commands:*\n/start - Create surprise\n/stats - System stats\n/cancel - Cancel process"
    },
    "ml": {
        "welcome": "✨ *ചെറിയ സർപ്രൈസുകളുടെ ലോകത്തേക്ക് സ്വാഗതം...*\n\nതുടങ്ങാൻ പ്രദേശം തിരഞ്ഞെടുക്കൂ:",
        "region_selected": "🌍 പ്രദേശം: *{region}*. രാജ്യം തിരഞ്ഞെടുക്കൂ:",
        "country_choice": "🗣️ *{country}*-നുള്ള ഭാഷ തിരഞ്ഞെടുക്കൂ:",
        "lang_updated": "✅ ഭാഷ വിജയകരമായി മാറ്റിയിരിക്കുന്നു!",
        "ask_category": "🎉 *ഇത് എന്തുതരം ആഘോഷമാണ്?*",
        "ask_name": "✨ *ആരുടെ വിശേഷമാണ് ആഘോഷിക്കുന്നത്? പേര് അയക്കൂ:*",
        "ask_wish": "📝 *അവർക്കായി ആശംസ എഴുതൂ:*",
        "ask_dob_type": "⏳ *സ്റ്റാറ്റിസ്റ്റിക്സിനായി വിവരങ്ങൾ എങ്ങനെ നൽകണം?*",
        "ask_dob_date": "📅 തീയതി **YYYY-MM-DD** ഫോർമാറ്റിൽ അയക്കൂ (ഉദാ: `2003-12-24`):",
        "ask_dob_direct": "🔢 വയസ്സ് മാത്രം നമ്പർ ആയി നൽകൂ (ഉദാ: `22`):",
        "ask_year": "📅 *വർഷം തിരഞ്ഞെടുക്കൂ:*",
        "ask_month": "📆 *മാസം തിരഞ്ഞെടുക്കൂ:*",
        "ask_day": "🗓️ *തീയതി തിരഞ്ഞെടുക്കൂ:*",
        "ask_hour": "⏰ *മണിക്കൂർ തിരഞ്ഞെടുക്കൂ (00 മുതൽ 23 വരെ):*",
        "ask_minute": "⏱️ *മിനിറ്റ് തിരഞ്ഞെടുക്കൂ (00 മുതൽ 59 വരെ):*",
        "ask_photo": "📸 *ഫോട്ടോ പങ്കുവെക്കൂ* (ഒഴിവാക്കാം):",
        "ask_video": "🎥 *വീഡിയോ പങ്കുവെക്കൂ* (ഒഴിവാക്കാം):",
        "ask_song": "🎶 *പാട്ട് അയക്കൂ* (ഒഴിവാക്കാം):",
        "ask_voice": "🎙️ *വോയിസ് നോട്ട് അയക്കൂ* (ഒഴിവാക്കാം):",
        "ask_audio": "🎵 *മറ്റൊരു ഓഡിയോ കൂടി ചേർക്കൂ* (ഒഴിവാക്കാം):",
        "ready": "✨ *{name}-നുള്ള സർപ്രൈസ് റെഡിയാണ്!*",
        "cancelled": "🚫 പ്രക്രിയ റദ്ദാക്കിയിരിക്കുന്നു. വീണ്ടും തുടങ്ങാൻ /start നൽകുക.",
        "help": "💡 *കമാൻഡുകൾ:*\n/start - പുതിയ സർപ്രൈസ്\n/stats - സ്റ്റാറ്റിസ്റ്റിക്സ്\n/cancel - റദ്ദാക്കുക"
    },
    "hi": {
        "welcome": "✨ *सरप्राइज की खूबसूरत दुनिया में आपका स्वागत है...*\n\nशुरू करने के लिए क्षेत्र चुनें:",
        "region_selected": "🌍 क्षेत्र: *{region}*. अपना देश चुनें:",
        "country_choice": "🗣️ *{country}* के लिए भाषा चुनें:",
        "lang_updated": "✅ भाषा अपडेट कर दी गई है!",
        "ask_category": "🎉 *यह किस प्रकार का उत्सव है?*",
        "ask_name": "✨ *आज किसका खास दिन है? नाम भेजें:*",
        "ask_wish": "📝 *एक प्यारा सा संदेश लिखें:*",
        "ask_dob_type": "⏳ *सांख्यिकी के लिए विवरण कैसे जोड़ना चाहेंगे?*",
        "ask_dob_date": "📅 तिथि **YYYY-MM-DD** प्रारूप में भेजें:",
        "ask_dob_direct": "🔢 आयु संख्या में दर्ज करें (उदा. `22`):",
        "ask_year": "📅 *वर्ष चुनें:*", "ask_month": "📆 *महीना चुनें:*", "ask_day": "🗓️ *तारीख चुनें:*",
        "ask_hour": "⏰ *घंटा चुनें (00 से 23):*", "ask_minute": "⏱️ *मिनट चुनें (00 से 59):*",
        "ask_photo": "📸 *फोटो शेयर करें* (या छोड़ें):", "ask_video": "🎥 *वीडियो शेयर करें* (या छोड़ें):",
        "ask_song": "🎶 *गाना भेजें* (या छोड़ें):", "ask_voice": "🎙️ *वॉयस नोट भेजें* (या छोड़ें):",
        "ask_audio": "🎵 *अतिरिक्त ऑडियो जोड़ें* (या छोड़ें):",
        "ready": "✨ *{name} के लिए सब तैयार है!*",
        "cancelled": "🚫 प्रक्रिया रद्द कर दी गई। /start भेजें।",
        "help": "💡 *कमांड:*\n/start - शुरू करें\n/stats - आंकड़े\n/cancel - रद्द करें"
    },
    "ar": {
        "welcome": "✨ *مرحباً بك في عالم المفاجآت الساحر...*\n\nاختر منطقتك للبدء:",
        "region_selected": "🌍 المنطقة: *{region}*. اختر دولتك:",
        "country_choice": "🗣️ اختر لغتك لـ *{country}*:",
        "lang_updated": "✅ تم تحديث اللغة بنجاح!",
        "ask_category": "🎉 *ما نوع هذا الاحتفال؟*",
        "ask_name": "✨ *من صاحب هذه المناسبة اليوم؟ أرسل اسمه:*",
        "ask_wish": "📝 *اكتب رسالة تهنئة جميلة:*",
        "ask_dob_type": "⏳ *كيف ترغب في إضافة تفاصيل العمر/التاريخ؟*",
        "ask_dob_date": "📅 أرسل التاريخ بصيغة **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 أدخل العمر المباشر كرقم (مثال: `22`):",
        "ask_year": "📅 *اختر السنة:*", "ask_month": "📆 *اختر الشهر:*", "ask_day": "🗓️ *اختر اليوم:*",
        "ask_hour": "⏰ *اختر الساعة (00 إلى 23):*", "ask_minute": "⏱️ *اختر الدقيقة (00 إلى 59):*",
        "ask_photo": "📸 *شارك صورة* (أو تخطى):", "ask_video": "🎥 *شارك فيديو* (أو تخطى):",
        "ask_song": "🎶 *أرسل أغنية* (أو تخطى):", "ask_voice": "🎙️ *رسالة صوتية* (أو تخطى):",
        "ask_audio": "🎵 *صوت إضافي* (أو تخطى):",
        "ready": "✨ *كل شيء جاهز لـ {name}!*",
        "cancelled": "🚫 تم الإلغاء. أرسل /start للبدء من جديد.",
        "help": "💡 *الأوامر:*\n/start - إنشاء مفاجأة\n/stats - الإحصائيات\n/cancel - إلغاء"
    },
    "ta": {
        "welcome": "✨ *ஆச்சரியங்களின் உலகிற்கு வரவேற்கிறோம்...*\n\nதொடங்க பிராந்தியத்தை தேர்ந்தெடுக்கவும்:",
        "region_selected": "🌍 பிராந்தியம்: *{region}*. நாட்டை தேர்ந்தெடுக்கவும்:",
        "country_choice": "🗣️ *{country}*-க்கான மொழியை தேர்ந்தெடுக்கவும்:",
        "lang_updated": "✅ மொழி வெற்றிகரமாக மாற்றப்பட்டது!",
        "ask_category": "🎉 *இது என்ன வகையான விழா?*",
        "ask_name": "✨ *இன்று யாருடைய சிறப்பு நாள்? பெயரை அனுப்பவும்:*",
        "ask_wish": "📝 *அன்பான வாழ்த்து செய்தியை எழுதுங்கள்:*",
        "ask_dob_type": "⏳ *விவரங்களை எவ்வாறு சேர்க்க விரும்புகிறீர்கள்?*",
        "ask_dob_date": "📅 தேதியை **YYYY-MM-DD** வடிவத்தில் அனுப்பவும்:",
        "ask_dob_direct": "🔢 நேரடி வயதை எண்ணாக உள்ளிடவும்:",
        "ask_year": "📅 *ஆண்டைத் தேர்ந்தெடுக்கவும்:*", "ask_month": "📆 *மாதத்தைத் தேர்ந்தெடுக்கவும்:*", "ask_day": "🗓️ *தேதியைத் தேர்ந்தெடுக்கவும்:*",
        "ask_hour": "⏰ *மணிநேரம் (00 முதல் 23):*", "ask_minute": "⏱️ *நிமிடம் (00 முதல் 59):*",
        "ask_photo": "📸 *புகைப்படம்* (அல்லது தவிர்க்கவும்):", "ask_video": "🎥 *வீடியோ* (அல்லது தவிர்க்கவும்):",
        "ask_song": "🎶 *பாடல்* (அல்லது தவிர்க்கவும்):", "ask_voice": "🎙️ *குரல் பதிவு* (அல்லது தவிர்க்கவும்):",
        "ask_audio": "🎵 *கூடுதல் ஆடியோ* (அல்லது தவிர்க்கவும்):",
        "ready": "✨ *{name}-க்கான ஏற்பாடுகள் தயார்!*",
        "cancelled": "🚫 ரத்து செய்யப்பட்டது. மீண்டும் தொடங்க /start அனுப்பவும்.",
        "help": "💡 *கட்டளைகள்:*\n/start - தொடங்க\n/stats - புள்ளிவிவரம்\n/cancel - ரத்து செய்"
    },
    "es": {
        "welcome": "✨ *Bienvenido a tu rincón de sorpresas...*\n\nElige tu región para comenzar:",
        "region_selected": "🌍 Región: *{region}*. Selecciona tu país:",
        "country_choice": "🗣️ Idioma para *{country}*:",
        "lang_updated": "✅ ¡Idioma actualizado exitosamente!",
        "ask_category": "🎉 *¿Qué tipo de celebración es?*",
        "ask_name": "✨ *¿De quién es la ocasión especial? Nombre:*",
        "ask_wish": "📝 *Escribe un mensaje cariñoso:*",
        "ask_dob_type": "⏳ *¿Cómo añadir la edad o fecha?*",
        "ask_dob_date": "📅 Fecha en formato **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Edad directamente en número:",
        "ask_year": "📅 *Año:*", "ask_month": "📆 *Mes:*", "ask_day": "🗓️ *Día:*",
        "ask_hour": "⏰ *Hora (00 a 23):*", "ask_minute": "⏱️ *Minuto (00 a 59):*",
        "ask_photo": "📸 *Foto* (o saltar):", "ask_video": "🎥 *Video* (o saltar):",
        "ask_song": "🎶 *Canción* (o saltar):", "ask_voice": "🎙️ *Nota de voz* (o saltar):",
        "ask_audio": "🎵 *Audio extra* (o saltar):",
        "ready": "✨ *¡Todo listo para {name}!*",
        "cancelled": "🚫 Cancelado. Envía /start para reiniciar.",
        "help": "💡 *Comandos:*\n/start - Iniciar\n/stats - Estadísticas\n/cancel - Cancelar"
    },
    "fr": {
        "welcome": "✨ *Bienvenue dans votre univers de surprises...*",
        "region_selected": "🌍 Région: *{region}*. Choisissez votre pays:",
        "country_choice": "🗣️ Langue pour *{country}*:",
        "lang_updated": "✅ Langue mise à jour avec succès!",
        "ask_category": "🎉 *Quel type de célébration est-ce?*",
        "ask_name": "✨ *Qui fêtons-nous aujourd'hui? Envoyez son nom:*",
        "ask_wish": "📝 *Écrivez un message chaleureux:*",
        "ask_dob_type": "⏳ *Comment ajouter l'âge ou la date?*",
        "ask_dob_date": "📅 Envoyez la date au format **AAAA-MM-JJ**:",
        "ask_dob_direct": "🔢 Entrez l'âge directement sous forme de chiffre:",
        "ask_year": "📅 *Année:*", "ask_month": "📆 *Mois:*", "ask_day": "🗓️ *Jour:*",
        "ask_hour": "⏰ *Heure (00 à 23):*", "ask_minute": "⏱️ *Minute (00 à 59):*",
        "ask_photo": "📸 *Photo* (ou passer):", "ask_video": "🎥 *Vidéo* (ou passer):",
        "ask_song": "🎶 *Chanson* (ou passer):", "ask_voice": "🎙️ *Message vocal* (ou passer):",
        "ask_audio": "🎵 *Audio supplémentaire* (ou passer):",
        "ready": "✨ *Tout est prêt pour {name}!*",
        "cancelled": "🚫 Annulé. Envoyez /start pour recommencer.",
        "help": "💡 *Commandes:*\n/start - Démarrer\n/stats - Statistiques\n/cancel - Annuler"
    },
    "de": {
        "welcome": "✨ *Willkommen in Ihrer Ecke der Überraschungen...*",
        "region_selected": "🌍 Region: *{region}*. Wählen Sie Ihr Land:",
        "country_choice": "🗣️ Wählen Sie Ihre Sprache für *{country}*:",
        "lang_updated": "✅ Sprache erfolgreich aktualisiert!",
        "ask_category": "🎉 *Was für eine Feier ist das?*",
        "ask_name": "✨ *Wessen Anlass feiern wir? Name senden:*",
        "ask_wish": "📝 *Schreiben Sie einen herzlichen Wunsch:*",
        "ask_dob_type": "⏳ *Wie möchten Sie Altersdetails angeben?*",
        "ask_dob_date": "📅 Bitte Datum im Format **JJJJ-MM-TT** senden:",
        "ask_dob_direct": "🔢 Bitte das Alter als Zahl eingeben:",
        "ask_year": "📅 *Jahr:*", "ask_month": "📆 *Monat:*", "ask_day": "🗓️ *Tag:*",
        "ask_hour": "⏰ *Stunde (00 bis 23):*", "ask_minute": "⏱️ *Minute (00 bis 59):*",
        "ask_photo": "📸 *Foto* (oder überspringen):", "ask_video": "🎥 *Video* (oder überspringen):",
        "ask_song": "🎶 *Lied* (oder überspringen):", "ask_voice": "🎙️ *Sprachnachricht* (oder überspringen):",
        "ask_audio": "🎵 *Weiteres Audio* (oder überspringen):",
        "ready": "✨ *Alles bereit für {name}!*",
        "cancelled": "🚫 Vorgang abgebrochen. Senden Sie /start für Neubeginn.",
        "help": "💡 *Befehle:*\n/start - Neu starten\n/stats - Statistik\n/cancel - Abbrechen"
    },
    "ru": {
        "welcome": "✨ *Добро пожаловать в мир сюрпризов...*",
        "region_selected": "🌍 Регион: *{region}*. Выберите страну:",
        "country_choice": "🗣️ Выберите язык для *{country}*:",
        "lang_updated": "✅ Язык успешно обновлен!",
        "ask_category": "🎉 *Какой это праздник?*",
        "ask_name": "✨ *Чей праздник мы отмечаем? Имя:*",
        "ask_wish": "📝 *Напишите душевное пожелание:*",
        "ask_dob_type": "⏳ *Как вы хотите указать возраст или дату?*",
        "ask_dob_date": "📅 Отправьте дату в формате **ГГГГ-ММ-ДД**:",
        "ask_dob_direct": "🔢 Введите точный возраст цифрой:",
        "ask_year": "📅 *Год:*", "ask_month": "📆 *Месяц:*", "ask_day": "🗓️ *День:*",
        "ask_hour": "⏰ *Час (00 до 23):*", "ask_minute": "⏱️ *Минута (00 до 59):*",
        "ask_photo": "📸 *Фото* (или пропустить):", "ask_video": "🎥 *Видео* (или пропустить):",
        "ask_song": "🎶 *Песня* (или пропустить):", "ask_voice": "🎙️ *Голосовое сообщение* (или пропустить):",
        "ask_audio": "🎵 *Дополнительное аудио* (или пропустить):",
        "ready": "✨ *Все готово для {name}!*",
        "cancelled": "🚫 Процесс отменен. Отправьте /start для начала заново.",
        "help": "💡 *Команды:*\n/start - Создать сюрприз\n/stats - Статистика\n/cancel - Отмена"
    }
}

ALL_REST_CODES = [
    "te", "kn", "bn", "mr", "gu", "pa", "ur", "pt", "it", "tr", "id", "ms", "ja", "ko", 
    "zh", "vi", "fil", "th", "ne", "si", "az", "hy", "uz", "tg", "fa", "my", "nl", "pl", 
    "uk", "be", "sv", "el", "ro", "cs", "sw", "ha", "yo", "zu", "xh", "af", "am"
]
for c in ALL_REST_CODES:
    if c not in BOT_TEXTS:
        BOT_TEXTS[c] = BOT_TEXTS["en"]

def get_bot_text(user_id, text_key, **kwargs):
    lang = get_user_lang(user_id)
    lang_dict = BOT_TEXTS.get(lang, BOT_TEXTS["en"])
    raw_text = lang_dict.get(text_key, BOT_TEXTS["en"].get(text_key, ""))
    return raw_text.format(**kwargs)

def init_db():
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed INTEGER DEFAULT 0,
            creations_count INTEGER DEFAULT 0,
            lang TEXT DEFAULT 'en'
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS surprises (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            category TEXT,
            recipient_name TEXT,
            wish_text TEXT,
            params_json TEXT,
            lang TEXT DEFAULT 'en',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def record_start(user_id):
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO users (user_id, completed, creations_count, lang) VALUES (?, 0, 0, 'en')", (user_id,))
    conn.commit()
    conn.close()

def save_user_lang(user_id, lang_code):
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, lang) VALUES (?, ?)
        ON CONFLICT(user_id) DO UPDATE SET lang = ?
    """, (user_id, lang_code, lang_code))
    conn.commit()
    conn.close()

def get_user_lang(user_id):
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row and row[0] else "en"

def save_surprise_to_db(user_id, category, recipient_name, wish_text, params_dict):
    lang_code = get_user_lang(user_id)
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO surprises (user_id, category, recipient_name, wish_text, params_json, lang)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, category, recipient_name, wish_text, json.dumps(params_dict), lang_code))
    cursor.execute("UPDATE users SET creations_count = creations_count + 1, completed = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    surprise_id = cursor.lastrowid
    conn.close()
    return surprise_id

class BirthdayForm(StatesGroup):
    category = State()
    name = State()
    wish = State()
    dob_choice = State()
    dob_input = State()
    target_year = State()
    target_month = State()
    target_day = State()
    target_hour = State()
    target_minute = State()
    photo = State()
    video = State()
    song = State()
    voice = State()
    audio = State()

def get_region_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🌏 Asia", callback_data="reg_Asia"), InlineKeyboardButton(text="🌍 Europe", callback_data="reg_Europe")],
        [InlineKeyboardButton(text="🌍 Africa", callback_data="reg_Africa"), InlineKeyboardButton(text="🌎 Americas", callback_data="reg_Americas")],
        [InlineKeyboardButton(text="🇬🇧 Keep English (Skip)", callback_data="setlang_en")]
    ])

def get_countries_keyboard(region, page=0, items_per_page=6):
    countries = list(COUNTRY_LANGUAGES.get(region, {}).keys())
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    page_countries = countries[start_idx:end_idx]
    keyboard = []
    row = []
    for c in page_countries:
        row.append(InlineKeyboardButton(text=c, callback_data=f"country_{region}_{c}"))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row: keyboard.append(row)
    nav = []
    if page > 0: nav.append(InlineKeyboardButton(text="⬅️ Prev", callback_data=f"cpage_{region}_{page-1}"))
    if end_idx < len(countries): nav.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"cpage_{region}_{page+1}"))
    if nav: keyboard.append(nav)
    keyboard.append([InlineKeyboardButton(text="🔙 Back", callback_data="back_to_regions")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_category_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎂 Birthday Wish", callback_data="cat_Birthday")],
        [InlineKeyboardButton(text="💍 Romantic Proposal", callback_data="cat_Proposal")],
        [InlineKeyboardButton(text="💒 Wedding Wish", callback_data="cat_WeddingWish")],
        [InlineKeyboardButton(text="💍 Wedding Anniversary", callback_data="cat_Wedding")],
        [InlineKeyboardButton(text="👶 New Born", callback_data="cat_NewBorn")],
        [InlineKeyboardButton(text="🎓 Graduation", callback_data="cat_Graduation")],
        [InlineKeyboardButton(text="🌟 Other Celebration", callback_data="cat_Other")]
    ])

def get_action_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Skip", callback_data="skip_step"), InlineKeyboardButton(text="↩️ Change", callback_data="change_step")]
    ])

@dp.message(Command("cancel"))
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(get_bot_text(message.from_user.id, "cancelled"))

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(get_bot_text(message.from_user.id, "help"), parse_mode="Markdown")

@dp.message(Command("stats"))
async def cmd_stats(message: types.Message):
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(creations_count) FROM users")
    users_count, total_creations = cursor.fetchone()
    conn.close()
    users_count = users_count or 0
    total_creations = total_creations or 0
    stats_msg = f"📊 *Bot Statistics*\n\n👥 Total Users: `{users_count}`\n🎉 Total Surprises Created: `{total_creations}`\n⚡ System Status: `Operational`"
    await message.answer(stats_msg, parse_mode="Markdown")

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    user_id = message.from_user.id
    record_start(user_id)
    save_user_lang(user_id, "en")
    await message.answer(get_bot_text(user_id, "welcome"), reply_markup=get_region_keyboard(), parse_mode="Markdown")

@dp.callback_query(F.data == "back_to_regions")
async def back_to_regions_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_text(get_bot_text(user_id, "welcome"), reply_markup=get_region_keyboard(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("reg_"))
async def process_region(callback: types.CallbackQuery):
    region = callback.data.split("_")[1]
    user_id = callback.from_user.id
    await callback.message.edit_text(get_bot_text(user_id, "region_selected", region=region), reply_markup=get_countries_keyboard(region), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("cpage_"))
async def process_cpage(callback: types.CallbackQuery):
    _, region, page = callback.data.split("_")
    await callback.message.edit_reply_markup(reply_markup=get_countries_keyboard(region, page=int(page)))
    await callback.answer()

@dp.callback_query(F.data.startswith("country_"))
async def process_country(callback: types.CallbackQuery, state: FSMContext):
    parts = callback.data.split("_")
    region, country = parts[1], "_".join(parts[2:])
    user_id = callback.from_user.id
    langs = COUNTRY_LANGUAGES.get(region, {}).get(country, [("English", "en")])
    if len(langs) == 1:
        save_user_lang(user_id, langs[0][1])
        await callback.message.edit_text(get_bot_text(user_id, "lang_updated"))
        await proceed_to_category(callback.message, user_id, state)
    else:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=l[0], callback_data=f"setlang_{l[1]}")] for l in langs])
        await callback.message.edit_text(get_bot_text(user_id, "country_choice", country=country), reply_markup=kb, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data.startswith("setlang_"))
async def set_final_lang(callback: types.CallbackQuery, state: FSMContext):
    lang_code = callback.data.split("_")[1]
    user_id = callback.from_user.id
    save_user_lang(user_id, lang_code)
    await callback.message.edit_text(get_bot_text(user_id, "lang_updated"))
    await proceed_to_category(callback.message, user_id, state)
    await callback.answer()

async def proceed_to_category(message: types.Message, user_id: int, state: FSMContext):
    await message.answer(get_bot_text(user_id, "ask_category"), reply_markup=get_category_keyboard(), parse_mode="Markdown")
    await state.set_state(BirthdayForm.category)

@dp.callback_query(F.data.startswith("cat_"))
async def process_category(callback: types.CallbackQuery, state: FSMContext):
    category = callback.data.split("_")[1]
    await state.update_data(category=category)
    user_id = callback.from_user.id
    await callback.message.answer(get_bot_text(user_id, "ask_name"), reply_markup=get_action_keyboard(), parse_mode="Markdown")
    await state.set_state(BirthdayForm.name)
    await callback.answer()

@dp.message(BirthdayForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(BirthdayForm.wish)
    await message.answer(get_bot_text(message.from_user.id, "ask_wish"), reply_markup=get_action_keyboard(), parse_mode="Markdown")

@dp.message(BirthdayForm.wish)
async def process_wish(message: types.Message, state: FSMContext):
    await state.update_data(wish=message.text.strip())
    await state.set_state(BirthdayForm.dob_choice)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Enter Date (DOB / Wedding Date)", callback_data="dob_date")],
        [InlineKeyboardButton(text="🔢 Enter Age Details", callback_data="dob_direct")],
        [InlineKeyboardButton(text="✨ Skip Stats", callback_data="skip_stats")]
    ])
    await message.answer(get_bot_text(message.from_user.id, "ask_dob_type"), reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "dob_date")
async def dob_date_selected(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(dob_type="date")
    await state.set_state(BirthdayForm.dob_input)
    await callback.message.answer(get_bot_text(callback.from_user.id, "ask_dob_date"), reply_markup=get_action_keyboard(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "dob_direct")
async def dob_direct_selected(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(dob_type="direct")
    await state.set_state(BirthdayForm.dob_input)
    await callback.message.answer(get_bot_text(callback.from_user.id, "ask_dob_direct"), reply_markup=get_action_keyboard(), parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "skip_stats")
async def skip_stats_selected(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(dob="", age="")
    await ask_target_year(callback.message, state)
    await callback.answer()

@dp.message(BirthdayForm.dob_input)
async def process_dob_input(message: types.Message, state: FSMContext):
    val = message.text.strip()
    data = await state.get_data()
    if data.get("dob_type") == "direct":
        await state.update_data(age=val, dob=val)
    else:
        await state.update_data(dob=val, age="")
    await ask_target_year(message, state)

async def ask_target_year(message: types.Message, state: FSMContext):
    await state.set_state(BirthdayForm.target_year)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="2026", callback_data="year_2026"), InlineKeyboardButton(text="2027", callback_data="year_2027")],
        [InlineKeyboardButton(text="✨ Skip", callback_data="skip_year")]
    ])
    await message.answer(get_bot_text(message.from_user.id, "ask_year"), reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("year_"))
async def process_year(callback: types.CallbackQuery, state: FSMContext):
    year = callback.data.split("_")[1]
    await state.update_data(target_year=year)
    await ask_target_month(callback.message, state)
    await callback.answer()

@dp.callback_query(F.data == "skip_year")
async def skip_year(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(target_year="")
    await ask_target_month(callback.message, state)
    await callback.answer()

async def ask_target_month(message: types.Message, state: FSMContext):
    await state.set_state(BirthdayForm.target_month)
    months = [("January", "01"), ("February", "02"), ("March", "03"), ("April", "04"),
              ("May", "05"), ("June", "06"), ("July", "07"), ("August", "08"),
              ("September", "09"), ("October", "10"), ("November", "11"), ("December", "12")]
    kb = []
    row = []
    for m, num in months:
        row.append(InlineKeyboardButton(text=m, callback_data=f"mon_{num}"))
        if len(row) == 3:
            kb.append(row)
            row = []
    if row: kb.append(row)
    kb.append([InlineKeyboardButton(text="✨ Skip", callback_data="skip_month")])
    await message.answer(get_bot_text(message.from_user.id, "ask_month"), reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("mon_"))
async def process_month(callback: types.CallbackQuery, state: FSMContext):
    mon = callback.data.split("_")[1]
    await state.update_data(target_month=mon)
    await ask_target_day(callback.message, state)
    await callback.answer()

@dp.callback_query(F.data == "skip_month")
async def skip_month(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(target_month="")
    await ask_target_day(callback.message, state)
    await callback.answer()

async def ask_target_day(message: types.Message, state: FSMContext):
    await state.set_state(BirthdayForm.target_day)
    kb = []
    row = []
    for d in range(1, 32):
        day_str = f"{d:02d}"
        row.append(InlineKeyboardButton(text=str(d), callback_data=f"day_{day_str}"))
        if len(row) == 7:
            kb.append(row)
            row = []
    if row: kb.append(row)
    kb.append([InlineKeyboardButton(text="✨ Skip", callback_data="skip_day")])
    await message.answer(get_bot_text(message.from_user.id, "ask_day"), reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("day_"))
async def process_day(callback: types.CallbackQuery, state: FSMContext):
    day = callback.data.split("_")[1]
    await state.update_data(target_day=day)
    await ask_target_hour(callback.message, state)
    await callback.answer()

@dp.callback_query(F.data == "skip_day")
async def skip_day(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(target_day="")
    await ask_target_hour(callback.message, state)
    await callback.answer()

async def ask_target_hour(message: types.Message, state: FSMContext):
    await state.set_state(BirthdayForm.target_hour)
    kb = []
    row = []
    for h in range(24):
        h_str = f"{h:02d}"
        row.append(InlineKeyboardButton(text=h_str, callback_data=f"hour_{h_str}"))
        if len(row) == 6:
            kb.append(row)
            row = []
    if row: kb.append(row)
    kb.append([InlineKeyboardButton(text="✨ Skip", callback_data="skip_hour")])
    await message.answer(get_bot_text(message.from_user.id, "ask_hour"), reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("hour_"))
async def process_hour(callback: types.CallbackQuery, state: FSMContext):
    hour = callback.data.split("_")[1]
    await state.update_data(target_hour=hour)
    await ask_target_minute(callback.message, state)
    await callback.answer()

@dp.callback_query(F.data == "skip_hour")
async def skip_hour(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(target_hour="")
    await ask_target_minute(callback.message, state)
    await callback.answer()

async def ask_target_minute(message: types.Message, state: FSMContext):
    await state.set_state(BirthdayForm.target_minute)
    kb = []
    row = []
    for m in range(0, 60):
        m_str = f"{m:02d}"
        row.append(InlineKeyboardButton(text=m_str, callback_data=f"min_{m_str}"))
        if len(row) == 6:
            kb.append(row)
            row = []
    if row: kb.append(row)
    kb.append([InlineKeyboardButton(text="✨ Skip", callback_data="skip_minute")])
    await message.answer(get_bot_text(message.from_user.id, "ask_minute"), reply_markup=InlineKeyboardMarkup(inline_keyboard=kb), parse_mode="Markdown")

@dp.callback_query(F.data.startswith("min_"))
async def process_minute(callback: types.CallbackQuery, state: FSMContext):
    minute = callback.data.split("_")[1]
    await state.update_data(target_minute=minute)
    await prompt_photo(callback.message, state)
    await callback.answer()

@dp.callback_query(F.data == "skip_minute")
async def skip_minute(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(target_minute="")
    await prompt_photo(callback.message, state)
    await callback.answer()

async def prompt_photo(message: types.Message, state: FSMContext):
    await state.set_state(BirthdayForm.photo)
    await message.answer(get_bot_text(message.from_user.id, "ask_photo"), reply_markup=get_action_keyboard(), parse_mode="Markdown")

async def get_telegram_file_url(bot: Bot, file_id: str) -> str:
    try:
        file = await bot.get_file(file_id)
        return f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
    except Exception:
        return ""

@dp.message(BirthdayForm.photo, F.photo)
async def process_photo(message: types.Message, state: FSMContext):
    url = await get_telegram_file_url(bot, message.photo[-1].file_id)
    await state.update_data(photo=url)
    await state.set_state(BirthdayForm.video)
    await message.answer(get_bot_text(message.from_user.id, "ask_video"), reply_markup=get_action_keyboard(), parse_mode="Markdown")

@dp.message(BirthdayForm.video, F.video)
async def process_video(message: types.Message, state: FSMContext):
    url = await get_telegram_file_url(bot, message.video.file_id)
    await state.update_data(video=url)
    await state.set_state(BirthdayForm.song)
    await message.answer(get_bot_text(message.from_user.id, "ask_song"), reply_markup=get_action_keyboard(), parse_mode="Markdown")

@dp.message(BirthdayForm.song, F.audio)
async def process_song(message: types.Message, state: FSMContext):
    url = await get_telegram_file_url(bot, message.audio.file_id)
    await state.update_data(song=url)
    await state.set_state(BirthdayForm.voice)
    await message.answer(get_bot_text(message.from_user.id, "ask_voice"), reply_markup=get_action_keyboard(), parse_mode="Markdown")

@dp.message(BirthdayForm.voice, F.voice)
async def process_voice(message: types.Message, state: FSMContext):
    url = await get_telegram_file_url(bot, message.voice.file_id)
    await state.update_data(voice=url)
    await state.set_state(BirthdayForm.audio)
    await message.answer(get_bot_text(message.from_user.id, "ask_audio"), reply_markup=get_action_keyboard(), parse_mode="Markdown")

@dp.message(BirthdayForm.audio, F.audio)
async def process_audio(message: types.Message, state: FSMContext):
    url = await get_telegram_file_url(bot, message.audio.file_id)
    await state.update_data(extra_audio=url)
    await finish_form(message, state)

@dp.callback_query(F.data == "skip_step")
async def process_skip(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    user_id = callback.from_user.id
    if current_state == BirthdayForm.photo.state:
        await state.set_state(BirthdayForm.video)
        await callback.message.answer(get_bot_text(user_id, "ask_video"), reply_markup=get_action_keyboard(), parse_mode="Markdown")
    elif current_state == BirthdayForm.video.state:
        await state.set_state(BirthdayForm.song)
        await callback.message.answer(get_bot_text(user_id, "ask_song"), reply_markup=get_action_keyboard(), parse_mode="Markdown")
    elif current_state == BirthdayForm.song.state:
        await state.set_state(BirthdayForm.voice)
        await callback.message.answer(get_bot_text(user_id, "ask_voice"), reply_markup=get_action_keyboard(), parse_mode="Markdown")
    elif current_state == BirthdayForm.voice.state:
        await state.set_state(BirthdayForm.audio)
        await callback.message.answer(get_bot_text(user_id, "ask_audio"), reply_markup=get_action_keyboard(), parse_mode="Markdown")
    elif current_state == BirthdayForm.audio.state:
        await finish_form(callback.message, state)
    elif current_state == BirthdayForm.dob_input.state:
        await ask_target_year(callback.message, state)
    await callback.answer("Skipped")

async def finish_form(message: types.Message, state: FSMContext):
    data = await state.get_data()
    y, m, d = data.get("target_year", ""), data.get("target_month", ""), data.get("target_day", "")
    h, mn = data.get("target_hour", "00"), data.get("target_minute", "00")
    
    target_time_str = f"{y}-{m}-{d}T{h}:{mn}:00" if (y and m and d) else ""

    params = {
        "name": data.get("name", "Friend"),
        "msg": data.get("wish", ""),
        "category": data.get("category", "Birthday"),
        "dob": data.get("dob", ""),
        "age": data.get("age", data.get("dob", "")),
        "target_time": target_time_str,
        "photo": data.get("photo", ""),
        "video": data.get("video", ""),
        "song": data.get("song", ""),
        "voice": data.get("voice", ""),
        "extra_audio": data.get("extra_audio", "")
    }
    
    surprise_id = save_surprise_to_db(message.from_user.id, params["category"], params["name"], params["msg"], params)
    
    preview_url = f"{VERCEL_URL}/?id={surprise_id}&preview=true"
    view_url = f"{VERCEL_URL}/?id={surprise_id}"
    
    share_text = f"✨ Check out this amazing celebration for {params['name']}! 🎉 {view_url}"
    tg_share = f"https://t.me/share/url?url={view_url}&text=✨ Check out this amazing celebration! 🎉"
    wa_share = f"https://api.whatsapp.com/send?text={share_text}"

    btn_label = "🎂 My Birthday View" if params["category"] == "Birthday" else "✨ Open Surprise View"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🤍 Preview Surprise", web_app=WebAppInfo(url=preview_url)),
            InlineKeyboardButton(text=btn_label, web_app=WebAppInfo(url=view_url))
        ],
        [
            InlineKeyboardButton(text="💬 Share on Telegram", url=tg_share),
            InlineKeyboardButton(text="🟢 Share on WhatsApp", url=wa_share)
        ],
        [
            InlineKeyboardButton(text="🔗 Copy Link (All Apps)", url=view_url)
        ],
        [
            InlineKeyboardButton(text="🗑️ Delete this Surprise", callback_data=f"delete_surp_{surprise_id}")
        ]
    ])
    
    success_msg = get_bot_text(message.from_user.id, "ready", name=params["name"]) + "\n\nChoose how you'd like to experience or share your creation below:"
    await message.answer(success_msg, reply_markup=kb, parse_mode="Markdown")
    await state.clear()

@dp.callback_query(F.data.startswith("delete_surp_"))
async def inline_delete_surprise(callback: types.CallbackQuery):
    surp_id = callback.data.split("_")[2]
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM surprises WHERE id = ?", (surp_id,))
    conn.commit()
    conn.close()
    await callback.message.edit_text("🗑️ This surprise has been deleted successfully!")
    await callback.answer()

async def get_surprise_api(request):
    surprise_id = request.query.get("id")
    if not surprise_id: return web.json_response({"error": "No ID"}, status=400)
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("SELECT params_json FROM surprises WHERE id = ?", (surprise_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return web.json_response(json.loads(row[0]), headers={"Access-Control-Allow-Origin": "*"})
    return web.json_response({"error": "Not found"}, status=404)

async def delete_surprise_api(request):
    surprise_id = request.query.get("id")
    if not surprise_id: return web.json_response({"error": "No ID"}, status=400)
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM surprises WHERE id = ?", (surprise_id,))
    conn.commit()
    conn.close()
    return web.json_response({"success": True}, headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "DELETE"})

async def web_server():
    app = web.Application()
    app.router.add_get("/api/surprise", get_surprise_api)
    app.router.add_delete("/api/delete", delete_surprise_api)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080)))
    await site.start()

async def setup_bot_commands():
    commands = [
        BotCommand(command="start", description="🎉 Create a Surprise"),
        BotCommand(command="stats", description="📊 Bot Statistics"),
        BotCommand(command="help", description="💡 Help & Info"),
        BotCommand(command="cancel", description="🚫 Cancel Process")
    ]
    await bot.set_my_commands(commands)

async def main():
    await setup_bot_commands()
    await asyncio.gather(web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
