import asyncio
import json
import os
import sqlite3
import urllib.parse
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
    WebAppInfo,
)
from aiohttp import web

API_TOKEN = "8854916574:AAEgxWmPyP4OPNSsLfsBbXXFu5W6LiFcq0o"
OWNER_ID = 1689374364
FREE_LIMIT = 5

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
VERCEL_URL = "https://birthday-surprise-app-two.vercel.app"

# --- മുഴുവൻ രാജ്യങ്ങളും ഭാഷകളും (Full 40+ Language Dictionaries) ---
COUNTRY_LANGUAGES = {
    "Asia": {
        "🇮🇳 India": [
            ("Hindi", "hi"),
            ("English", "en"),
            ("Malayalam", "ml"),
            ("Telugu", "te"),
            ("Kannada", "kn"),
            ("Bengali", "bn"),
        ],
        "🇯🇵 Japan": [("Japanese", "ja")],
        "🇰🇷 South Korea": [("Korean", "ko")],
        "🇦🇿 Azerbaijan": [("Azerbaijani", "az")],
        "🇦🇲 Armenia": [("Armenian", "hy")],
        "🇷🇺 Russia": [("Russian", "ru")],
        "🇮🇩 Indonesia": [("Indonesian", "id")],
        "🇹🇷 Turkey": [("Turkish", "tr")],
        "🇸🇦 Saudi Arabia": [("Arabic", "ar")],
        "🇪🇬 Egypt": [("Arabic", "ar")],
        "🇲🇾 Malaysia": [("Malay", "ms")],
        "🇸🇬 Singapore": [
            ("English", "en"),
            ("Mandarin Chinese", "zh"),
            ("Malay", "ms"),
            ("Tamil", "ta"),
        ],
        "🇨🇳 China": [("Chinese (Mandarin)", "zh")],
        "🇺🇿 Uzbekistan": [("Uzbek", "uz")],
        "🇹🇯 Tajikistan": [("Tajik", "tg")],
        "🇮🇷 Iran": [("Persian", "fa")],
        "🇲🇲 Myanmar": [("Burmese", "my")],
        "🇳🇬 Nigeria": [("English", "en")],
        "🇦🇪 UAE": [("Arabic", "ar"), ("English", "en")],
        "🇻🇳 Vietnam": [("Vietnamese", "vi")],
        "🇵🇭 Philippines": [("Filipino", "fil"), ("English", "en")],
    },
    "Europe": {
        "🇧🇾 Belarus": [("Belarusian", "be"), ("Russian", "ru")],
        "🇮🇹 Italy": [("Italian", "it")],
        "🇩🇪 Germany": [("German", "de")],
        "🇪🇸 Spain": [("Spanish", "es")],
        "🇫🇷 France": [("French", "fr")],
        "🇺🇦 Ukraine": [("Ukrainian", "uk")],
    },
    "Africa": {
        "🇰🇪 Kenya": [("English", "en"), ("Swahili", "sw")],
        "🇿🇦 South Africa": [
            ("English", "en"),
            ("Zulu", "zu"),
            ("Xhosa", "xh"),
            ("Afrikaans", "af"),
        ],
    },
    "Americas": {
        "🇧🇷 Brazil": [("Portuguese", "pt")],
        "🇲🇽 Mexico": [("Spanish", "es")],
    },
}

# --- പഴയ എല്ലാ ഭാഷകളും ഉൾപ്പെടുത്തിയ ഫുൾ ഡിക്ഷണറി ---
BOT_TEXTS = {
    "en": {
        "welcome": "✨ Welcome to your little corner of surprises...\n\nYour language is currently set to **English**. Want to change your country/language? Choose below or keep English:",
        "region_selected": "🌍 Region: **{region}**. Select your country:",
        "country_choice": "🗣️ Choose your language for **{country}**:",
        "lang_updated": "✅ Language preference updated successfully!",
        "ask_category": "🎉 What kind of celebration is this? Choose below:",
        "owner_active": "🤍 **Owner Mode Active!** Whose special occasion are we celebrating today? Send me their name:",
        "free_remaining": "🎁 You have **{remaining}** free surprise(s) remaining! Send me their name:",
        "free_first": "🎁 Your first **{limit}** surprises are **FREE**! Send me their name:",
        "ask_name": "Whose special occasion are we celebrating today? Send me their name:",
        "ask_wish": "Write a sweet, heartfelt wish or message for them (Long paragraphs supported!):",
        "ask_age_mode": "How would you like to add age details for stats?",
        "ask_dob_input": "📅 Please send Date in **YYYY-MM-DD** format (e.g., `2003-12-24`):",
        "ask_age_input": "🔢 Please enter their direct age as a number (e.g., `22`):",
        "ask_year": "Choose the year for the surprise:",
        "ask_month": "Choose the month:",
        "ask_date": "Pick the date:",
        "ask_hour": "Select the Hour (24-Hour format, 00 to 23):",
        "ask_minute": "Select the Minute (00 to 59):",
        "ask_photo": "Share a lovely photo to cherish (or skip):",
        "ask_video": "Share a special video moment (or skip):",
        "ask_song": "Send a favorite song or audio file (or skip):",
        "ask_voice": "Send a warm voice note to make it extra special (or skip):",
        "ask_audio": "Add one more audio file if you'd like (or skip):",
        "ready": "✨ All ready for {name}!\n\nChoose how you'd like to experience or share your creation below:",
    },
    "hi": {
        "welcome": "✨ सरप्राइज की इस छोटी सी दुनिया में आपका स्वागत है...\n\nआपकी भाषा वर्तमान में **हिंदी** पर सेट है।",
        "region_selected": "🌍 क्षेत्र: **{region}**. अपना देश चुनें:",
        "country_choice": "🗣️ **{country}** के लिए अपनी भाषा चुनें:",
        "lang_updated": "✅ भाषा सफलतापूर्वक अपडेट कर दी गई है!",
        "ask_category": "🎉 यह किस प्रकार का उत्सव है? नीचे से चुनें:",
        "owner_active": "🤍 **ओनर मोड सक्रिय है!**\n\nआज हम किसका जश्न मना रहे हैं? नाम भेजें:",
        "free_remaining": "🎁 आपके पास **{remaining}** मुफ्त सरप्राइज शेष हैं!",
        "free_first": "🎁 आपके पहले **{limit}** सरप्राइज **मुफ्त** हैं!",
        "ask_name": "आज हम किसका जश्न मना रहे हैं? उनका नाम भेजें:",
        "ask_wish": "उनके लिए एक प्यारा सा संदेश लिखें:",
        "ask_age_mode": "आयु विवरण कैसे जोड़ना चाहते हैं?",
        "ask_dob_input": "📅 **YYYY-MM-DD** प्रारूप में तिथि भेजें (जैसे: `2003-12-24`):",
        "ask_age_input": "🔢 सीधी आयु संख्या के रूप में दर्ज करें (जैसे: `22`):",
        "ask_year": "सरप्राइज के लिए वर्ष चुनें:",
        "ask_month": "महीना चुनें:",
        "ask_date": "तारीख चुनें:",
        "ask_hour": "घंटा चुनें (00-23):",
        "ask_minute": "मिनट चुनें (00-59):",
        "ask_photo": "एक प्यारी सी फोटो शेयर करें (या छोड़ें):",
        "ask_video": "एक खास वीडियो शेयर करें (या छोड़ें):",
        "ask_song": "पसंदीदा गाना या ऑडियो भेजें (या छोड़ें):",
        "ask_voice": "एक वॉयस नोट भेजें (या छोड़ें):",
        "ask_audio": "एक और ऑडियो फाइल जोड़ें (या छोड़ें):",
        "ready": "✨ {name} के लिए सब तैयार है!",
    },
    "ml": {
        "welcome": "✨ ചെറിയ സർപ്രൈസുകളുടെ ലോകത്തേക്ക് സ്വാഗതം...\n\nനിങ്ങളുടെ ഭാഷ ഇപ്പോൾ **മലയാളം** ആണ്.",
        "region_selected": "🌍 പ്രദേശം: **{region}**. നിങ്ങളുടെ രാജ്യം തിരഞ്ഞെടുക്കൂ:",
        "country_choice": "🗣️ **{country}**-നുള്ള ഭാഷ തിരഞ്ഞെടുക്കൂ:",
        "lang_updated": "✅ ഭാഷ വിജയകരമായി മാറ്റിയിരിക്കുന്നു!",
        "ask_category": "🎉 ഇത് എന്തുതരം ആഘോഷമാണ്? താഴെ നിന്നും തിരഞ്ഞെടുക്കൂ:",
        "owner_active": "🤍 **ഓണർ മോഡ് ആക്ടീവ് ആണ്!**\n\nഇന്ന് ആരുടെ വിശേഷമാണ് ആഘോഷിക്കുന്നത്? പേര് അയക്കൂ:",
        "free_remaining": "🎁 നിങ്ങൾക്ക് ഇനി **{remaining}** ഫ്രീ സർപ്രൈസുകൾ ബാക്കിയുണ്ട്!",
        "free_first": "🎁 നിങ്ങളുടെ ആദ്യത്തെ **{limit}** സർപ്രൈസുകൾ **സൗജന്യമാണ്**!",
        "ask_name": "ഇന്ന് ആരുടെ വിശേഷമാണ് ആഘോഷിക്കുന്നത്? അവരുടെ പേര് അയക്കൂ:",
        "ask_wish": "അവർക്കായി ഒരു മനോഹരമായ ആശംസ എഴുതൂ:",
        "ask_age_mode": "വയസ്സ് അല്ലെങ്കിൽ ജനന തീയതി എങ്ങനെ ചേർക്കണം?",
        "ask_dob_input": "📅 തീയതി **YYYY-MM-DD** ഫോർമാറ്റിൽ അയക്കൂ (ഉദാഹരണത്തിന്: `2003-12-24`):",
        "ask_age_input": "🔢 പ്രായം മാത്രം സംഖ്യയായി നൽകൂ (ഉദാഹരണത്തിന്: `22`):",
        "ask_year": "വർഷം തിരഞ്ഞെടുക്കൂ:",
        "ask_month": "മാസം തിരഞ്ഞെടുക്കൂ:",
        "ask_date": "തീയതി തിരഞ്ഞെടുക്കൂ:",
        "ask_hour": "മണിക്കൂർ തിരഞ്ഞെടുക്കൂ (00-23):",
        "ask_minute": "മിനിറ്റ് തിരഞ്ഞെടുക്കൂ (00-59):",
        "ask_photo": "ഒരു ഫോട്ടോ പങ്കുവെക്കൂ (သို့မဟုတ် ഒഴിവാക്കൂ):",
        "ask_video": "ഒരു വീഡിയോ പങ്കുവെക്കൂ (သို့မဟုတ် ഒഴിവാക്കൂ):",
        "ask_song": "പാട്ടോ ഓഡിയോ ഫയലോ അയക്കൂ (သို့မဟုတ် ഒഴിവാക്കൂ):",
        "ask_voice": "ഒരു വോയിസ് നോട്ട് അയക്കൂ (သို့မဟုတ် ഒഴിവാക്കൂ):",
        "ask_audio": "മറ്റൊരു ഓഡിയോ കൂടി ചേർക്കണമെങ്കിൽ ചേർക്കൂ (သို့မဟုတ် ഒഴിവാക്കൂ):",
        "ready": "✨ {name}-നുള്ള സർപ്രൈസ് റെഡിയാണ്!",
    },
    "te": {
        "welcome": "✨ సర్ప్రైజ్‌ల చిన్న ప్రపంచానికి స్వాగతం...\n\nమీ భాష ప్రస్తుతం **తెలుగు**కి సెట్ చేయబడింది.",
        "region_selected": "🌍 ప్రాంతం: **{region}**. మీ దేశాన్ని ఎంచుకోండి:",
        "country_choice": "🗣️ **{country}** కోసం మీ భాషను ఎంచుకోండి:",
        "lang_updated": "✅ భాష ప్రాధాన్యత విజయవంతంగా నవీకరించబడింది!",
        "ask_category": "🎉 ఇది ఏ రకమైన వేడుక?",
        "owner_active": "🤍 **ఓనర్ మోడ్ యాక్టివ్‌లో ఉంది!**\n\nఈరోజు ఏ వేడుక జరుపుకుంటున్నాం? పేరును పంపండి:",
        "free_remaining": "🎁 మీకు ఇంకా **{remaining}** ఉచిత సర్ప్రైజ్‌లు మిగిలి ఉన్నాయి!",
        "free_first": "🎁 మీ మొదటి **{limit}** సర్ప్రైజ్‌లు **ఉచితం**!",
        "ask_name": "ఈరోజు ఏ వేడుక జరుపుకుంటున్నాం? వారి పేరును పంపండి:",
        "ask_wish": "వారి కోసం శుభాకాంక్షలు వ్రాయండి:",
        "ask_age_mode": "వయస్సు వివరాలను ఎలా జోడించాలనుకుంటున్నారు?",
        "ask_dob_input": "📅 తేదీని **YYYY-MM-DD** ფორმატில் அனுப்பவும் (ఉదా: `2003-12-24`):",
        "ask_age_input": "🔢 ప్రత్యక్ష వయస్సును సంఖ్యగా నమోదు చేయండి (ఉదా: `22`):",
        "ask_year": "సంవత్సరాన్ని ఎంచుకోండి:",
        "ask_month": "నెలని ఎంచుకోండి:",
        "ask_date": "తేదీని ఎంచుకోండి:",
        "ask_hour": "గంటను ఎంచుకోండి (00-23):",
        "ask_minute": "నిమిషాన్ని ఎంచుకోండి (00-59):",
        "ask_photo": "ఫోటోను షేర్ చేయండి (లేదా దాటవేయి):",
        "ask_video": "వీడియోను షేర్ చేయండి (లేదా దాటవేయి):",
        "ask_song": "పాటను పంపండి (లేదా దాటవేయి):",
        "ask_voice": "వాయిస్ నోట్ పంపండి (లేదా దాటవేయి):",
        "ask_audio": "మరో ఆడియో ఫైల్‌ని జోడించండి (లేదా దాటవేయి):",
        "ready": "✨ {name} కోసం అన్నీ సిద్ధంగా ఉన్నాయి!",
    },
    "kn": {
        "welcome": "✨ ಆಶ್ಚರ್ಯಗಳ ಸಣ್ಣ ಜಗತ್ತಿಗೆ ಸ್ವಾಗತ...\n\nನಿಮ್ಮ ಭಾಷೆಯನ್ನು **ಕನ್ನಡ**ಕ್ಕೆ ಹೊಂದಿಸಲಾಗಿದೆ.",
        "region_selected": "🌍 ಪ್ರದೇಶ: **{region}**. ನಿಮ್ಮ ದೇಶವನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
        "country_choice": "🗣️ **{country}** ಗಾಗಿ ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
        "lang_updated": "✅ ಭಾಷಾ ಪ್ರಾಶಸ್ತ್ಯವನ್ನು ಯಶಸ್ವಿಯಾಗಿ ನವೀಕರಿಸಲಾಗಿದೆ!",
        "ask_category": "🎉 ಇದು ಯಾವ ರೀತಿಯ ಆಚರಣೆ?",
        "owner_active": "🤍 **ಮಾಲೀಕ ಮೋಡ್ ಸಕ್ರಿಯವಾಗಿದೆ!**\n\nಇಂದು ಯಾವ ವಿಶೇಷತೆ ಆಚರಿಸುತ್ತಿದ್ದೇವೆ? ಹೆಸರನ್ನು ಕಳುಹಿಸಿ:",
        "free_remaining": "🎁 ನೀವು **{remaining}** ಉಚಿತ ಆಶ್ಚರ್ಯಗಳನ್ನು ಹೊಂದಿದ್ದೀರಿ!",
        "free_first": "🎁 ನಿಮ್ಮ ಮೊದಲ **{limit}** ಆಶ್ಚರ್ಯಗಳು **ಉಚಿತ**!",
        "ask_name": "ಇಂದು ಯಾವ ವಿಶೇಷತೆ ಆಚರಿಸುತ್ತಿದ್ದೇವೆ? ಅವರ ಹೆಸರನ್ನು ಕಳುಹಿಸಿ:",
        "ask_wish": "ಅವರಿಗಾಗಿ ಶುಭಾಶಯವನ್ನು ಬರೆಯಿರಿ:",
        "ask_age_mode": "ವಯಸ್ಸಿನ ವಿವರಗಳನ್ನು ಹೇಗೆ ಸೇರಿಸಲು ಬಯಸುತ್ತೀರಿ?",
        "ask_dob_input": "📅 ದಿನಾಂಕವನ್ನು **YYYY-MM-DD** ფორಮ್ಯಾಟ್‌ನಲ್ಲಿ ಕಳುಹಿಸಿ (ಉದಾ: `2003-12-24`):",
        "ask_age_input": "🔢 ವಯಸ್ಸನ್ನು ಸಂಖ್ಯೆಯಾಗಿ ನಮೂದಿಸಿ (ಉದಾ: `22`):",
        "ask_year": "ವರ್ಷವನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
        "ask_month": "ತಿಂಗಳನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
        "ask_date": "ದಿನಾಂಕವನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
        "ask_hour": "ಗಂಟೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ (00-23):",
        "ask_minute": "ನಿಮಿಷವನ್ನು ಆಯ್ಕೆಮಾಡಿ (00-59):",
        "ask_photo": "ಫೋಟೋ ಹಂಚಿಕೊಳ್ಳಿ (ಅಥವಾ ಬಿಟ್ಟುಬಿಡಿ):",
        "ask_video": "ವೀಡಿಯೊ ಹಂಚಿಕೊಳ್ಳಿ (ಅಥವಾ ಬಿಟ್ಟುಬಿಡಿ):",
        "ask_song": "ಹಾಡನ್ನು ಕಳುಹಿಸಿ (ಅಥವಾ ಬಿಟ್ಟುಬಿಡಿ):",
        "ask_voice": "ಧ್ವನಿ ಟಿಪ್ಪಣಿಯನ್ನು ಕಳುಹಿಸಿ (ಅಥವಾ ಬಿಟ್ಟುಬಿಡಿ):",
        "ask_audio": "ಇನ್ನೊಂದು ಆಡಿಯೊವನ್ನು ಸೇರಿಸಿ (ಅಥವಾ ಬಿಟ್ಟುಬಿಡಿ):",
        "ready": "✨ {name} ಗಾಗಿ ಎಲ್ಲವೂ ಸಿದ್ಧವಾಗಿದೆ!",
    },
    "bn": {
        "welcome": "✨ আপনার চমকের ছোট দুনিয়ায় স্বাগতম...\n\nআপনার ভাষা বর্তমানে **বাংলা** তে সেট করা আছে।",
        "region_selected": "🌍 অঞ্চল: **{region}**। আপনার দেশ নির্বাচন করুন:",
        "country_choice": "🗣️ **{country}** এর জন্য আপনার ভাষা বেছে নিন:",
        "lang_updated": "✅ ভাষা পছন্দ সফলভাবে আপডেট করা হয়েছে!",
        "ask_category": "🎉 এটি কি ধরনের উদযাপন?",
        "owner_active": "🤍 **মালিক মোড সক্রিয়!**\n\nআজ কী উদযাপন করছি? তার নাম পাঠান:",
        "free_remaining": "🎁 আপনার **{remaining}** টি বিনামূল্যে সারপ্রাইজ বাকি আছে!",
        "free_first": "🎁 আপনার প্রথম **{limit}** টি সারপ্রাইজ **ফ্রি**!",
        "ask_name": "আজ কার বিশেষ দিন উদযাপন করছি? তার নাম পাঠান:",
        "ask_wish": "তাদের জন্য একটি সুন্দর শুভেচ্ছা লিখুন:",
        "ask_age_mode": "বয়সের বিবরণ কীভাবে যোগ করতে চান?",
        "ask_dob_input": "📅 জন্ম তারিখ **YYYY-MM-DD** ফরম্যাটে পাঠান (যেমন: `2003-12-24`):",
        "ask_age_input": "🔢 সরাসরি বয়স সংখ্যায় লিখুন (যেমন: `22`):",
        "ask_year": "বছর বেছে নিন:",
        "ask_month": "মাস বেছে নিন:",
        "ask_date": "তারিখ বেছে নিন:",
        "ask_hour": "ঘণ্টা বেছে নিন (00-23):",
        "ask_minute": "মিনিট বেছে নিন (00-59):",
        "ask_photo": "একটি ছবি শেয়ার করুন (অথবা বাদ দিন):",
        "ask_video": "একটি ভিডিও শেয়ার করুন (অথবা বাদ দিন):",
        "ask_song": "একটি গান পাঠান (অথবা বাদ দিন):",
        "ask_voice": "একটি ভয়েস নোট পাঠান (অথবা বাদ দিন):",
        "ask_audio": "অন্য একটি অডিও যোগ করুন (অথবা বাদ দিন):",
        "ready": "✨ {name} এর জন্য সবকিছু প্রস্তুত!",
    },
    "ms": {
        "welcome": "✨ Selamat datang ke sudut kejutan anda...\n\nBahasa anda ditetapkan kepada **Bahasa Melayu**.",
        "region_selected": "🌍 Wilayah: **{region}**. Pilih negara anda:",
        "country_choice": "🗣️ Pilih bahasa anda untuk **{country}**:",
        "lang_updated": "✅ Keutamaan bahasa berjaya dikemas kini!",
        "ask_category": "🎉 Apakah jenis sambutan ini?",
        "owner_active": "🤍 **Mod Pemilik Aktif!**\n\nApa yang kita sambut hari ini? Hantar nama:",
        "free_remaining": "🎁 Anda mempunyai **{remaining}** kejutan percuma!",
        "free_first": "🎁 **{limit}** kejutan pertama anda adalah **PERCUMA**!",
        "ask_name": "Apa yang kita sambut hari ini? Hantar nama:",
        "ask_wish": "Tulis ucapan yang manis:",
        "ask_age_mode": "Bagaimana anda ingin menambah butiran umur?",
        "ask_dob_input": "📅 Sila hantar Tarikh dalam format **YYYY-MM-DD** (cth. `2003-12-24`):",
        "ask_age_input": "🔢 Sila masukkan umur sebagai nombor (cth. `22`):",
        "ask_year": "Pilih tahun:",
        "ask_month": "Pilih bulan:",
        "ask_date": "Pilih tarikh:",
        "ask_hour": "Pilih jam (00-23):",
        "ask_minute": "Pilih minit (00-59):",
        "ask_photo": "Kongsi foto (atau langkau):",
        "ask_video": "Kongsi video (atau langkau):",
        "ask_song": "Hantar lagu (atau langkau):",
        "ask_voice": "Hantar nota suara (atau langkau):",
        "ask_audio": "Tambah audio lain (atau langkau):",
        "ready": "✨ Semuanya siap untuk {name}!",
    },
    "zh": {
        "welcome": "✨ 欢迎来到您的惊喜角落...\n\n您的语言当前设置为 **中文 (Mandarin)**。",
        "region_selected": "🌍 地区：**{region}**。请选择您的国家：",
        "country_choice": "🗣️ 请选择 **{country}** 的语言：",
        "lang_updated": "✅ 语言首选项更新成功！",
        "ask_category": "🎉 这是什么类型的庆祝活动？",
        "owner_active": "🤍 **所有者模式已激活！**\n\n我们今天在庆祝什么？发送名字：",
        "free_remaining": "🎁 您还有 **{remaining}** 次免费惊喜制作机会！",
        "free_first": "🎁 您的前 **{limit}** 个惊喜是**免费**的！",
        "ask_name": "我们今天在庆祝什么？发送名字：",
        "ask_wish": "为他们写一份温馨的祝福：",
        "ask_age_mode": "您想如何添加详细信息？",
        "ask_dob_input": "📅 请以 **YYYY-MM-DD** 格式发送日期（例如 `2003-12-24`）：",
        "ask_age_input": "🔢 请直接输入数字年龄（例如 `22`）：",
        "ask_year": "选择年份：",
        "ask_month": "选择月份：",
        "ask_date": "选择日期：",
        "ask_hour": "选择小时 (00-23)：",
        "ask_minute": "选择分钟 (00-59)：",
        "ask_photo": "分享一张照片（或跳过）：",
        "ask_video": "分享视频时刻（或跳过）：",
        "ask_song": "发送喜欢的歌曲（或跳过）：",
        "ask_voice": "发送语音便签（或跳过）：",
        "ask_audio": "添加另一个音频（或跳过）：",
        "ready": "✨ 一切为 {name} 准备就绪！",
    },
    "ta": {
        "welcome": "✨ ஆச்சரியங்கள் நிறைந்த உங்களின் சிறிய உலகத்திற்கு வரவேற்பு...\n\nஉங்கள் மொழி **தமிழ்** என அமைக்கப்பட்டுள்ளது.",
        "region_selected": "🌍 பிராந்தியம்: **{region}**. உங்கள் நாட்டைத் தேர்ந்தெடுக்கவும்:",
        "country_choice": "🗣️ **{country}** க்கான மொழியைத் தேர்ந்தெடுக்கவும்:",
        "lang_updated": "✅ மொழி முன்னுரிமை வெற்றிகரமாக புதுப்பிக்கப்பட்டது!",
        "ask_category": "🎉 இது என்ன வகையான கொண்டாட்டம்?",
        "owner_active": "🤍 **உரிமையாளர் பயன்முறை активен!**\n\nஇன்று என்ன கொண்டாடுகிறோம்? பெயரை அனுப்பவும்:",
        "free_remaining": "🎁 உங்களிடம் **{remaining}** இலவச ஆச்சரியங்கள் மீதமுள்ளன!",
        "free_first": "🎁 உங்கள் முதல் **{limit}** ஆச்சரியங்கள் **இலவசம்**!",
        "ask_name": "இன்று என்ன கொண்டாடுகிறோம்? பெயரை அனுப்பவும்:",
        "ask_wish": "அவர்களுக்காக ஒரு இனிய வாழ்த்தை எழுதுங்கள்:",
        "ask_age_mode": "வயது விவரங்களை எவ்வாறு சேர்க்க விரும்புகிறீர்கள்?",
        "ask_dob_input": "📅 பிறந்த தேதியை **YYYY-MM-DD** வடிவத்தில் அனுப்பவும் (எ.கா. `2003-12-24`):",
        "ask_age_input": "🔢 நேரடி வயதை எண்ணாக உள்ளிடவும் (எ.கா. `22`):",
        "ask_year": "ஆண்டைத் தேர்ந்தெடுக்கவும்:",
        "ask_month": "மாதத்தைத் தேர்ந்தெடுக்கவும்:",
        "ask_date": "தேதியைத் தேர்ந்தெடுக்கவும்:",
        "ask_hour": "மணிநேரத்தைத் தேர்ந்தெடுக்கவும் (00-23):",
        "ask_minute": "நிமிடத்தைத் தேர்ந்தெடுக்கவும் (00-59):",
        "ask_photo": "புகைப்படத்தைப் பகிரவும் (அல்லது தவிர்க்கவும்):",
        "ask_video": "வீடியோவைப் பகிரவும் (அல்லது தவிர்க்கவும்):",
        "ask_song": "பாடலை அனுப்பவும் (அல்லது தவிர்க்கவும்):",
        "ask_voice": "குரல் குறிப்பை அனுப்பவும் (அல்லது தவிர்க்கவும்):",
        "ask_audio": "மற்றொரு ஆடியோவைச் சேர்க்கவும் (அல்லது தவிர்க்கவும்):",
        "ready": "✨ {name}க்காக அனைத்தும் தயார்!",
    },
    "uz": {
        "welcome": "✨ Kutilmagan sovg'alar olamiga xush kelibsiz...\n\nSizning tilingiz **O'zbekcha**ga sozlangan.",
        "region_selected": "🌍 Hudud: **{region}**. Davlatni tanlang:",
        "country_choice": "🗣️ **{country}** uchun tilni tanlang:",
        "lang_updated": "✅ Til muvaffaqiyatli yangilandi!",
        "ask_category": "🎉 Bu qanday bayram yoki marosim?",
        "owner_active": "🤍 **Egasi rejimi faol!**\n\nBugun nishonlayapmiz? Ismini yuboring:",
        "free_remaining": "🎁 Sizda **{remaining}** ta bepul imkoniyat qoldi!",
        "free_first": "🎁 Dastlabki **{limit}** ta sovg'angiz **BEPUL** yaratiladi!",
        "ask_name": "Bugun nishonlayapmiz? Ismini yuboring:",
        "ask_wish": "Samimiy tilak yozing:",
        "ask_age_mode": "Yosh tafsilotlarini qanday kiritmoqchisiz?",
        "ask_dob_input": "📅 Tug'ilgan sanani **YYYY-MM-DD** formatida yuboring (masalan: `2003-12-24`):",
        "ask_age_input": "🔢 To'g'ridan-to'g'ri yoshni kiriting (masalan: `22`):",
        "ask_year": "Yilni tanlang:",
        "ask_month": "Oyni tanlang:",
        "ask_date": "Sanani tanlang:",
        "ask_hour": "Soatni tanlang (00-23):",
        "ask_minute": "Daqiqani tanlang (00-59):",
        "ask_photo": "Rasm yuboring (yoki o'tkazib yuboring):",
        "ask_video": "Video yuboring (yoki o'tkazib yuboring):",
        "ask_song": "Qo'shiq yuboring (yoki o'tkazib yuboring):",
        "ask_voice": "Ovozli xabar yuboring (yoki o'tkazib yuboring):",
        "ask_audio": "Yana bir audio qo'shing (yoki o'tkazib yuboring):",
        "ready": "✨ {name} uchun barchasi tayyor!",
    },
    "tg": {
        "welcome": "✨ Хуш омадед ба гӯшаи сюрпризҳои шумо...\n\nЗабони шумо ба **Тоҷикӣ** танзим шудааст.",
        "region_selected": "🌍 Минқақа: **{region}**. Давлати худро интихоб кунед:",
        "country_choice": "🗣️ Забонро барои **{country}** интихоб кунед:",
        "lang_updated": "✅ Забон бо муваффақият нав карда шуд!",
        "ask_category": "🎉 Ин чӣ гуна ҷашн аст?",
        "owner_active": "🤍 **Режими соҳибмулк фаъол аст!**\n\nИмрӯз чӣ ҷашн мегирем? Номро фиристед:",
        "free_remaining": "🎁 Шумо **{remaining}** сюрпризи ройгон доред!",
        "free_first": "🎁 Аввалин **{limit}** сюрпризи шумо **РОЙГОН** аст!",
        "ask_name": "Имрӯз чӣ ҷашн мегирем? Номро фиристед:",
        "ask_wish": "Табрики зебо нависед:",
        "ask_age_mode": "Тафсилоти синну солро чӣ тавр iлова кардан мехоҳед?",
        "ask_dob_input": "📅 Санаро бо формати **YYYY-MM-DD** фиристед (масалан: `2003-12-24`):",
        "ask_age_input": "🔢 Синну солро ҳамчун рақам ворид кунед (масалан: `22`):",
        "ask_year": "Солро интихоб кунед:",
        "ask_month": "Моҳро интихоб кунед:",
        "ask_date": "Санаро интихоб кунед:",
        "ask_hour": "Соатро интихоб кунед (00-23):",
        "ask_minute": "Дақиқаро интихоб кунед (00-59):",
        "ask_photo": "Сурат фиристед (ё гузаред):",
        "ask_video": "Видео фиристед (ё гузаред):",
        "ask_song": "Суруд фиристед (ё гузаред):",
        "ask_voice": "Паёми овозӣ фиристед (ё гузаред):",
        "ask_audio": "Аудиои дигар илова кунед (ё гузаред):",
        "ready": "✨ Ҳама чиз барои {name} омода аст!",
    },
    "fa": {
        "welcome": "✨ به گوشه کوچک شگفتی های خود خوش آمدید...\n\nزبان شما روی **فارسی** تنظیم شده است.",
        "region_selected": "🌍 منطقه: **{region}**. کشور خود را انتخاب کنید:",
        "country_choice": "🗣️ زبان خود را برای **{country}** انتخاب کنید:",
        "lang_updated": "✅ زبان با موفقیت به‌روزرسانی شد!",
        "ask_category": "🎉 این چه نوع جشنی است؟",
        "owner_active": "🤍 **حالت مالک فعال است!**\n\nامروز چه مناسبتی را جشن می گیریم؟ نام را بفرستید:",
        "free_remaining": "🎁 شما **{remaining}** سورپرایز رایگان دیگر دارید!",
        "free_first": "🎁 **{limit}** سورپرایز اول شما کاملاً **رایگان** است!",
        "ask_name": "امروز چه مناسبتی را جشن می گیریم؟ نام را بفرستید:",
        "ask_wish": "یک پیام تبریک صمیمی بنویسید:",
        "ask_age_mode": "چگونه می‌خواهید جزئیات سن را اضافه کنید؟",
        "ask_dob_input": "📅 تاریخ تولد را با فرمت **YYYY-MM-DD** بفرستید (مثلا: `2003-12-24`):",
        "ask_age_input": "🔢 لطفاً سن را به عنوان یک عدد وارد کنید (مثلا: `22`):",
        "ask_year": "سال را انتخاب کنید:",
        "ask_month": "ماه را انتخاب کنید:",
        "ask_date": "تاریخ را انتخاب کنید:",
        "ask_hour": "ساعت را انتخاب کنید (00-23):",
        "ask_minute": "دقیقه را انتخاب کنید (00-59):",
        "ask_photo": "عکس به اشتراک بگذارید (یا رد شوید):",
        "ask_video": "ویدیو به اشتراک بگذارید (یا رد شوید):",
        "ask_song": "آهنگ بفرستید (یا رد شوید):",
        "ask_voice": "یادداشت صوتی بفرستید (یا رد شوید):",
        "ask_audio": "فایل صوتی دیگری اضافه کنید (یا رد شوید):",
        "ready": "✨ همه چیز برای {name} آماده است!",
    },
    "my": {
        "welcome": "✨ အံ့သြစရာလေးများမှ ကြိုဆိုပါတယ်...\n\nသင့်ဘာသာစကားကို **မြန်မာ** သို့ သတ်မှတ်ထားပါသည်။",
        "region_selected": "🌍 ဒေသ: **{region}**။ သင့်နိုင်ငံကို ရွေးပါ-",
        "country_choice": "🗣️ **{country}** အတွက် ဘာသာစကားကို ရွေးပါ-",
        "lang_updated": "✅ ဘာသာစကား အောင်မြင်စွာ ပြောင်းလဲပြီးပါပြီ။",
        "ask_category": "🎉 မည်သည့်ပွဲအခမ်းအနား ဖြစ်ပါသနည်း။",
        "owner_active": "🤍 **ပိုင်ရှင်မုဒ် အလုပ်လုပ်နေသည်!**\n\nယနေ့ မည်သည့်ပွဲကို ကျင်းပနေသလဲ? အမည်ကို ပို့ပါ-",
        "free_remaining": "🎁 သင့်တွင် အခမဲ့ အံ့သြစရာ **{remaining}** ခု ကျန်ရှိပါသည်!",
        "free_first": "🎁 ပထမဆုံး **{limit}** ခုသော အံ့သြစရာများမှာ **အခမဲ့** ဖြစ်ပါသည်!",
        "ask_name": "ယနေ့ မည်သည့်ပွဲကို ကျင်းပနေသလဲ? အမည်ကို ပို့ပါ-",
        "ask_wish": "ဆုတောင်း စာတိုလေး ရေးပါ-",
        "ask_age_mode": "အသက်အချက်အလက်ကို မည်သို့ထည့်လိုသနည်း။",
        "ask_dob_input": "📅 မွေးနေ့ကို **YYYY-MM-DD** ပုံစံဖြင့် ပို့ပါ (ဥပမာ - `2003-12-24`)-",
        "ask_age_input": "🔢 အသက်ကို နံပါတ်ဖြင့် ရိုက်ထည့်ပါ (ဥပမာ - `22`)-",
        "ask_year": "ခုနှစ်ကို ရွေးပါ-",
        "ask_month": "လကို ရွေးပါ-",
        "ask_date": "ရက်စွဲကို ရွေးပါ-",
        "ask_hour": "နာရီကို ရွေးပါ (00-23):",
        "ask_minute": "မိနစ်ကို ရွေးပါ (00-59):",
        "ask_photo": "ဓာတ်ပုံမျှဝေပါ (သို့မဟုတ် ကျော်သွားပါ):",
        "ask_video": "ဗီဒီယိုမျှဝေပါ (သို့မဟုတ် ကျော်သွားပါ):",
        "ask_song": "သီချင်းပို့ပါ (သို့မဟုတ် ကျော်သွားပါ):",
        "ask_voice": "အသံဖိုင်ပို့ပါ (သို့မဟုတ် ကျော်သွားပါ):",
        "ask_audio": "အခြားအသံဖိုင် ထည့်ပါ (သို့မဟုတ် ကျော်သွားပါ):",
        "ready": "✨ {name} အတွက် အားလုံး အသင့်ဖြစ်ပါပြီ!",
    },
    "az": {
        "welcome": "✨ Sürprizlər dünyasına xoş gəlmisiniz...\n\nDiliniz **Azərbaycan dili** olaraq təyin edildi.",
        "region_selected": "🌍 Bölgə: **{region}**. Ölkənizi seçin:",
        "country_choice": "🗣️ **{country}** üçün dilinizi seçin:",
        "lang_updated": "✅ Dil seçimi uğurla yeniləndi!",
        "ask_category": "🎉 Bu hansı növ tədbirdir?",
        "owner_active": "🤍 **Sahib Rejimi Aktivdir!**\n\nBu gün nəyi qeyd edirik? Adını göndərin:",
        "free_remaining": "🎁 **{remaining}** pulsuz sürpriz haqqınız qaldı!",
        "free_first": "🎁 İlk **{limit}** sürpriziniz **PULSUZDUR**!",
        "ask_name": "Bu gün nəyi qeyd edirik? Adını göndərin:",
        "ask_wish": "Gözəl bir mesaj yazın:",
        "ask_age_mode": "Yaş məlumatlarını necə əlavə etmək istəyirsiniz?",
        "ask_dob_input": "📅 Doğum tarixini **YYYY-MM-DD** formatında göndərin (məsələn: `2003-12-24`):",
        "ask_age_input": "🔢 Yaşınızı rəqəm olaraq daxil edin (məsələn: `22`):",
        "ask_year": "İli seçin:",
        "ask_month": "Ayı seçin:",
        "ask_date": "Tarixi seçin:",
        "ask_hour": "Saatı seçin (00-23):",
        "ask_minute": "Dəqiqəni seçin (00-59):",
        "ask_photo": "Şəkil paylaşın (və ya keçin):",
        "ask_video": "Video paylaşın (və ya keçin):",
        "ask_song": "Mahnı göndərin (və ya keçin):",
        "ask_voice": "Səsli mesaj göndərin (və ya keçin):",
        "ask_audio": "Başqa audio əlavə edin (və ya keçin):",
        "ready": "✨ {name} üçün hər şey hazırdır!",
    },
    "hy": {
        "welcome": "✨ Բարի գալուստ անակնկալների աշխարհ...\n\nՁեր լեզուն սահմանված է **Հայերեն**:",
        "region_selected": "🌍 Մարզ՝ **{region}**. Ընտրեք ձեր երկիրը:",
        "country_choice": "🗣️ Ընտրեք ձեր լեզուն **{country}**-ի համար:",
        "lang_updated": "✅ Լեզվի նախընտրությունը հաջողությամբ թարմացվեց:",
        "ask_category": "🎉 Ինչպիսի՞ տոն է սա:",
        "owner_active": "🤍 **Սեփականատիրոջ ռեժիմն ակտիվ է:**\n\nԻ՞նչ ենք նշում այսօր: Ուղարկեք անունը՝",
        "free_remaining": "🎁 Դուք ունեք **{remaining}** անվճար անակնկալ հնարավորություն:",
        "free_first": "🎁 Ձեր առաջին **{limit}** անակնկալներն **ԱՆՎՃԱՐ** են:",
        "ask_name": "Ի՞նչ ենք նշում այսօր: Ուղարկեք անունը՝",
        "ask_wish": "Գրեք ջերմ մաղթանք՝",
        "ask_age_mode": "Ինչպ՞ես եք ցանկանում ավելացնել տարիքի տվյալները:",
        "ask_dob_input": "📅 Ուղարկեք ծննդյան ամսաթիվը **YYYY-MM-DD** ձևաչափով (օր.՝ `2003-12-24`):",
        "ask_age_input": "🔢 Մուտքագրեք տարիքը որպես թիվ (օր.՝ `22`):",
        "ask_year": "Ընտրեք տարին՝",
        "ask_month": "Ընտրեք ամիսը՝",
        "ask_date": "Ընտրեք ամսաթիվը՝",
        "ask_hour": "Ընտրեք ժամը (00-23)՝",
        "ask_minute": "Ընտրեք րոպեն (00-59)՝",
        "ask_photo": "Կիսվեք լուսանկարով (կամ բաց թողեք)՝",
        "ask_video": "Կիսվեք տեսանյութով (կամ բաց թողեք)՝",
        "ask_song": "Ուղարկեք երգ (կամ բաց թողեք)՝",
        "ask_voice": "Ուղարկեք ձայնային հաղորդագրություն (կամ բաց թողեք)՝",
        "ask_audio": "Ավելացրեք այլ աուդիո (կամ բաց թողեք)՝",
        "ready": "✨ Ամեն ինչ պատրաստ է {name}-ի համար:",
    },
    "be": {
        "welcome": "✨ Сардэчна запрашаем у ваш куток сюрпрызаў...\n\nВаша мова ўстаноўлена як **Беларуская**.",
        "region_selected": "🌍 Рэгіён: **{region}**. Выберыце вашу краіну:",
        "country_choice": "🗣️ Выберыце мову для **{country}**:",
        "lang_updated": "✅ Мова паспяхова абноўлена!",
        "ask_category": "🎉 Што гэта за свята?",
        "owner_active": "🤍 **Рэжым уладальніка актыўны!**\n\nШто мы сёння святкуем? Адпраўце імя:",
        "free_remaining": "🎁 У вас засталося **{remaining}** бясплатных сюрпрызаў!",
        "free_first": "🎁 Вашы першыыя **{limit}** сюрпрызаў **БЯСПЛАТНЫЯ**!",
        "ask_name": "Што мы сёння святкуем? Адпраўце імя:",
        "ask_wish": "Напішыце цёплае віншаванне:",
        "ask_age_mode": "Як вы хочаце дадаць звесткі пра ўзрост?",
        "ask_dob_input": "📅 Адпраўце дату ў фармаце **YYYY-MM-DD** (напр., `2003-12-24`):",
        "ask_age_input": "🔢 Увядзіце ўзрост лічбай (напр., `22`):",
        "ask_year": "Выберыце год:",
        "ask_month": "Выберыце месяц:",
        "ask_date": "Выберыце дату:",
        "ask_hour": "Выберыце гадзіну (00-23):",
        "ask_minute": "Выберыце хвіліну (00-59):",
        "ask_photo": "Падзяліцеся фота (або прапусціце):",
        "ask_video": "Падзяліцеся відэа (або прапусціце):",
        "ask_song": "Адпраўце песню (або прапусціце):",
        "ask_voice": "Адпраўце галасавое паведамленне (або прапусціце):",
        "ask_audio": "Дадайце яшчэ аўдыя (або прапусціце):",
        "ready": "✨ Усё гатова для {name}!",
    },
    "id": {
        "welcome": "✨ Selamat datang di sudut kejutan Anda...\n\nBahasa Anda saat ini adalah **Bahasa Indonesia**.",
        "region_selected": "🌍 Wilayah: **{region}**. Pilih negara Anda:",
        "country_choice": "🗣️ Pilih bahasa Anda untuk **{country}**:",
        "lang_updated": "✅ Preferensi bahasa berhasil diperbarui!",
        "ask_category": "🎉 Perayaan jenis apa ini?",
        "owner_active": "🤍 **Mode Pemilik Aktif!**\n\nApa yang kita rayakan hari ini? Kirim namanya:",
        "free_remaining": "🎁 Anda memiliki **{remaining}** kejutan gratis yang tersisa!",
        "free_first": "🎁 **{limit}** kejutan pertama Anda adalah **GRATIS**!",
        "ask_name": "Apa yang kita rayakan hari ini? Kirim namanya:",
        "ask_wish": "Tulis ucapan yang manis:",
        "ask_age_mode": "Bagaimana Anda ingin menambahkan detail usia?",
        "ask_dob_input": "📅 Silakan kirim Tanggal dalam format **YYYY-MM-DD** (cth. `2003-12-24`):",
        "ask_age_input": "🔢 Silakan masukkan usia sebagai angka (cth. `22`):",
        "ask_year": "Pilih tahun:",
        "ask_month": "Pilih bulan:",
        "ask_date": "Pilih tanggal:",
        "ask_hour": "Pilih jam (00-23):",
        "ask_minute": "Pilih menit (00-59):",
        "ask_photo": "Bagikan foto (atau lewati):",
        "ask_video": "Bagikan video (atau lewati):",
        "ask_song": "Kirim lagu (atau lewati):",
        "ask_voice": "Kirim catatan suara (atau lewati):",
        "ask_audio": "Tambahkan audio lain (atau lewati):",
        "ready": "✨ Semuanya siap untuk {name}!",
    },
    "tr": {
        "welcome": "✨ Sürprizler köşenize hoş geldiniz...\n\nDiliniz şu anda **Türkçe** olarak ayarlandı.",
        "region_selected": "🌍 Bölge: **{region}**. Ülkenizi seçin:",
        "country_choice": "🗣️ **{country}** için dilinizi seçin:",
        "lang_updated": "✅ Dil tercihi başarıyla güncellendi!",
        "ask_category": "🎉 Bu nasıl bir kutlama?",
        "owner_active": "🤍 **Sahip Modu Aktif!**\n\nBugün neyi kutluyoruz? Adını gönderin:",
        "free_remaining": "🎁 Kalan **{remaining}** ücretsiz sürpriziniz var!",
        "free_first": "🎁 İlk **{limit}** sürpriziniz **ÜCRETSİZ**!",
        "ask_name": "Bugün neyi kutluyoruz? Adını gönderin:",
        "ask_wish": "Tatlı bir mesaj yazın:",
        "ask_age_mode": "Yaş detaylarını nasıl eklemek istersiniz?",
        "ask_dob_input": "📅 Lütfen Tarihi **YYYY-MM-DD** formatında gönderin (örn. `2003-12-24`):",
        "ask_age_input": "🔢 Lütfen yaşı bir sayı olarak girin (örn. `22`):",
        "ask_year": "Yılı seçin:",
        "ask_month": "Ayı seçin:",
        "ask_date": "Tarihi seçin:",
        "ask_hour": "Saati seçin (00-23):",
        "ask_minute": "Dakikayı seçin (00-59):",
        "ask_photo": "Fotoğraf paylaşın (veya atlayın):",
        "ask_video": "Video paylaşın (veya atlayın):",
        "ask_song": "Şarkı gönderin (veya atlayın):",
        "ask_voice": "Sesli mesaj gönderin (veya atlayın):",
        "ask_audio": "Başka bir ses ekleyin (veya atlayın):",
        "ready": "✨ {name} için her şey hazır!",
    },
    "pt": {
        "welcome": "✨ Bem-vindo ao seu cantinho de surpresas...\n\nSeu idioma está definido como **Português**.",
        "region_selected": "🌍 Região: **{region}**. Selecione seu país:",
        "country_choice": "🗣️ Escolha seu idioma para **{country}**:",
        "lang_updated": "✅ Preferência de idioma atualizada com sucesso!",
        "ask_category": "🎉 Que tipo de celebração é esta?",
        "owner_active": "🤍 **Modo Proprietário Ativo!**\n\nO que estamos celebrando hoje? Envie o nome:",
        "free_remaining": "🎁 Você tem **{remaining}** surpresa(s) gratuita(s)!",
        "free_first": "🎁 Suas primeiras **{limit}** surpresas são **GRÁTIS**!",
        "ask_name": "O que estamos celebrando hoje? Envie o nome:",
        "ask_wish": "Escreva uma mensagem carinhosa:",
        "ask_age_mode": "Como você gostaria de adicionar os detalhes?",
        "ask_dob_input": "📅 Envie a Data no formato **YYYY-MM-DD** (ex: `2003-12-24`):",
        "ask_age_input": "🔢 Digite a idade diretamente como número (ex: `22`):",
        "ask_year": "Escolha o ano:",
        "ask_month": "Escolha o mês:",
        "ask_date": "Escolha a data:",
        "ask_hour": "Selecione a hora (00-23):",
        "ask_minute": "Selecione o minuto (00-59):",
        "ask_photo": "Compartilhe uma foto (ou pule):",
        "ask_video": "Compartilhe um vídeo (ou pule):",
        "ask_song": "Envie uma música (ou pule):",
        "ask_voice": "Envie uma nota de voz (ou pule):",
        "ask_audio": "Adicione outro áudio (ou pule):",
        "ready": "✨ Tudo pronto para {name}!",
    },
    "uk": {
        "welcome": "✨ Ласкаво просимо у ваш куточок сюрпризів...\n\nВаша мова: **Українська**.",
        "region_selected": "🌍 Регіон: **{region}**. Виберіть вашу країну:",
        "country_choice": "🗣️ Виберіть мову для **{country}**:",
        "lang_updated": "✅ Мову успішно оновлено!",
        "ask_category": "🎉 Що це за свято?",
        "owner_active": "🤍 **Режим власника активний!**\n\nЩо ми сьогодні святкуємо? Надішліть ім'я:",
        "free_remaining": "🎁 У вас залишилось **{remaining}** безкоштовних сюрпризів!",
        "free_first": "🎁 Ваші перші **{limit}** сюрпризів **безкоштовні**!",
        "ask_name": "Що ми сьогодні святкуємо? Надішліть ім'я:",
        "ask_wish": "Напишіть тепле привітання:",
        "ask_age_mode": "Як ви хочете додати дані про вік?",
        "ask_dob_input": "📅 Надішліть дату у форматі **YYYY-MM-DD** (напр., `2003-12-24`):",
        "ask_age_input": "🔢 Введіть вік числом (напр., `22`):",
        "ask_year": "Виберіть рік:",
        "ask_month": "Виберіть місяць:",
        "ask_date": "Виберіть дату:",
        "ask_hour": "Виберіть годину (00-23):",
        "ask_minute": "Виберіть хвилину (00-59):",
        "ask_photo": "Поділіться фото (або пропустіть):",
        "ask_video": "Поділіться відео (або пропустіть):",
        "ask_song": "Надішліть пісню (або пропустіть):",
        "ask_voice": "Надішліть голосове повідомлення (або пропустіть):",
        "ask_audio": "Додайте ще аудіо (або пропустіть):",
        "ready": "✨ Все готово для {name}!",
    },
    "fi": {
        "welcome": "✨ Tervetuloa yllätysten nurkkaan...\n\nKielesi on asetettu **suomeksi**.",
        "region_selected": "🌍 Alue: **{region}**. Valitse maasi:",
        "country_choice": "🗣️ Valitse kieli maalle **{country}**:",
        "lang_updated": "✅ Kieliasetus päivitetty onnistuneesti!",
        "ask_category": "🎉 Millainen juhla tämä on?",
        "owner_active": "🤍 **Omistajatila aktiivinen!**\n\nMitä juhlimme tänään? Lähetä nimi:",
        "free_remaining": "🎁 Sinulla on **{remaining}** ilmainen yllätys jäljellä!",
        "free_first": "🎁 Ensimmäiset **{limit}** yllätystäsi ovat **ILMAISIA**!",
        "ask_name": "Mitä juhlimme tänään? Lähetä nimi:",
        "ask_wish": "Kirjoita lämmin toivotus:",
        "ask_age_mode": "Miten haluat lisätä ikätiedot?",
        "ask_dob_input": "📅 Lähetä päivämäärä muodossa **YYYY-MM-DD** (esim. `2003-12-24`):",
        "ask_age_input": "🔢 Anna suora ikä numerona (esim. `22`):",
        "ask_year": "Valitse vuosi:",
        "ask_month": "Valitse kuukausi:",
        "ask_date": "Valitse päivämäärä:",
        "ask_hour": "Valitse tunti (00-23):",
        "ask_minute": "Valitse minuutti (00-59):",
        "ask_photo": "Jaa kuva (tai ohita):",
        "ask_video": "Jaa video (tai ohita):",
        "ask_song": "Lähetä kappale (tai ohita):",
        "ask_voice": "Lähetä ääniviesti (tai ohita):",
        "ask_audio": "Lisää toinen ääni (tai ohita):",
        "ready": "✨ Kaikki valmista {name} varten!",
    },
    "nl": {
        "welcome": "✨ Welkom in je kleine hoekje vol verrassingen...\n\nJe taal is ingesteld op **Nederlands**.",
        "region_selected": "🌍 Regio: **{region}**. Selecteer je land:",
        "country_choice": "🗣️ Kies je taal voor **{country}**:",
        "lang_updated": "✅ Taalvoorkeur succesvol bijgewerkt!",
        "ask_category": "🎉 Wat voor soort feest is dit?",
        "owner_active": "🤍 **Eigenaarmodus actief!**\n\nWat vieren we vandaag? Stuur de naam:",
        "free_remaining": "🎁 Je hebt nog **{remaining}** gratis verrassing(en)!",
        "free_first": "🎁 Je eerste **{limit}** verrassingen zijn **GRATIS**!",
        "ask_name": "Wat vieren we vandaag? Stuur de naam:",
        "ask_wish": "Schrijf een lieve wens:",
        "ask_age_mode": "Hoe wil je de leeftijdsgegevens toevoegen?",
        "ask_dob_input": "📅 Stuur de datum in **YYYY-MM-DD** formaat (bijv. `2003-12-24`):",
        "ask_age_input": "🔢 Voer de leeftijd in als getal (bijv. `22`):",
        "ask_year": "Kies het jaar:",
        "ask_month": "Kies de maand:",
        "ask_date": "Kies de datum:",
        "ask_hour": "Selecteer het uur (00-23):",
        "ask_minute": "Selecteer de minuut (00-59):",
        "ask_photo": "Deel een foto (of sla over):",
        "ask_video": "Deel een video (of sla over):",
        "ask_song": "Stuur een liedje (of sla over):",
        "ask_voice": "Stuur een spraakbericht (of sla over):",
        "ask_audio": "Voeg nog een audio toe (of sla over):",
        "ready": "✨ Alles klaar voor {name}!",
    },
    "pl": {
        "welcome": "✨ Witaj w swoim małym kąciku niespodzianek...\n\nTwój język to **Polski**.",
        "region_selected": "🌍 Region: **{region}**. Wybierz swój kraj:",
        "country_choice": "🗣️ Wybierz język dla **{country}**:",
        "lang_updated": "✅ Pomyślnie zaktualizowano preferencje językowe!",
        "ask_category": "🎉 Co to za święto?",
        "owner_active": "🤍 **Tryb właściciela aktywny!**\n\nCo dzisiaj świętujemy? Wyślij imię:",
        "free_remaining": "🎁 Masz jeszcze **{remaining}** darmowych niespodzianek!",
        "free_first": "🎁 Twoje pierwsze **{limit}** niespodzianek jest **DARMOWYCH**!",
        "ask_name": "Co dzisiaj świętujemy? Wyślij imię:",
        "ask_wish": "Napisz miłe życzenia:",
        "ask_age_mode": "Jak chcesz dodać szczegóły wieku?",
        "ask_dob_input": "📅 Wyślij datę w formacie **YYYY-MM-DD** (np. `2003-12-24`):",
        "ask_age_input": "🔢 Wprowadź wiek jako liczbę (np. `22`):",
        "ask_year": "Wybierz rok:",
        "ask_month": "Wybierz miesiąc:",
        "ask_date": "Wybierz datę:",
        "ask_hour": "Wybierz godzinę (00-23):",
        "ask_minute": "Wybierz minutę (00-59):",
        "ask_photo": "Udostępnij zdjęcie (lub pomiń):",
        "ask_video": "Udostępnij wideo (lub pomiń):",
        "ask_song": "Wyślij piosenkę (lub pomiń):",
        "ask_voice": "Wyślij wiadomość głosową (lub pomiń):",
        "ask_audio": "Dodaj kolejne audio (lub pomiń):",
        "ready": "✨ Wszystko gotowe dla {name}!",
    },
    "sv": {
        "welcome": "✨ Välkommen till din lilla hörna av överraskningar...\n\nDitt språk är inställt på **Svenska**.",
        "region_selected": "🌍 Region: **{region}**. Välj ditt land:",
        "country_choice": "🗣️ Välj ditt språk för **{country}**:",
        "lang_updated": "✅ Språkinställningen har uppdaterats!",
        "ask_category": "🎉 Vad är det för firande?",
        "owner_active": "🤍 **Ägarläge aktivt!**\n\nVad firar vi idag? Skicka namnet:",
        "free_remaining": "🎁 Du har **{remaining}** gratis överraskningar kvar!",
        "free_first": "🎁 Dina första **{limit}** överraskningar är **GRATIS**!",
        "ask_name": "Vad firar vi idag? Skicka namnet:",
        "ask_wish": "Skriv en fin hälsning:",
        "ask_age_mode": "Hur vill du lägga till åldersdetaljer?",
        "ask_dob_input": "📅 Skicka datum i formatet **YYYY-MM-DD** (t.ex. `2003-12-24`):",
        "ask_age_input": "🔢 Ange ålder direkt som ett nummer (t.ex. `22`):",
        "ask_year": "Välj år:",
        "ask_month": "Välj månad:",
        "ask_date": "Välj datum:",
        "ask_hour": "Välj timme (00-23):",
        "ask_minute": "Välj minut (00-59):",
        "ask_photo": "Dela ett foto (eller hoppa över):",
        "ask_video": "Dela en video (eller hoppa över):",
        "ask_song": "Skicka en låt (eller hoppa över):",
        "ask_voice": "Skicka ett röstmeddelande (eller hoppa över):",
        "ask_audio": "Lägg till ett ljud till (eller hoppa över):",
        "ready": "✨ Allt klart för {name}!",
    },
    "no": {
        "welcome": "✨ Velkommen til ditt lille hjørne av overraskelser...\n\nSpråket ditt er satt til **Norsk**.",
        "region_selected": "🌍 Region: **{region}**. Velg landet ditt:",
        "country_choice": "🗣️ Velg språk for **{country}**:",
        "lang_updated": "✅ Språkvalg oppdatert!",
        "ask_category": "🎉 Hva slags feiring er dette?",
        "owner_active": "🤍 **Eiermodus aktiv!**\n\nHva feirer vi i dag? Send navnet:",
        "free_remaining": "🎁 Du har **{remaining}** gratis overraskelser igjen!",
        "free_first": "🎁 Dine første **{limit}** overraskelser er **GRATIS**!",
        "ask_name": "Hva feirer vi i dag? Send navnet:",
        "ask_wish": "Skriv en fin hilsen:",
        "ask_age_mode": "Hvordan vil du legge til aldersdetaljer?",
        "ask_dob_input": "📅 Send dato i formatet **YYYY-MM-DD** (f.eks. `2003-12-24`):",
        "ask_age_input": "🔢 Angi alder direkte som et tall (f.eks. `22`):",
        "ask_year": "Velg år:",
        "ask_month": "Velg måned:",
        "ask_date": "Velg dato:",
        "ask_hour": "Velg time (00-23):",
        "ask_minute": "Velg minutt (00-59):",
        "ask_photo": "Del et foto (eller hopp over):",
        "ask_video": "Del en video (eller hopp over):",
        "ask_song": "Send en sang (eller hopp over):",
        "ask_voice": "Send et talenotat (eller hopp over):",
        "ask_audio": "Legg til en lyd til (eller hopp over):",
        "ready": "✨ Alt klar for {name}!",
    },
    "da": {
        "welcome": "✨ Velkommen til dit lille hjørne af overraskelser...\n\nDit sprog er sat til **Dansk**.",
        "region_selected": "🌍 Region: **{region}**. Vælg dit land:",
        "country_choice": "🗣️ Vælg dit sprog for **{country}**:",
        "lang_updated": "✅ Sprogvalg opdateret!",
        "ask_category": "🎉 Hvad er det for en fejring?",
        "owner_active": "🤍 **Ejertilstand aktiv!**\n\nHvad fejrer vi i dag? Send navnet:",
        "free_remaining": "🎁 Du har **{remaining}** gratis overraskelser tilbage!",
        "free_first": "🎁 Dine første **{limit}** overraskelser er **GRATIS**!",
        "ask_name": "Hvad fejrer vi i dag? Send navnet:",
        "ask_wish": "Skriv en sød hilsen:",
        "ask_age_mode": "Hvordan vil du tilføje aldersdetaljer?",
        "ask_dob_input": "📅 Send dato i formatet **YYYY-MM-DD** (f.eks. `2003-12-24`):",
        "ask_age_input": "🔢 Indtast alderen direkte som et tal (f.eks. `22`):",
        "ask_year": "Vælg år:",
        "ask_month": "Vælg måned:",
        "ask_date": "Vælg dato:",
        "ask_hour": "Vælg time (00-23):",
        "ask_minute": "Vælg minut (00-59):",
        "ask_photo": "Del et foto (eller spring over):",
        "ask_video": "Del en video (eller spring over):",
        "ask_song": "Send en sang (eller spring over):",
        "ask_voice": "Send en stemmebesked (eller spring over):",
        "ask_audio": "Tilføj en lyd mere (eller spring over):",
        "ready": "✨ Alt klar til {name}!",
    },
    "el": {
        "welcome": "✨ Καλώς ήρθατε στη μικρή σας γωνιά έκπληξης...\n\nΗ γλώσσα σας έχει οριστεί σε **Ελληνικά**.",
        "region_selected": "🌍 Περιοχή: **{region}**. Επιλέξτε τη χώρα σας:",
        "country_choice": "🗣️ Επιλέξτε τη γλώσσα σας για **{country}**:",
        "lang_updated": "✅ Η προτίμηση γλώσσας ενημερώθηκε επιτυχώς!",
        "ask_category": "🎉 Τι είδους γιορτή είναι αυτή;",
        "owner_active": "🤍 **Ενεργή λειτουργία κατόχου!**\n\nΤι γιορτάζουμε σήμερα; Στείλτε το όνομα:",
        "free_remaining": "🎁 Έχετε **{remaining}** δωρεάν έκπληξη/εις απομείνει!",
        "free_first": "🎁 Οι πρώτες **{limit}** εκπλήξεις σας είναι **ΔΩΡΕΑΝ**!",
        "ask_name": "Τι γιορτάζουμε σήμερα; Στείλτε το όνομα:",
        "ask_wish": "Γράψτε ένα γλυκό μήνυμα:",
        "ask_age_mode": "Πώς θα θέλατε να προσθέσετε λεπτομέρειες;",
        "ask_dob_input": "📅 Στείλτε την ημερομηνία σε μορφή **YYYY-MM-DD** (π.χ. `2003-12-24`):",
        "ask_age_input": "🔢 Εισαγάγετε απευθείας την ηλικία ως αριθμό (π.χ. `22`):",
        "ask_year": "Επιλέξτε έτος:",
        "ask_month": "Επιλέξτε μήνα:",
        "ask_date": "Επιλέξτε ημερομηνία:",
        "ask_hour": "Επιλέξτε ώρα (00-23):",
        "ask_minute": "Επιλέξτε λεπτό (00-59):",
        "ask_photo": "Μοιραστείτε φωτογραφία (ή παράλειψη):",
        "ask_video": "Μοιραστείτε βίντεο (ή παράλειψη):",
        "ask_song": "Στείλτε τραγούδι (ή παράλειψη):",
        "ask_voice": "Στείλτε φωνητικό μήνυμα (ή παράλειψη):",
        "ask_audio": "Προσθέστε άλλο ήχο (ή παράλειψη):",
        "ready": "✨ Όλα έτοιμα για το/τη {name}!",
    },
    "cs": {
        "welcome": "✨ Vítejte ve svém malém koutku překvapení...\n\nJazyk je nastaven na **Češtinu**.",
        "region_selected": "🌍 Region: **{region}**. Vyberte svou zemi:",
        "country_choice": "🗣️ Vyberte jazyk pro **{country}**:",
        "lang_updated": "✅ Jazykové předvolby byly úspěšně aktualizovány!",
        "ask_category": "🎉 O jakou oslavu se jedná?",
        "owner_active": "🤍 **Režim vlastníka aktivní!**\n\nCo dnes slavíme? Pošlete jméno:",
        "free_remaining": "🎁 Zbývá vám **{remaining}** bezplatných překvapení!",
        "free_first": "🎁 Vašich prvních **{limit}** překvapení je **ZDARMA**!",
        "ask_name": "Co dnes slavíme? Pošlete jméno:",
        "ask_wish": "Napište milé přání:",
        "ask_age_mode": "Jak chcete přidat údaje?",
        "ask_dob_input": "📅 Pošlete datum ve formátu **YYYY-MM-DD** (např. `2003-12-24`):",
        "ask_age_input": "🔢 Zadejte věk přímo jako číslo (např. `22`):",
        "ask_year": "Vyberte rok:",
        "ask_month": "Vyberte měsíc:",
        "ask_date": "Vyberte datum:",
        "ask_hour": "Vyberte hodinu (00-23):",
        "ask_minute": "Vyberte minutu (00-59):",
        "ask_photo": "Sdílejte fotku (nebo přeskočte):",
        "ask_video": "Sdílejte video (nebo přeskočte):",
        "ask_song": "Pošlete písničku (nebo přeskočte):",
        "ask_voice": "Pošlete hlasovou zprávu (nebo přeskočte):",
        "ask_audio": "Přidejte další audio (nebo přeskočte):",
        "ready": "✨ Vše je připraveno pro {name}!",
    },
    "hu": {
        "welcome": "✨ Üdvözöllek a meglepetések kis világában...\n\nA nyelved beállítása: **Magyar**.",
        "region_selected": "🌍 Régió: **{region}**. Válaszd ki az országodat:",
        "country_choice": "🗣️ Válaszd ki a nyelvet ehhez: **{country}**:",
        "lang_updated": "✅ Nyelvi beállítás sikeresen frissítve!",
        "ask_category": "🎉 Milyen ünnepség ez?",
        "owner_active": "🤍 **Tulajdonos mód aktív!**\n\nMit ünnepelünk ma? Küldd el a nevet:",
        "free_remaining": "🎁 Még **{remaining}** ingyenes meglepetésed van!",
        "free_first": "🎁 Az első **{limit}** meglepetésed **INGYENES**!",
        "ask_name": "Mit ünnepelünk ma? Küldd el a nevet:",
        "ask_wish": "Írj egy kedves üzenetet:",
        "ask_age_mode": "Hogyan szeretnéd hozzáadni az adatokat?",
        "ask_dob_input": "📅 Kérlek küldd el a dátumot **YYYY-MM-DD** formátumban (pl. `2003-12-24`):",
        "ask_age_input": "🔢 Kérlek add meg a kort számként (pl. `22`):",
        "ask_year": "Vlaszd ki az évet:",
        "ask_month": "Válaszd ki a hónapot:",
        "ask_date": "Válaszd ki a napot:",
        "ask_hour": "Válaszd ki az órát (00-23):",
        "ask_minute": "Válaszd ki a percet (00-59):",
        "ask_photo": "Ossz meg egy fotót (vagy ugord át):",
        "ask_video": "Ossz meg egy videót (vagy ugord át):",
        "ask_song": "Küldj egy dalt (vagy ugord át):",
        "ask_voice": "Küldj hangüzenetet (vagy ugord át):",
        "ask_audio": "Adj hozzá még egy audiót (vagy ugord át):",
        "ready": "✨ Minden kész {name} számára!",
    },
    "ro": {
        "welcome": "✨ Bine ai venit în colțul tău de surprize...\n\nLimba ta este setată pe **Română**.",
        "region_selected": "🌍 Regiune: **{region}**. Selectează țara ta:",
        "country_choice": "🗣️ Alege limba pentru **{country}**:",
        "lang_updated": "✅ Preferința de limbă a fost actualizată cu succes!",
        "ask_category": "🎉 Ce fel de sărbătoare este aceasta?",
        "owner_active": "🤍 **Mod Proprietar Activ!**\n\nCe sărbătorim azi? Trimite numele:",
        "free_remaining": "🎁 Mai ai **{remaining}** surprize gratuite!",
        "free_first": "🎁 Primele **{limit}** surprize sunt **GRATUITE**!",
        "ask_name": "Ce sărbătorim azi? Trimite numele:",
        "ask_wish": "Scrie un mesaj frumos:",
        "ask_age_mode": "Cum dorești să adaugi detaliile?",
        "ask_dob_input": "📅 Trimite data în formatul **YYYY-MM-DD** (de ex. `2003-12-24`):",
        "ask_age_input": "🔢 Introdu vârsta direct ca număr (de ex. `22`):",
        "ask_year": "Alege anul:",
        "ask_month": "Alege luna:",
        "ask_date": "Alege data:",
        "ask_hour": "Selectează ora (00-23):",
        "ask_minute": "Selectează minutul (00-59):",
        "ask_photo": "Distribuie o poză (sau sari peste):",
        "ask_video": "Distribuie un video (sau sari peste):",
        "ask_song": "Trimite o melodie (sau sari peste):",
        "ask_voice": "Trimite o notă vocală (sau sari peste):",
        "ask_audio": "Adaugă încă un audio (sau sari peste):",
        "ready": "✨ Totul este pregătit pentru {name}!",
    },
    "hr": {
        "welcome": "✨ Dobrodošli u svoj mali kutak iznenađenja...\n\nVaš jezik je postavljen na **Hrvatski**.",
        "region_selected": "🌍 Regija: **{region}**. Odaberite svoju zemlju:",
        "country_choice": "🗣️ Odaberite jezik za **{country}**:",
        "lang_updated": "✅ Jezična preferencija uspješno ažurirana!",
        "ask_category": "🎉 Kakva je ovo proslava?",
        "owner_active": "🤍 **Način vlasnika aktivan!**\n\nŠto danas slavimo? Pošaljite ime:",
        "free_remaining": "🎁 Imate još **{remaining}** besplatnih iznenađenja!",
        "free_first": "🎁 Vaših prvih **{limit}** iznenađenja je **BESPLATNO**!",
        "ask_name": "Što danas slavimo? Pošaljite ime:",
        "ask_wish": "Napišite lijepu čestitku:",
        "ask_age_mode": "Kako želite dodati detalje?",
        "ask_dob_input": "📅 Pošaljite datum u formatu **YYYY-MM-DD** (npr. `2003-12-24`):",
        "ask_age_input": "🔢 Unesite dob kao broj (npr. `22`):",
        "ask_year": "Odaberite godinu:",
        "ask_month": "Odaberite mjesec:",
        "ask_date": "Odaberite datum:",
        "ask_hour": "Odaberite sat (00-23):",
        "ask_minute": "Odaberite minutu (00-59):",
        "ask_photo": "Podijelite fotografiju (ili preskočite):",
        "ask_video": "Podijelite video (ili preskočite):",
        "ask_song": "Pošaljite pjesmu (ili preskočite):",
        "ask_voice": "Pošaljite glasovnu poruku (ili preskočite):",
        "ask_audio": "Dodajte još jedan audio (ili preskočite):",
        "ready": "✨ Sve je spremno za {name}!",
    },
    "sk": {
        "welcome": "✨ Vitajte vo svom malom kútiku prekvapení...\n\nJazyk je nastavený na **Slovenčinu**.",
        "region_selected": "🌍 Región: **{region}**. Vyberte svoju krajinu:",
        "country_choice": "🗣️ Vyberte jazyk pre **{country}**:",
        "lang_updated": "✅ Jazykové predvoľby boli úspešne aktualizované!",
        "ask_category": "🎉 O akú oslavu ide?",
        "owner_active": "🤍 **Režim vlastníka aktívny!**\n\nČo dnes oslavujeme? Pošlite meno:",
        "free_remaining": "🎁 Zostáva vám **{remaining}** bezplatných prekvapení!",
        "free_first": "🎁 Vašich prvých **{limit}** prekvapení je **ZADARMO**!",
        "ask_name": "Čo dnes oslavujeme? Pošlite meno:",
        "ask_wish": "Napíšte milé prianie:",
        "ask_age_mode": "Ako chcete pridať údaje?",
        "ask_dob_input": "📅 Pošlite dátum vo formáte **YYYY-MM-DD** (napr. `2003-12-24`):",
        "ask_age_input": "🔢 Zadajte vek priamo ako číslo (napr. `22`):",
        "ask_year": "Vyberte rok:",
        "ask_month": "Vyberte mesiac:",
        "ask_date": "Vyberte dátum:",
        "ask_hour": "Vyberte hodinu (00-23):",
        "ask_minute": "Vyberte minútu (00-59):",
        "ask_photo": "Zdieľajte fotku (alebo preskočte):",
        "ask_video": "Zdieľajte video (alebo preskočte):",
        "ask_song": "Pošlite pesničku (alebo preskočte):",
        "ask_voice": "Pošlite hlasovую správu (alebo preskočte):",
        "ask_audio": "Pridajte ďalšie audio (alebo preskočte):",
        "ready": "✨ Všetko je pripravené pre {name}!",
    },
    "bg": {
        "welcome": "✨ Добре дошли в малкия си кът за изненади...\n\nВашият език е зададен на **Български**.",
        "region_selected": "🌍 Регион: **{region}**. Изберете вашата държава:",
        "country_choice": "🗣️ Изберете език за **{country}**:",
        "lang_updated": "✅ Езиковите предпочитания са обновени успешно!",
        "ask_category": "🎉 Какъв празник е това?",
        "owner_active": "🤍 **Режимът на собственик е активен!**\n\nКакво празнуваме днес? Изпратете име:",
        "free_remaining": "🎁 Имате оставащи **{remaining}** безплатни изненади!",
        "free_first": "🎁 Вашите първи **{limit}** изненади са **БЕЗПЛАТНИ**!",
        "ask_name": "Какво празнуваме днес? Изпратете име:",
        "ask_wish": "Напишете мило пожелание:",
        "ask_age_mode": "Как искате да добавите детайли?",
        "ask_dob_input": "📅 Изпратете дата във формат **YYYY-MM-DD** (напр. `2003-12-24`):",
        "ask_age_input": "🔢 Въведете възрастта като число (напр. `22`):",
        "ask_year": "Изберете година:",
        "ask_month": "Изберете месец:",
        "ask_date": "Изберете дата:",
        "ask_hour": "Изберете час (00-23):",
        "ask_minute": "Изберете минута (00-59):",
        "ask_photo": "Споделете снимка (или пропуснете):",
        "ask_video": "Споделете видео (или пропуснете):",
        "ask_song": "Изпратете песен (или пропуснете):",
        "ask_voice": "Изпратете гласово съобщение (или пропуснете):",
        "ask_audio": "Добавете друго аудио (или пропуснете):",
        "ready": "✨ Всичко е готово за {name}!",
    },
    "sr": {
        "welcome": "✨ Dobrodošli u svoj mali kutak iznenađenja...\n\nVaš jezik je podešen na **Srpski**.",
        "region_selected": "🌍 Region: **{region}**. Izaberite svoju zemlju:",
        "country_choice": "🗣️ Izaberite jezik za **{country}**:",
        "lang_updated": "✅ Jezička podešavanja su uspešno ažurirana!",
        "ask_category": "🎉 Kakva je ovo proslava?",
        "owner_active": "🤍 **Režim vlasnika aktivan!**\n\nŠta danas slavimo? Pošaljite ime:",
        "free_remaining": "🎁 Imate još **{remaining}** besplatnih iznenađenja!",
        "free_first": "🎁 Vaših prvih **{limit}** iznenađenja je **BESPLATNO**!",
        "ask_name": "Šta danas slavimo? Pošaljite ime:",
        "ask_wish": "Napišite lepu čestitku:",
        "ask_age_mode": "Kako želite da dodate detalje?",
        "ask_dob_input": "📅 Pošaljite datum u formatu **YYYY-MM-DD** (npr. `2003-12-24`):",
        "ask_age_input": "🔢 Unesite starost kao broj (npr. `22`):",
        "ask_year": "Izaberite godinu:",
        "ask_month": "Izaberite mesec:",
        "ask_date": "Izaberite datum:",
        "ask_hour": "Izaberite sat (00-23):",
        "ask_minute": "Izaberite minut (00-59):",
        "ask_photo": "Podelite fotografiju (ili preskočite):",
        "ask_video": "Podelite video (ili preskočite):",
        "ask_song": "Pošaljite pesmu (ili preskočite):",
        "ask_voice": "Pošaljite glasovnu poruku (ili preskočite):",
        "ask_audio": "Dodajte još jedan audio (ili preskočite):",
        "ready": "✨ Sve je spremno za {name}!",
    },
    "sl": {
        "welcome": "✨ Dobrodošli v svojem malem kotičku presenečenj...\n\nVaš jezik je nastavljen na **Slovenščino**.",
        "region_selected": "🌍 Regija: **{region}**. Izberite svojo državo:",
        "country_choice": "🗣️ Izberite jezik za **{country}**:",
        "lang_updated": "✅ Jezikovna nastavitev je bila uspešno posodobljena!",
        "ask_category": "🎉 Kakšna praznovanje je to?",
        "owner_active": "🤍 **Način lastnika aktiven!**\n\nKaj praznujemo danes? Pošljite ime:",
        "free_remaining": "🎁 Imate še **{remaining}** brezplačnih presenečenj!",
        "free_first": "🎁 Vaših prvih **{limit}** presenečenj je **BREZPLAČNIH**!",
        "ask_name": "Kaj praznujemo danes? Pošljite ime:",
        "ask_wish": "Napišite lepo voščilo:",
        "ask_age_mode": "Kako želite dodati podatke?",
        "ask_dob_input": "📅 Pošljite datum v formatu **YYYY-MM-DD** (npr. `2003-12-24`):",
        "ask_age_input": "🔢 Vnesite starost kot številko (npr. `22`):",
        "ask_year": "Izberite leto:",
        "ask_month": "Izberite mesec:",
        "ask_date": "Izberite datum:",
        "ask_hour": "Izberite uro (00-23):",
        "ask_minute": "Izberite minuto (00-59):",
        "ask_photo": "Delite fotografijo (ali preskočite):",
        "ask_video": "Delite video (ali preskočite):",
        "ask_song": "Pošljite pesem (ali preskočite):",
        "ask_voice": "Pošljite glasovno sporočilo (ali preskočite):",
        "ask_audio": "Dodajte drug zvok (ali preskočite):",
        "ready": "✨ Vse je pripravljeno za {name}!",
    },
    "lt": {
        "welcome": "✨ Sveiki atvykę į savo mažą staigmenų kampelį...\n\nJūsų kalba nustatyta į **Lietuvių**.",
        "region_selected": "🌍 Regionas: **{region}**. Pasirinkite savo šalį:",
        "country_choice": "🗣️ Pasirinkite kalbą **{country}** šaliai:",
        "lang_updated": "✅ Kalbos nustatymai sėkmingai atnaujinti!",
        "ask_category": "🎉 Kokia čia šventė?",
        "owner_active": "🤍 **Savininko režimas aktyvus!**\n\nKą šiandien švenčiame? Atsiųskite vardą:",
        "free_remaining": "🎁 Turite likusias **{remaining}** nemokamas staigmenas!",
        "free_first": "🎁 Jūsų pirmosios **{limit}** staigmos yra **NEMOKAMOS**!",
        "ask_name": "Ką šiandien švenčiame? Atsiųskite vardą:",
        "ask_wish": "Parašykite gražų sveikinimą:",
        "ask_age_mode": "Kaip norite pridėti duomenis?",
        "ask_dob_input": "📅 Atsiųskite datą formatu **YYYY-MM-DD** (pvz. `2003-12-24`):",
        "ask_age_input": "🔢 Įveskite amžių skaičiumi (pvz. `22`):",
        "ask_year": "Pasirinkite metus:",
        "ask_month": "Pasirinkite mėnesį:",
        "ask_date": "Pasirinkite datą:",
        "ask_hour": "Pasirinkite valandą (00-23):",
        "ask_minute": "Pasirinkite minutę (00-59):",
        "ask_photo": "Bendrinkite nuotrauką (arba praleiskite):",
        "ask_video": "Bendrinkite vaizdo įrašą (arba praleiskite):",
        "ask_song": "Atsiųskite dainą (arba praleiskite):",
        "ask_voice": "Atsiųskite balso žinutę (arba praleiskite):",
        "ask_audio": "Pridėkite kitą garso įrašą (arba praleiskite):",
        "ready": "✨ Viskas paruošta {name}!",
    },
    "lv": {
        "welcome": "✨ Laipni lūdzam jūsu mazo pārsteigumu stūrītī...\n\nJūsu valoda ir iestatīta uz **Latviešu**.",
        "region_selected": "🌍 Reģions: **{region}**. Izvēlieties savu valsti:",
        "country_choice": "🗣️ Izvēlieties valodu priekš **{country}**:",
        "lang_updated": "✅ Valodas iestatījumi veiksmīgi atjaunināti!",
        "ask_category": "🎉 Kādi svētki tie ir?",
        "owner_active": "🤍 **Īpašnieka režīms aktīvs!**\n\nKo mēs šodien svinam? Atsūtiet vārdu:",
        "free_remaining": "🎁 Jums ir atlikuši **{remaining}** bezmaksas pārsteigumi!",
        "free_first": "🎁 Jūsu pirmie **{limit}** pārsteigumi ir **BEZMAKSAS**!",
        "ask_name": "Ko mēs šodien svinam? Atsūtiet vārdu:",
        "ask_wish": "Uzrakstiet jauku vēlējumu:",
        "ask_age_mode": "Kā jūs vēlaties pievienot informāciju?",
        "ask_dob_input": "📅 Nosūtiet datumu formātā **YYYY-MM-DD** (piem. `2003-12-24`):",
        "ask_age_input": "🔢 Ievadiet vecumu kā skaitli (piem. `22`):",
        "ask_year": "Izvēlieties gadu:",
        "ask_month": "Izvēlieties mēnesi:",
        "ask_date": "Izvēlieties datumu:",
        "ask_hour": "Izvēlieties stundu (00-23):",
        "ask_minute": "Izvēlieties minūti (00-59):",
        "ask_photo": "Kopīgojiet fotoattēlu (vai izlaidiet):",
        "ask_video": "Kopīgojiet video (vai izlaidiet):",
        "ask_song": "Nosūtiet dziesmu (vai izlaidiet):",
        "ask_voice": "Nosūtiet balss ziņu (vai izlaidiet):",
        "ask_audio": "Pievienojiet citu audio (vai izlaidiet):",
        "ready": "✨ Viss gatavs {name}!",
    },
    "et": {
        "welcome": "✨ Tere tulemast üllatuste nurka...\n\nTeie keeleks on määratud **Eesti**.",
        "region_selected": "🌍 Piirkond: **{region}**. Valige oma riik:",
        "country_choice": "🗣️ Valige keel riigile **{country}**:",
        "lang_updated": "✅ Keelesäte edukalt uuendatud!",
        "ask_category": "🎉 Milline pidu see on?",
        "owner_active": "🤍 **Omaniku režiim aktiivne!**\n\nMida me täna tähistame? Saatke nimi:",
        "free_remaining": "🎁 Teil on jäänud **{remaining}** tasuta üllatust!",
        "free_first": "🎁 Teie esimese **{limit}** üllatust on **TASUTA**!",
        "ask_name": "Mida me täna tähistame? Saatke nimi:",
        "ask_wish": "Kirjutage südamlik soov:",
        "ask_age_mode": "Kuidas soovite andmeid lisada?",
        "ask_dob_input": "📅 Saatke kuupäev formaadis **YYYY-MM-DD** (nt `2003-12-24`):",
        "ask_age_input": "🔢 Sisestage vanus numbrina (nt `22`):",
        "ask_year": "Valige aasta:",
        "ask_month": "Valige kuu:",
        "ask_date": "Valige kuupäev:",
        "ask_hour": "Valige tund (00-23):",
        "ask_minute": "Valige minut (00-59):",
        "ask_photo": "Jagage fotot (või jätke vahele):",
        "ask_video": "Jagage videot (või jätke vahele):",
        "ask_song": "Saatke laul (või jätke vahele):",
        "ask_voice": "Saatke häälsõnum (või jätke vahele):",
        "ask_audio": "Lisage teine heli (või jätke vahele):",
        "ready": "✨ Kõik on {name} jaoks valmis!",
    },
}

def get_bot_text(user_id, text_key, **kwargs):
    lang = get_user_lang(user_id)
    lang_dict = BOT_TEXTS.get(lang)
    if not lang_dict:
        return BOT_TEXTS["en"].get(text_key, "").format(**kwargs)
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

def get_user_creations(user_id):
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("SELECT creations_count FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else 0

def increment_user_creation(user_id):
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, completed, creations_count) VALUES (?, 1, 1)
        ON CONFLICT(user_id) DO UPDATE SET 
            completed = 1,
            creations_count = creations_count + 1
    """, (user_id,))
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
    conn.commit()
    surprise_id = cursor.lastrowid
    conn.close()
    return surprise_id

def get_stats():
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_started = cursor.fetchone()[0]
    cursor.execute("SELECT SUM(creations_count) FROM users")
    row = cursor.fetchone()
    total_completed = row[0] if row and row[0] else 0
    conn.close()
    return total_started, total_completed

class BirthdayForm(StatesGroup):
    category = State()
    name = State()
    wish = State()
    age_choice = State()
    dob_input = State()
    age_input = State()
    year = State()
    month = State()
    date = State()
    hour = State()
    minute = State()
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
        [InlineKeyboardButton(text="💍 Wedding Anniversary", callback_data="cat_Wedding")],
        [InlineKeyboardButton(text="👶 New Born", callback_data="cat_NewBorn")],
        [InlineKeyboardButton(text="🎓 Graduation", callback_data="cat_Graduation")],
        [InlineKeyboardButton(text="🌟 Other Celebration", callback_data="cat_Other")]
    ])

def get_action_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Skip", callback_data="skip_step"), InlineKeyboardButton(text="↩️ Change", callback_data="change_step")]
    ])

def get_age_choice_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Enter Date (DOB / Wedding Date)", callback_data="choice_dob")],
        [InlineKeyboardButton(text="🔢 Enter Direct Details", callback_data="choice_age")],
        [InlineKeyboardButton(text="✨ Skip Stats", callback_data="skip_step")]
    ])

def get_year_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="2026", callback_data="set_year_2026"), InlineKeyboardButton(text="2027", callback_data="set_year_2027")],
        [InlineKeyboardButton(text="✨ Skip", callback_data="skip_step"), InlineKeyboardButton(text="↩️ Change", callback_data="change_step")]
    ])

def get_month_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="January", callback_data="set_month_Jan"), InlineKeyboardButton(text="February", callback_data="set_month_Feb"), InlineKeyboardButton(text="March", callback_data="set_month_Mar")],
        [InlineKeyboardButton(text="April", callback_data="set_month_Apr"), InlineKeyboardButton(text="May", callback_data="set_month_May"), InlineKeyboardButton(text="June", callback_data="set_month_Jun")],
        [InlineKeyboardButton(text="July", callback_data="set_month_Jul"), InlineKeyboardButton(text="August", callback_data="set_month_Aug"), InlineKeyboardButton(text="September", callback_data="set_month_Sep")],
        [InlineKeyboardButton(text="October", callback_data="set_month_Oct"), InlineKeyboardButton(text="November", callback_data="set_month_Nov"), InlineKeyboardButton(text="December", callback_data="set_month_Dec")],
        [InlineKeyboardButton(text="✨ Skip", callback_data="skip_step"), InlineKeyboardButton(text="↩️ Change", callback_data="change_step")]
    ])

def get_date_keyboard():
    buttons = []
    row = []
    for i in range(1, 32):
        row.append(InlineKeyboardButton(text=str(i), callback_data=f"set_date_{str(i).zfill(2)}"))
        if len(row) == 7:
            buttons.append(row)
            row = []
    if row: buttons.append(row)
    buttons.append([InlineKeyboardButton(text="✨ Skip", callback_data="skip_step"), InlineKeyboardButton(text="↩️ Change", callback_data="change_step")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_hour_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="00", callback_data="set_hour_00"), InlineKeyboardButton(text="06", callback_data="set_hour_06"), InlineKeyboardButton(text="12", callback_data="set_hour_12"), InlineKeyboardButton(text="18", callback_data="set_hour_18")],
        [InlineKeyboardButton(text="✨ Skip", callback_data="skip_step"), InlineKeyboardButton(text="↩️ Change", callback_data="change_step")]
    ])

def get_minute_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="00", callback_data="set_min_00"), InlineKeyboardButton(text="15", callback_data="set_min_15"), InlineKeyboardButton(text="30", callback_data="set_min_30"), InlineKeyboardButton(text="45", callback_data="set_min_45")],
        [InlineKeyboardButton(text="✨ Skip", callback_data="skip_step"), InlineKeyboardButton(text="↩️ Change", callback_data="change_step")]
    ])

@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    record_start(user_id)
    save_user_lang(user_id, "en")
    await message.answer(get_bot_text(user_id, "welcome"), reply_markup=get_region_keyboard(), parse_mode="Markdown")

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

@dp.callback_query(F.data == "back_to_regions")
async def back_regions(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    await callback.message.edit_text(get_bot_text(user_id, "welcome"), reply_markup=get_region_keyboard())
    await callback.answer()

async def proceed_to_category(message: types.Message, user_id: int, state: FSMContext):
    await message.answer(get_bot_text(user_id, "ask_category"), reply_markup=get_category_keyboard())
    await state.set_state(BirthdayForm.category)

@dp.callback_query(F.data.startswith("cat_"))
async def process_category(callback: types.CallbackQuery, state: FSMContext):
    category = callback.data.split("_")[1]
    await state.update_data(category=category)
    user_id = callback.from_user.id
    await callback.message.answer(get_bot_text(user_id, "ask_name"), reply_markup=get_action_keyboard())
    await state.set_state(BirthdayForm.name)
    await callback.answer()

STATE_SEQUENCE = [BirthdayForm.name, BirthdayForm.wish, BirthdayForm.age_choice, BirthdayForm.year, BirthdayForm.month, BirthdayForm.date, BirthdayForm.hour, BirthdayForm.minute, BirthdayForm.photo, BirthdayForm.video, BirthdayForm.song, BirthdayForm.voice, BirthdayForm.audio]

@dp.callback_query(F.data == "skip_step")
async def process_skip(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    user_id = callback.from_user.id
    curr_idx = next((i for i, s in enumerate(STATE_SEQUENCE) if s.state == current_state), -1)
    if curr_idx != -1 and curr_idx + 1 < len(STATE_SEQUENCE):
        nxt = STATE_SEQUENCE[curr_idx + 1]
        await state.set_state(nxt)
        keys = {BirthdayForm.name: "ask_name", BirthdayForm.wish: "ask_wish", BirthdayForm.age_choice: "ask_age_mode", BirthdayForm.year: "ask_year", BirthdayForm.month: "ask_month", BirthdayForm.date: "ask_date", BirthdayForm.hour: "ask_hour", BirthdayForm.minute: "ask_minute", BirthdayForm.photo: "ask_photo", BirthdayForm.video: "ask_video", BirthdayForm.song: "ask_song", BirthdayForm.voice: "ask_voice", BirthdayForm.audio: "ask_audio"}
        kb = get_action_keyboard()
        if nxt == BirthdayForm.age_choice: kb = get_age_choice_keyboard()
        elif nxt == BirthdayForm.year: kb = get_year_keyboard()
        elif nxt == BirthdayForm.month: kb = get_month_keyboard()
        elif nxt == BirthdayForm.date: kb = get_date_keyboard()
        elif nxt == BirthdayForm.hour: kb = get_hour_keyboard()
        elif nxt == BirthdayForm.minute: kb = get_minute_keyboard()
        await callback.message.answer(get_bot_text(user_id, keys.get(nxt, "ask_name")), reply_markup=kb)
    else:
        await finish_form(callback.message, state)
    await callback.answer("Skipped")

@dp.callback_query(F.data == "change_step")
async def process_change(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    user_id = callback.from_user.id
    curr_idx = next((i for i, s in enumerate(STATE_SEQUENCE) if s.state == current_state), -1)
    if curr_idx > 0:
        prev = STATE_SEQUENCE[curr_idx - 1]
        await state.set_state(prev)
        keys = {BirthdayForm.wish: "ask_wish", BirthdayForm.age_choice: "ask_age_mode", BirthdayForm.year: "ask_year", BirthdayForm.month: "ask_month", BirthdayForm.date: "ask_date", BirthdayForm.hour: "ask_hour", BirthdayForm.minute: "ask_minute"}
        kb = get_action_keyboard()
        if prev == BirthdayForm.age_choice: kb = get_age_choice_keyboard()
        elif prev == BirthdayForm.year: kb = get_year_keyboard()
        elif prev == BirthdayForm.month: kb = get_month_keyboard()
        elif prev == BirthdayForm.date: kb = get_date_keyboard()
        elif prev == BirthdayForm.hour: kb = get_hour_keyboard()
        elif prev == BirthdayForm.minute: kb = get_minute_keyboard()
        await callback.message.answer(get_bot_text(user_id, keys.get(prev, "ask_name")), reply_markup=kb)
    else:
        await callback.message.answer("We are at the very beginning!", reply_markup=get_action_keyboard())
    await callback.answer("Going back")

@dp.callback_query(F.data == "choice_dob")
async def cb_choice_dob(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(BirthdayForm.dob_input)
    await callback.message.answer(get_bot_text(callback.from_user.id, "ask_dob_input"), reply_markup=get_action_keyboard())
    await callback.answer()

@dp.callback_query(F.data == "choice_age")
async def cb_choice_age(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(BirthdayForm.age_input)
    await callback.message.answer(get_bot_text(callback.from_user.id, "ask_age_input"), reply_markup=get_action_keyboard())
    await callback.answer()

@dp.message(BirthdayForm.dob_input)
async def process_dob(message: types.Message, state: FSMContext):
    await state.update_data(dob=message.text.strip())
    await state.set_state(BirthdayForm.year)
    await message.answer(get_bot_text(message.from_user.id, "ask_year"), reply_markup=get_year_keyboard())

@dp.message(BirthdayForm.age_input)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text.strip())
    await state.set_state(BirthdayForm.year)
    await message.answer(get_bot_text(message.from_user.id, "ask_year"), reply_markup=get_year_keyboard())

@dp.callback_query(F.data.startswith("set_year_"))
async def cb_year(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(year=callback.data.split("_")[2])
    await state.set_state(BirthdayForm.month)
    await callback.message.answer(get_bot_text(callback.from_user.id, "ask_month"), reply_markup=get_month_keyboard())
    await callback.answer()

@dp.callback_query(F.data.startswith("set_month_"))
async def cb_month(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(month=callback.data.split("_")[2])
    await state.set_state(BirthdayForm.date)
    await callback.message.answer(get_bot_text(callback.from_user.id, "ask_date"), reply_markup=get_date_keyboard())
    await callback.answer()

@dp.callback_query(F.data.startswith("set_date_"))
async def cb_date(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(date=callback.data.split("_")[2])
    await state.set_state(BirthdayForm.hour)
    await callback.message.answer(get_bot_text(callback.from_user.id, "ask_hour"), reply_markup=get_hour_keyboard())
    await callback.answer()

@dp.callback_query(F.data.startswith("set_hour_"))
async def cb_hour(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(hour=callback.data.split("_")[2])
    await state.set_state(BirthdayForm.minute)
    await callback.message.answer(get_bot_text(callback.from_user.id, "ask_minute"), reply_markup=get_minute_keyboard())
    await callback.answer()

@dp.callback_query(F.data.startswith("set_min_"))
async def cb_min(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(minute=callback.data.split("_")[2])
    await state.set_state(BirthdayForm.photo)
    await callback.message.answer(get_bot_text(callback.from_user.id, "ask_photo"), reply_markup=get_action_keyboard())
    await callback.answer()

@dp.message(BirthdayForm.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(BirthdayForm.wish)
    await message.answer(get_bot_text(message.from_user.id, "ask_wish"), reply_markup=get_action_keyboard())

@dp.message(BirthdayForm.wish)
async def process_wish(message: types.Message, state: FSMContext):
    await state.update_data(wish=message.text)
    await state.set_state(BirthdayForm.age_choice)
    await message.answer(get_bot_text(message.from_user.id, "ask_age_mode"), reply_markup=get_age_choice_keyboard())

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
    await message.answer(get_bot_text(message.from_user.id, "ask_video"), reply_markup=get_action_keyboard())

@dp.message(BirthdayForm.video, F.video)
async def process_video(message: types.Message, state: FSMContext):
    url = await get_telegram_file_url(bot, message.video.file_id)
    await state.update_data(video=url)
    await state.set_state(BirthdayForm.song)
    await message.answer(get_bot_text(message.from_user.id, "ask_song"), reply_markup=get_action_keyboard())

@dp.message(BirthdayForm.song, F.audio)
async def process_song_audio(message: types.Message, state: FSMContext):
    url = await get_telegram_file_url(bot, message.audio.file_id)
    await state.update_data(song=url)
    await state.set_state(BirthdayForm.voice)
    await message.answer(get_bot_text(message.from_user.id, "ask_voice"), reply_markup=get_action_keyboard())

@dp.message(BirthdayForm.song, F.document)
async def process_song_doc(message: types.Message, state: FSMContext):
    url = await get_telegram_file_url(bot, message.document.file_id)
    await state.update_data(song=url)
    await state.set_state(BirthdayForm.voice)
    await message.answer(get_bot_text(message.from_user.id, "ask_voice"), reply_markup=get_action_keyboard())

@dp.message(BirthdayForm.voice, F.voice)
async def process_voice(message: types.Message, state: FSMContext):
    url = await get_telegram_file_url(bot, message.voice.file_id)
    await state.update_data(voice=url)
    await finish_form(message, state)

@dp.message(BirthdayForm.photo)
async def skip_photo(message: types.Message, state: FSMContext):
    await state.set_state(BirthdayForm.video)
    await message.answer(get_bot_text(message.from_user.id, "ask_video"), reply_markup=get_action_keyboard())

@dp.message(BirthdayForm.video)
async def skip_video(message: types.Message, state: FSMContext):
    await state.set_state(BirthdayForm.song)
    await message.answer(get_bot_text(message.from_user.id, "ask_song"), reply_markup=get_action_keyboard())

@dp.message(BirthdayForm.song)
async def skip_song(message: types.Message, state: FSMContext):
    await state.set_state(BirthdayForm.voice)
    await message.answer(get_bot_text(message.from_user.id, "ask_voice"), reply_markup=get_action_keyboard())

@dp.message(BirthdayForm.voice)
async def skip_voice(message: types.Message, state: FSMContext):
    await finish_form(message, state)

async def finish_form(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id != OWNER_ID:
        increment_user_creation(user_id)
    data = await state.get_data()
    
    params = {
        "name": data.get("name", "Friend"),
        "msg": data.get("wish", ""),
        "category": data.get("category", "Birthday"),
        "dob": data.get("dob", ""),
        "age": data.get("age", ""),
        "photo": data.get("photo", ""),
        "video": data.get("video", ""),
        "song": data.get("song", ""),
        "voice": data.get("voice", "")
    }

    if data.get("year") and data.get("date") and data.get("hour") and data.get("minute"):
        m_map = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}
        m_raw = str(data.get("month", "01"))
        m_val = m_map.get(m_raw[:3].capitalize(), m_raw.zfill(2))
        params["target_time"] = f"{data.get('year')}-{m_val}-{str(data.get('date')).zfill(2)}T{str(data.get('hour')).zfill(2)}:{str(data.get('minute')).zfill(2)}:00"

    surprise_id = save_surprise_to_db(user_id, params["category"], params["name"], params["msg"], params)
    
    preview_url = f"{VERCEL_URL}/?id={surprise_id}&preview=true"
    final_url = f"{VERCEL_URL}/?id={surprise_id}"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤍 Preview Surprise", web_app=WebAppInfo(url=preview_url)), InlineKeyboardButton(text="🎂 Celebration View", web_app=WebAppInfo(url=preview_url))],
        [InlineKeyboardButton(text="🔗 Copy Link", url=final_url)]
    ])
    await message.answer(get_bot_text(user_id, "ready", name=params["name"]), reply_markup=kb)
    await state.clear()

async def get_surprise_api(request):
    surprise_id = request.query.get("id")
    if not surprise_id: return web.json_response({"error": "No ID"}, status=400)
    conn = sqlite3.connect("bot_stats.db")
    cursor = conn.cursor()
    cursor.execute("SELECT params_json FROM surprises WHERE id = ?", (surprise_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = json.loads(row[0]) if row[0] else {}
        return web.json_response(data, headers={"Access-Control-Allow-Origin": "*"})
    return web.json_response({"error": "Not found"}, status=404)

async def handle(request):
    return web.Response(text="Bot is running!")

async def web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    app.router.add_get("/api/surprise", get_surprise_api)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", int(os.environ.get("PORT", 8080)))
    await site.start()

async def main():
    await asyncio.gather(web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
