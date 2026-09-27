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
    WebAppInfo,
)
from aiohttp import web

API_TOKEN = "8854916574:AAEgxWmPyP4OPNSsLfsBbXXFu5W6LiFcq0o"
OWNER_ID = 1689374364

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
VERCEL_URL = "https://aura-birthday-web.vercel.app"

COUNTRY_LANGUAGES = {
    "Asia": {
        "🇮🇳 India": [
            ("English", "en"),
            ("Malayalam", "ml"),
            ("Hindi", "hi"),
            ("Tamil", "ta"),
            ("Telugu", "te"),
            ("Kannada", "kn"),
            ("Bengali", "bn"),
            ("Marathi", "mr"),
            ("Gujarati", "gu"),
            ("Punjabi", "pa"),
            ("Urdu", "ur"),
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

# --- 40+ ഭാഷകളിലെ സമ്പൂർണ്ണ ബോട്ട് ടെക്സ്റ്റ് ഡിക്ഷണറി ---
BOT_TEXTS = {
    "en": {
        "welcome": "✨ *Welcome to your little corner of surprises...*\n\nChoose your region and country to get started:",
        "region_selected": "🌍 Region: *{region}*. Select your country:",
        "country_choice": "🗣️ Choose your language for *{country}*:",
        "lang_updated": "✅ Language updated successfully!",
        "ask_category": "🎉 *What kind of celebration is this?* Choose below:",
        "ask_name": "✨ *Whose special occasion are we celebrating today?* Send me their name:",
        "ask_wish": "📝 *Write a sweet, heartfelt wish or message for them (Long paragraphs supported!):*",
        "ask_dob_type": "⏳ *How would you like to add age details for stats?*",
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
        "ready": "✨ *All ready for {name}!*"
    },
    "ml": {
        "welcome": "✨ *ചെറിയ സർപ്രൈസുകളുടെ ലോകത്തേക്ക് സ്വാഗതം...*\n\nതുടങ്ങാൻ പ്രദേശം തിരഞ്ഞെടുക്കൂ:",
        "region_selected": "🌍 പ്രദേശം: *{region}*. നിങ്ങളുടെ രാജ്യം തിരഞ്ഞെടുക്കൂ:",
        "country_choice": "🗣️ *{country}*-നുള്ള ഭാഷ തിരഞ്ഞെടുക്കൂ:",
        "lang_updated": "✅ ഭാഷ വിജയകരമായി മാറ്റിയിരിക്കുന്നു!",
        "ask_category": "🎉 *ഇത് എന്തുതരം ആഘോഷമാണ്?*",
        "ask_name": "✨ *ഇന്ന് ആരുടെ വിശേഷമാണ് ആഘോഷിക്കുന്നത്? പേര് അയക്കൂ:*",
        "ask_wish": "📝 *അവർക്കായി ആശംസ എഴുതൂ (വലിയ പാരഗ്രാഫുകളും അയക്കാം):*",
        "ask_dob_type": "⏳ *സ്റ്റാറ്റിസ്റ്റിക്സിനായി തീയതി എങ്ങനെ നൽകണം?*",
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
        "ready": "✨ *{name}-നുള്ള സർപ്രൈസ് റെഡിയാണ്!*"
    },
    "hi": {
        "welcome": "✨ *सरप्राइज की इस खूबसूरत दुनिया में आपका स्वागत है...*",
        "region_selected": "🌍 क्षेत्र: *{region}*. अपना देश चुनें:",
        "country_choice": "🗣️ *{country}* के लिए अपनी भाषा चुनें:",
        "lang_updated": "✅ भाषा सफलतापूर्वक अपडेट कर दी गई है!",
        "ask_category": "🎉 *यह किस प्रकार का उत्सव है?*",
        "ask_name": "✨ *आज हम किसका जश्न मना रहे हैं? नाम भेजें:*",
        "ask_wish": "📝 *एक प्यारा सा संदेश लिखें:*",
        "ask_dob_type": "⏳ *आयु विवरण कैसे जोड़ना चाहेंगे?*",
        "ask_dob_date": "📅 कृपया **YYYY-MM-DD** प्रारूप में तिथि भेजें:",
        "ask_dob_direct": "🔢 सीधी आयु संख्या में दर्ज करें (उदा. `22`):",
        "ask_year": "📅 *वर्ष चुनें:*",
        "ask_month": "📆 *महीना चुनें:*",
        "ask_day": "🗓️ *तारीख चुनें:*",
        "ask_hour": "⏰ *घंटा चुनें (00 से 23):*",
        "ask_minute": "⏱️ *मिनट चुनें (00 से 59):*",
        "ask_photo": "📸 *फोटो शेयर करें* (या छोड़ें):",
        "ask_video": "🎥 *वीडियो शेयर करें* (या छोड़ें):",
        "ask_song": "🎶 *गाना भेजें* (या छोड़ें):",
        "ask_voice": "🎙️ *वॉयस नोट भेजें* (या छोड़ें):",
        "ask_audio": "🎵 *एक और ऑडियो जोड़ें* (या छोड़ें):",
        "ready": "✨ *{name} के लिए सब तैयार है!*"
    },
    "ta": {
        "welcome": "✨ *ஆச்சரியங்களின் உலகிற்கு வரவேற்கிறோம்...*",
        "region_selected": "🌍 பிராந்தியம்: *{region}*. நாட்டை தேர்ந்தெடுக்கவும்:",
        "country_choice": "🗣️ *{country}*-க்கான மொழியை தேர்ந்தெடுக்கவும்:",
        "lang_updated": "✅ மொழி வெற்றிகரமாக மாற்றப்பட்டது!",
        "ask_category": "🎉 *இது என்ன வகையான கொண்டாட்டம்?*",
        "ask_name": "✨ *இன்று யாருடைய சிறப்பு நாள்? பெயரை அனுப்பவும்:*",
        "ask_wish": "📝 *அன்பான வாழ்த்து செய்தியை எழுதுங்கள்:*",
        "ask_dob_type": "⏳ *வயது விவரங்களை எவ்வாறு சேர்க்க விரும்புகிறீர்கள்?*",
        "ask_dob_date": "📅 தேதியை **YYYY-MM-DD** வடிவத்தில் அனுப்பவும்:",
        "ask_dob_direct": "🔢 நேரடி வயதை எண்ணாக உள்ளிடவும்:",
        "ask_year": "📅 *ஆண்டைத் தேர்ந்தெடுக்கவும்:*",
        "ask_month": "📆 *மாதத்தைத் தேர்ந்தெடுக்கவும்:*",
        "ask_day": "🗓️ *தேதியைத் தேர்ந்தெடுக்கவும்:*",
        "ask_hour": "⏰ *மணிநேரத்தை தேர்ந்தெடுக்கவும் (00 - 23):*",
        "ask_minute": "⏱️ *நிமிடத்தை தேர்ந்தெடுக்கவும் (00 - 59):*",
        "ask_photo": "📸 *புகைப்படத்தை பகிரவும்* (அல்லது தவிர்க்கவும்):",
        "ask_video": "🎥 *வீடியோவை பகிரவும்* (அல்லது தவிர்க்கவும்):",
        "ask_song": "🎶 *பாடலை அனுப்பவும்* (அல்லது தவிர்க்கவும்):",
        "ask_voice": "🎙️ *குரல் பதிவை அனுப்பவும்* (அல்லது தவிர்க்கவும்):",
        "ask_audio": "🎵 *கூடுதல் ஆடியோ சேர்க்கவும்* (அல்லது தவிர்க்கவும்):",
        "ready": "✨ *{name}-க்கான ஏற்பாடுகள் அனைத்தும் தயார்!*"
    },
    "te": {
        "welcome": "✨ *సర్ప్రైజ్ ప్రపంచానికి స్వాగతం...*",
        "region_selected": "🌍 ప్రాంతం: *{region}*. మీ దేశాన్ని ఎంచుకోండి:",
        "country_choice": "🗣️ *{country}* భాషను ఎంచుకోండి:",
        "lang_updated": "✅ భాష నవీకరించబడింది!",
        "ask_category": "🎉 *ఇది ఏ రకమైన వేడుక?*",
        "ask_name": "✨ *ఎవరి ప్రత్యేక సందర్భం జరుపుకుంటున్నాము? పేరు పంపండి:*",
        "ask_wish": "📝 *ఒక మంచి శుభాకాంక్ష రాయండి:*",
        "ask_dob_type": "⏳ *వయస్సు వివరాలు ఎలా జోడించాలి?*",
        "ask_dob_date": "📅 **YYYY-MM-DD** ఫార్మాట్‌లో తేదీని పంపండి:",
        "ask_dob_direct": "🔢 వయస్సును సంఖ్యగా ఇవ్వండి:",
        "ask_year": "📅 *సంవత్సరాన్ని ఎంచుకోండి:*",
        "ask_month": "📆 *నెలను ఎంచుకోండి:*",
        "ask_day": "🗓️ *తేదీని ఎంచుకోండి:*",
        "ask_hour": "⏰ *గంటను ఎంచుకోండి (00 నుండి 23):*",
        "ask_minute": "⏱️ *నిమిషాన్ని ఎంచుకోండి (00 నుండి 59):*",
        "ask_photo": "📸 *ఫోటోను పంచుకోండి* (లేదా దాటవేయండి):",
        "ask_video": "🎥 *వీడియో పంచుకోండి* (లేదా దాటవేయండి):",
        "ask_song": "🎶 *పాట పంపండి* (లేదా దాటవేయండి):",
        "ask_voice": "🎙️ *వాయిస్ నోట్ పంపండి* (లేదా దాటవేయండి):",
        "ask_audio": "🎵 *మరో ఆడియో జోడించండి* (లేదా దాటవేయండి):",
        "ready": "✨ *{name} కోసం అన్నీ సిద్ధంగా ఉన్నాయి!*"
    },
    "kn": {
        "welcome": "✨ *ಅಚ್ಚರಿಗಳ ಲೋಕಕ್ಕೆ ಸುಸ್ವಾಗತ...*",
        "region_selected": "🌍 ಪ್ರದೇಶ: *{region}*. ದೇಶವನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
        "country_choice": "🗣️ *{country}* ಭಾಷೆ ಆಯ್ಕೆಮಾಡಿ:",
        "lang_updated": "✅ ಭಾಷೆ ನವೀಕರಿಸಲಾಗಿದೆ!",
        "ask_category": "🎉 *ಇದು ಯಾವ ರೀತಿಯ ಆಚರಣೆ?*",
        "ask_name": "✨ *ಯಾರ ವಿಶೇಷ ದಿನ ಆಚರಿಸುತ್ತಿದ್ದೇವೆ? ಹೆಸರು ಕಳುಹಿಸಿ:*",
        "ask_wish": "📝 *ಒಂದು ಸುಂದರ ಸಂದೇಶ ಬರೆಯಿರಿ:*",
        "ask_dob_type": "⏳ *ವಯಸ್ಸಿನ ವಿವರ ಹೇಗೆ ನೀಡಲು ಬಯಸುತ್ತೀರಿ?*",
        "ask_dob_date": "📅 **YYYY-MM-DD** ಮಾದರಿಯಲ್ಲಿ ದಿನಾಂಕ ಕಳುಹಿಸಿ:",
        "ask_dob_direct": "🔢 ವಯಸ್ಸನ್ನು ಸಂಖ್ಯೆಯಾಗಿ ನಮೂದಿಸಿ:",
        "ask_year": "📅 *ವರ್ಷ ಆಯ್ಕೆಮಾಡಿ:*",
        "ask_month": "📆 *ತಿಂಗಳು ಆಯ್ಕೆಮಾಡಿ:*",
        "ask_day": "🗓️ *ದಿನಾಂಕ ಆಯ್ಕೆಮಾಡಿ:*",
        "ask_hour": "⏰ *ಗಂಟೆ ಆಯ್ಕೆಮಾಡಿ (00 ರಿಂದ 23):*",
        "ask_minute": "⏱️ *ನಿಮಿಷ ಆಯ್ಕೆಮಾಡಿ (00 ರಿಂದ 59):*",
        "ask_photo": "📸 *ಫೋಟೋ ಕಳುಹಿಸಿ* (ಅಥವಾ ಬಿಟ್ಟುಬಿಡಿ):",
        "ask_video": "🎥 *ವೀಡಿಯೊ ಕಳುಹಿಸಿ* (ಅಥವಾ ಬಿಟ್ಟುಬಿಡಿ):",
        "ask_song": "🎶 *ಹಾಡು ಕಳುಹಿಸಿ* (ಅಥವಾ ಬಿಟ್ಟುಬಿಡಿ):",
        "ask_voice": "🎙️ *ಧ್ವನಿ ಸಂದೇಶ ಕಳುಹಿಸಿ* (ಅಥವಾ ಬಿಟ್ಟುಬಿಡಿ):",
        "ask_audio": "🎵 *ಇನ್ನೊಂದು ಆಡಿಯೋ ಸೇರಿಸಿ* (ಅಥವಾ ಬಿಟ್ಟುಬಿಡಿ):",
        "ready": "✨ *{name} ಗಾಗಿ ಎಲ್ಲವೂ ಸಿದ್ಧವಾಗಿದೆ!*"
    },
    "bn": {
        "welcome": "✨ *বিস্ময়ের জগতে আপনাকে স্বাগতম...*",
        "region_selected": "🌍 অঞ্চল: *{region}*. দেশ নির্বাচন করুন:",
        "country_choice": "🗣️ *{country}* ভাষা নির্বাচন করুন:",
        "lang_updated": "✅ ভাষা সফলভাবে আপডেট করা হয়েছে!",
        "ask_category": "🎉 *এটি কী ধরনের উৎসব?*",
        "ask_name": "✨ *আজ কার বিশেষ দিন? নাম পাঠান:*",
        "ask_wish": "📝 *একটি সুন্দর বার্তা লিখুন:*",
        "ask_dob_type": "⏳ *বয়সের বিবরণ কীভাবে যুক্ত করবেন?*",
        "ask_dob_date": "📅 **YYYY-MM-DD** ফরম্যাটে তারিখ পাঠান:",
        "ask_dob_direct": "🔢 সরাসরি বয়স সংখ্যায় লিখুন:",
        "ask_year": "📅 *বছর নির্বাচন করুন:*",
        "ask_month": "📆 *মাস নির্বাচন করুন:*",
        "ask_day": "🗓️ *তারিখ নির্বাচন করুন:*",
        "ask_hour": "⏰ *ঘণ্টা নির্বাচন করুন (00 থেকে 23):*",
        "ask_minute": "⏱️ *মিনিট নির্বাচন করুন (00 থেকে 59):*",
        "ask_photo": "📸 *ছবি শেয়ার করুন* (বা এড়িয়ে যান):",
        "ask_video": "🎥 *ভিডিও শেয়ার করুন* (বা এড়িয়ে যান):",
        "ask_song": "🎶 *গান পাঠান* (বা এড়িয়ে যান):",
        "ask_voice": "🎙️ *ভয়েস নোট পাঠান* (বা এড়িয়ে যান):",
        "ask_audio": "🎵 *অন্য একটি অডিও যোগ করুন* (বা এড়িয়ে যান):",
        "ready": "✨ *{name} এর জন্য সবকিছু প্রস্তুত!*"
    },
    "mr": {
        "welcome": "✨ *सरप्राईजच्या जगात आपले स्वागत आहे...*",
        "region_selected": "🌍 प्रदेश: *{region}*. देश निवडा:",
        "country_choice": "🗣️ भाषा निवडा:",
        "lang_updated": "✅ भाषा अपडेट केली!",
        "ask_category": "🎉 *हा कोणता उत्सव आहे?*",
        "ask_name": "✨ *नाव पाठवा:*",
        "ask_wish": "📝 *एक छान संदेश लिहा:*",
        "ask_dob_type": "⏳ *वयाचे तपशील कसे जोडायचे?*",
        "ask_dob_date": "📅 **YYYY-MM-DD** स्वरूपात तारीख पाठवा:",
        "ask_dob_direct": "🔢 वय आकड्यात टाका:",
        "ask_year": "📅 *वर्ष निवडा:*",
        "ask_month": "📆 *महिना निवडा:*",
        "ask_day": "🗓️ *तारीख निवडा:*",
        "ask_hour": "⏰ *तास निवडा (00 ते 23):*",
        "ask_minute": "⏱️ *मिनिट निवडा (00 ते 59):*",
        "ask_photo": "📸 *फोटो पाठवा:*",
        "ask_video": "🎥 *व्हिडिओ पाठवा:*",
        "ask_song": "🎶 *गाणे पाठवा:*",
        "ask_voice": "🎙️ *व्हॉइस नोट पाठवा:*",
        "ask_audio": "🎵 *ऑडिओ जोडा:*",
        "ready": "✨ *{name} साठी सर्व तयार आहे!*"
    },
    "gu": {
        "welcome": "✨ *સરપ્રાઈઝની દુનિયામાં આપનું સ્વાગત છે...*",
        "region_selected": "🌍 પ્રદેશ: *{region}*:",
        "country_choice": "🗣️ ભાષા પસંદ કરો:",
        "lang_updated": "✅ ભાષા અપડેટ થઈ ગઈ!",
        "ask_category": "🎉 *આ કયો ઉત્સવ છે?*",
        "ask_name": "✨ *નામ મોકલો:*",
        "ask_wish": "📝 *સુંદર સંદેશ લખો:*",
        "ask_dob_type": "⏳ *ઉંમર વિગતો કેવી રીતે ઉમેરવી?*",
        "ask_dob_date": "📅 **YYYY-MM-DD** ફોર્મેટમાં તારીખ મોકલો:",
        "ask_dob_direct": "🔢 સીધી ઉંમર નંબરમાં લખો:",
        "ask_year": "📅 *વર્ષ પસંદ કરો:*",
        "ask_month": "📆 *મહિનો પસંદ કરો:*",
        "ask_day": "🗓️ *તારીખ પસંદ કરો:*",
        "ask_hour": "⏰ *કલાક પસંદ કરો (00 થી 23):*",
        "ask_minute": "⏱️ *મિનિટ પસંદ કરો (00 થી 59):*",
        "ask_photo": "📸 *ફોટો શેર કરો:*",
        "ask_video": "🎥 *વીડિયો શેર કરો:*",
        "ask_song": "🎶 *ગીત મોકલો:*",
        "ask_voice": "🎙️ *વોઈસ નોટ મોકલો:*",
        "ask_audio": "🎵 *ઓડિયો ઉમેરો:*",
        "ready": "✨ *{name} માટે બધું તૈયાર છે!*"
    },
    "pa": {
        "welcome": "✨ *ਸਰਪ੍ਰਾਈਜ਼ਾਂ ਦੀ ਦੁਨੀਆ ਵਿੱਚ ਜੀ ਆਇਆਂ ਨੂੰ...*",
        "region_selected": "🌍 ਖੇਤਰ: *{region}*:",
        "country_choice": "🗣️ ਭਾਸ਼ਾ ਚੁਣੋ:",
        "lang_updated": "✅ ਭਾਸ਼ਾ ਅੱਪਡੇਟ ਹੋ ਗਈ!",
        "ask_category": "🎉 *ਇਹ ਕਿਸ ਤਰ੍ਹਾਂ ਦਾ ਜਸ਼ਨ ਹੈ?*",
        "ask_name": "✨ *ਨਾਮ ਭੇਜੋ:*",
        "ask_wish": "📝 *ਇੱਕ ਪਿਆਰਾ ਸੁਨੇਹਾ ਲਿਖੋ:*",
        "ask_dob_type": "⏳ *ਉਮਰ ਵੇਰਵਾ ਕਿਵੇਂ ਜੋੜਨਾ ਚਾਹੁੰਦੇ ਹੋ?*",
        "ask_dob_date": "📅 **YYYY-MM-DD** ਫਾਰਮੈਟ ਵਿੱਚ ਮਿਤੀ ਭੇਜੋ:",
        "ask_dob_direct": "🔢 ਸਿੱਧੀ ਉਮਰ ਨੰਬਰ ਵਿੱਚ ਲਿਖੋ:",
        "ask_year": "📅 *ਸਾਲ ਚੁਣੋ:*",
        "ask_month": "📆 *ਮਹੀਨਾ ਚੁਣੋ:*",
        "ask_day": "🗓️ *ਤਾਰੀਖ ਚੁਣੋ:*",
        "ask_hour": "⏰ *ਘੰਟਾ ਚੁਣੋ (00 ਤੋਂ 23):*",
        "ask_minute": "⏱️ *ਮਿੰਟ ਚੁਣੋ (00 ਤੋਂ 59):*",
        "ask_photo": "📸 *ਫੋਟੋ ਭੇਜੋ:*",
        "ask_video": "🎥 *ਵੀਡੀਓ ਭੇਜੋ:*",
        "ask_song": "🎶 *ਗਾਣਾ ਭੇਜੋ:*",
        "ask_voice": "🎙️ *ਵੌਇਸ ਨੋਟ ਭੇਜੋ:*",
        "ask_audio": "🎵 *ਆਡੀਓ ਸ਼ਾਮਲ ਕਰੋ:*",
        "ready": "✨ *{name} ਲਈ ਸਭ ਤਿਆਰ ਹੈ!*"
    },
    "ur": {
        "welcome": "✨ *سرپرائزز کی دنیا میں خوش آمدید...*",
        "region_selected": "🌍 خطہ: *{region}*:",
        "country_choice": "🗣️ زبان منتخب کریں:",
        "lang_updated": "✅ زبان تبدیل ہو گئی!",
        "ask_category": "🎉 *یہ کس قسم کی تقریب ہے؟*",
        "ask_name": "✨ *نام بھیجیں:*",
        "ask_wish": "📝 *ایک خوبصورت پیغام لکھیں:*",
        "ask_dob_type": "⏳ *عمر کی تفصیل کیسے درج کرنا چاہتے ہیں؟*",
        "ask_dob_date": "📅 تاریخ **YYYY-MM-DD** فارمیٹ میں بھیجیں:",
        "ask_dob_direct": "🔢 براہ راست عمر نمبر میں لکھیں:",
        "ask_year": "📅 *سال منتخب کریں:*",
        "ask_month": "📆 *مہینہ منتخب کریں:*",
        "ask_day": "🗓️ *تاریخ منتخب کریں:*",
        "ask_hour": "⏰ *گھنٹہ منتخب کریں (00 تا 23):*",
        "ask_minute": "⏱️ *منٹ منتخب کریں (00 تا 59):*",
        "ask_photo": "📸 *تصویر شیئر کریں:*",
        "ask_video": "🎥 *ویڈیو شیئر کریں:*",
        "ask_song": "🎶 *گانا بھیجیں:*",
        "ask_voice": "🎙️ *وائس نوٹ بھیجیں:*",
        "ask_audio": "🎵 *مزید آڈیو شامل کریں:*",
        "ready": "✨ *{name} کے لیے سب تیار ہے!*"
    },
    "ar": {
        "welcome": "✨ *مرحباً بك في عالم المفاجآت الساحر...*",
        "region_selected": "🌍 المنطقة: *{region}*. اختر دولتك:",
        "country_choice": "🗣️ اختر لغتك لـ *{country}*:",
        "lang_updated": "✅ تم تحديث اللغة بنجاح!",
        "ask_category": "🎉 *ما نوع هذا الاحتفال؟*",
        "ask_name": "✨ *من صاحب هذه المناسبة اليوم؟ أرسل اسمه:*",
        "ask_wish": "📝 *اكتب رسالة تهنئة جميلة:*",
        "ask_dob_type": "⏳ *كيف ترغب في إضافة تفاصيل العمر؟*",
        "ask_dob_date": "📅 أرسل التاريخ بصيغة **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 أدخل العمر المباشر كرقم (مثال: `22`):",
        "ask_year": "📅 *اختر السنة:*",
        "ask_month": "📆 *اختر الشهر:*",
        "ask_day": "🗓️ *اختر اليوم:*",
        "ask_hour": "⏰ *اختر الساعة (00 إلى 23):*",
        "ask_minute": "⏱️ *اختر الدقيقة (00 إلى 59):*",
        "ask_photo": "📸 *شارك صورة جميلة* (أو تخطى):",
        "ask_video": "🎥 *شارك فيديو* (أو تخطى):",
        "ask_song": "🎶 *أرسل أغنية* (أو تخطى):",
        "ask_voice": "🎙️ *أرسل رسالة صوتية* (أو تخطى):",
        "ask_audio": "🎵 *أضف مقطع صوتي آخر* (أو تخطى):",
        "ready": "✨ *كل شيء جاهز لـ {name}!*"
    },
    "ru": {
        "welcome": "✨ *Добро пожаловать в мир сюрпризов...*",
        "region_selected": "🌍 Регион: *{region}*. Выберите страну:",
        "country_choice": "🗣️ Выберите язык для *{country}*:",
        "lang_updated": "✅ Язык успешно обновлен!",
        "ask_category": "🎉 *Какой это праздник?*",
        "ask_name": "✨ *Чей праздник мы празднуем? Введите имя:*",
        "ask_wish": "📝 *Напишите теплое пожелание:*",
        "ask_dob_type": "⏳ *Как вы хотите указать возраст?*",
        "ask_dob_date": "📅 Введите дату в формате **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Введите точный возраст цифрой:",
        "ask_year": "📅 *Выберите год:*",
        "ask_month": "📆 *Выберите месяц:*",
        "ask_day": "🗓️ *Выберите день:*",
        "ask_hour": "⏰ *Выберите час (00-23):*",
        "ask_minute": "⏱️ *Выберите минуту (00-59):*",
        "ask_photo": "📸 *Загрузите фото* (или пропустите):",
        "ask_video": "🎥 *Загрузите видео* (или пропустите):",
        "ask_song": "🎶 *Отправьте песню* (или пропустите):",
        "ask_voice": "🎙️ *Отправьте голосовое* (или пропустите):",
        "ask_audio": "🎵 *Добавьте еще аудио* (или пропустите):",
        "ready": "✨ *Все готово для {name}!*"
    },
    "de": {
        "welcome": "✨ *Willkommen in der Welt der Überraschungen...*",
        "region_selected": "🌍 Region: *{region}*. Land wählen:",
        "country_choice": "🗣️ Sprache für *{country}* wählen:",
        "lang_updated": "✅ Sprache erfolgreich aktualisiert!",
        "ask_category": "🎉 *Welche Art von Feier ist das?*",
        "ask_name": "✨ *Wessen Anlass feiern wir? Name senden:*",
        "ask_wish": "📝 *Schreiben Sie eine liebevolle Nachricht:*",
        "ask_dob_type": "⏳ *Wie möchten Sie das Alter angeben?*",
        "ask_dob_date": "📅 Datum im Format **YYYY-MM-DD** senden:",
        "ask_dob_direct": "🔢 Alter direkt als Zahl eingeben:",
        "ask_year": "📅 *Jahr wählen:*",
        "ask_month": "📆 *Monat wählen:*",
        "ask_day": "🗓️ *Tag wählen:*",
        "ask_hour": "⏰ *Stunde wählen (00 bis 23):*",
        "ask_minute": "⏱️ *Minute wählen (00 bis 59):*",
        "ask_photo": "📸 *Foto teilen* (oder überspringen):",
        "ask_video": "🎥 *Video teilen* (oder überspringen):",
        "ask_song": "🎶 *Lied senden* (oder überspringen):",
        "ask_voice": "🎙️ *Sprachnachricht senden* (oder überspringen):",
        "ask_audio": "🎵 *Weiteres Audio hinzufügen* (oder überspringen):",
        "ready": "✨ *Alles bereit für {name}!*"
    },
    "fr": {
        "welcome": "✨ *Bienvenue dans le monde des surprises...*",
        "region_selected": "🌍 Région: *{region}*. Choisissez votre pays:",
        "country_choice": "🗣️ Langue pour *{country}*:",
        "lang_updated": "✅ Langue mise à jour avec succès!",
        "ask_category": "🎉 *Quel genre de fête est-ce?*",
        "ask_name": "✨ *Pour qui est cette célébration? Nom:*",
        "ask_wish": "📝 *Écrivez un message chaleureux:*",
        "ask_dob_type": "⏳ *Comment ajouter l'âge?*",
        "ask_dob_date": "📅 Date au format **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Âge direct sous forme de nombre:",
        "ask_year": "📅 *Choisissez l'année:*",
        "ask_month": "📆 *Choisissez le mois:*",
        "ask_day": "🗓️ *Choisissez le jour:*",
        "ask_hour": "⏰ *Heure (00 à 23):*",
        "ask_minute": "⏱️ *Minute (00 à 59):*",
        "ask_photo": "📸 *Partagez une photo* (ou ignorer):",
        "ask_video": "🎥 *Partagez une vidéo* (ou ignorer):",
        "ask_song": "🎶 *Envoyez une chanson* (ou ignorer):",
        "ask_voice": "🎙️ *Message vocal* (ou ignorer):",
        "ask_audio": "🎵 *Audio supplémentaire* (ou ignorer):",
        "ready": "✨ *Tout est prêt pour {name}!*"
    },
    "es": {
        "welcome": "✨ *Bienvenido al rincón de las sorpresas...*",
        "region_selected": "🌍 Región: *{region}*. Selecciona tu país:",
        "country_choice": "🗣️ Idioma para *{country}*:",
        "lang_updated": "✅ ¡Idioma actualizado exitosamente!",
        "ask_category": "🎉 *¿Qué tipo de celebración es?*",
        "ask_name": "✨ *¿De quién es la ocasión especial? Nombre:*",
        "ask_wish": "📝 *Escribe un mensaje cariñoso:*",
        "ask_dob_type": "⏳ *¿Cómo añadir la edad para estadísticas?*",
        "ask_dob_date": "📅 Fecha en formato **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Edad directamente en número:",
        "ask_year": "📅 *Elige el año:*",
        "ask_month": "📆 *Elige el mes:*",
        "ask_day": "🗓️ *Elige el día:*",
        "ask_hour": "⏰ *Hora (00 a 23):*",
        "ask_minute": "⏱️ *Minuto (00 a 59):*",
        "ask_photo": "📸 *Comparte una foto* (o saltar):",
        "ask_video": "🎥 *Comparte un video* (o saltar):",
        "ask_song": "🎶 *Envía una canción* (o saltar):",
        "ask_voice": "🎙️ *Nota de voz* (o saltar):",
        "ask_audio": "🎵 *Audio adicional* (o saltar):",
        "ready": "✨ *¡Todo listo para {name}!*"
    },
    "pt": {
        "welcome": "✨ *Bem-vindo ao mundo das surpresas...*",
        "region_selected": "🌍 Região: *{region}*. Escolha seu país:",
        "country_choice": "🗣️ Idioma para *{country}*:",
        "lang_updated": "✅ Idioma atualizado com sucesso!",
        "ask_category": "🎉 *Que tipo de comemoração é essa?*",
        "ask_name": "✨ *De quem é o dia especial? Nome:*",
        "ask_wish": "📝 *Escreva uma mensagem carinhosa:*",
        "ask_dob_type": "⏳ *Como adicionar a idade?*",
        "ask_dob_date": "📅 Data no formato **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Digite a idade diretamente como número:",
        "ask_year": "📅 *Escolha o ano:*",
        "ask_month": "📆 *Escolha o mês:*",
        "ask_day": "🗓️ *Escolha o dia:*",
        "ask_hour": "⏰ *Hora (00 a 23):*",
        "ask_minute": "⏱️ *Minuto (00 a 59):*",
        "ask_photo": "📸 *Compartilhe uma foto* (ou pule):",
        "ask_video": "🎥 *Compartilhe um vídeo* (ou pule):",
        "ask_song": "🎶 *Envie uma música* (ou pule):",
        "ask_voice": "🎙️ *Mensagem de voz* (ou pule):",
        "ask_audio": "🎵 *Áudio extra* (ou pule):",
        "ready": "✨ *Tudo pronto para {name}!*"
    },
    "it": {
        "welcome": "✨ *Benvenuto nell'angolo delle sorprese...*",
        "region_selected": "🌍 Regione: *{region}*. Scegli il tuo paese:",
        "country_choice": "🗣️ Lingua per *{country}*:",
        "lang_updated": "✅ Lingua aggiornata con successo!",
        "ask_category": "🎉 *Che tipo di celebrazione è?*",
        "ask_name": "✨ *Di chi è l'occasione? Invia il nome:*",
        "ask_wish": "📝 *Scrivi un dolce messaggio:*",
        "ask_dob_type": "⏳ *Come aggiungere l'età?*",
        "ask_dob_date": "📅 Data nel formato **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Età direttamente come numero:",
        "ask_year": "📅 *Scegli l'anno:*",
        "ask_month": "📆 *Scegli il mese:*",
        "ask_day": "🗓️ *Scegli il giorno:*",
        "ask_hour": "⏰ *Ora (00 - 23):*",
        "ask_minute": "⏱️ *Minuto (00 - 59):*",
        "ask_photo": "📸 *Invia una foto* (o salta):",
        "ask_video": "🎥 *Invia un video* (o salta):",
        "ask_song": "🎶 *Invia una canzone* (o salta):",
        "ask_voice": "🎙️ *Messaggio vocale* (o salta):",
        "ask_audio": "🎵 *Altro audio* (o salta):",
        "ready": "✨ *Tutto pronto per {name}!*"
    },
    "tr": {
        "welcome": "✨ *Sürprizler dünyasına hoş geldiniz...*",
        "region_selected": "🌍 Bölge: *{region}*. Ülkenizi seçin:",
        "country_choice": "🗣️ *{country}* için dil seçin:",
        "lang_updated": "✅ Dil başarıyla güncellendi!",
        "ask_category": "🎉 *Bu nasıl bir kutlama?*",
        "ask_name": "✨ *Kimin özel gününü kutluyoruz? İsmini gönderin:*",
        "ask_wish": "📝 *Güzel bir mesaj yazın:*",
        "ask_dob_type": "⏳ *Yaş bilgisini nasıl eklemek istersiniz?*",
        "ask_dob_date": "📅 **YYYY-MM-DD** formatında tarih gönderin:",
        "ask_dob_direct": "🔢 Yaşı doğrudan sayı olarak girin:",
        "ask_year": "📅 *Yılı seçin:*",
        "ask_month": "📆 *Ayı seçin:*",
        "ask_day": "🗓️ *Günü seçin:*",
        "ask_hour": "⏰ *Saati seçin (00 - 23):*",
        "ask_minute": "⏱️ *Dakikayı seçin (00 - 59):*",
        "ask_photo": "📸 *Fotoğraf gönderin* (veya atlayın):",
        "ask_video": "🎥 *Video gönderin* (veya atlayın):",
        "ask_song": "🎶 *Şarkı gönderin* (veya atlayın):",
        "ask_voice": "🎙️ *Sesli mesaj* (veya atlayın):",
        "ask_audio": "🎵 *Ekstra ses dosyası* (veya atlayın):",
        "ready": "✨ *{name} için her şey hazır!*"
    },
    "id": {
        "welcome": "✨ *Selamat datang di dunia kejutan...*",
        "region_selected": "🌍 Wilayah: *{region}*. Pilih negara Anda:",
        "country_choice": "🗣️ Pilih bahasa untuk *{country}*:",
        "lang_updated": "✅ Bahasa berhasil diperbarui!",
        "ask_category": "🎉 *Perayaan apa ini?*",
        "ask_name": "✨ *Siapa yang merayakan hari spesial? Kirim namanya:*",
        "ask_wish": "📝 *Tulis pesan yang manis:*",
        "ask_dob_type": "⏳ *Bagaimana cara menambahkan usia?*",
        "ask_dob_date": "📅 Kirim tanggal format **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Masukkan usia langsung sebagai angka:",
        "ask_year": "📅 *Pilih tahun:*",
        "ask_month": "📆 *Pilih bulan:*",
        "ask_day": "🗓️ *Pilih hari:*",
        "ask_hour": "⏰ *Jam (00 sampai 23):*",
        "ask_minute": "⏱️ *Menit (00 sampai 59):*",
        "ask_photo": "📸 *Kirim foto* (atau lewati):",
        "ask_video": "🎥 *Kirim video* (atau lewati):",
        "ask_song": "🎶 *Kirim lagu* (atau lewati):",
        "ask_voice": "🎙️ *Pesan suara* (atau lewati):",
        "ask_audio": "🎵 *Audio lainnya* (atau lewati):",
        "ready": "✨ *Semuanya siap untuk {name}!*"
    },
    "ms": {
        "welcome": "✨ *Selamat datang ke dunia kejutan...*",
        "region_selected": "🌍 Wilayah: *{region}*. Pilih negara:",
        "country_choice": "🗣️ Bahasa untuk *{country}*:",
        "lang_updated": "✅ Bahasa berjaya dikemaskini!",
        "ask_category": "🎉 *Apakah jenis perayaan ini?*",
        "ask_name": "✨ *Siapa yang kita raikan hari ini? Nama:*",
        "ask_wish": "📝 *Tulis ucapan yang indah:*",
        "ask_dob_type": "⏳ *Bagaimana menambah umur?*",
        "ask_dob_date": "📅 Tarikh format **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Masukkan umur sebagai nombor:",
        "ask_year": "📅 *Pilih tahun:*",
        "ask_month": "📆 *Pilih bulan:*",
        "ask_day": "🗓️ *Pilih hari:*",
        "ask_hour": "⏰ *Jam (00 hingga 23):*",
        "ask_minute": "⏱️ *Minit (00 hingga 59):*",
        "ask_photo": "📸 *Kongsi foto* (atau langkau):",
        "ask_video": "🎥 *Kongsi video* (atau langkau):",
        "ask_song": "🎶 *Hantar lagu* (atau langkau):",
        "ask_voice": "🎙️ *Nota suara* (atau langkau):",
        "ask_audio": "🎵 *Audio tambahan* (atau langkau):",
        "ready": "✨ *Semua sedia untuk {name}!*"
    },
    "ja": {
        "welcome": "✨ *サプライズの世界へようこそ...*",
        "region_selected": "🌍 地域: *{region}*. 国を選択してください:",
        "country_choice": "🗣️ *{country}* の言語を選択:",
        "lang_updated": "✅ 言語が更新されました！",
        "ask_category": "🎉 *どんなお祝いですか？*",
        "ask_name": "✨ *誰のお祝いですか？お名前を送信してください:*",
        "ask_wish": "📝 *素敵なメッセージを書いてください:*",
        "ask_dob_type": "⏳ *年齢情報をどのように追加しますか？*",
        "ask_dob_date": "📅 日付を **YYYY-MM-DD** 形式で送信:",
        "ask_dob_direct": "🔢 年齢を数字で直接入力:",
        "ask_year": "📅 *年を選択:*",
        "ask_month": "📆 *月を選択:*",
        "ask_day": "🗓️ *日を選択:*",
        "ask_hour": "⏰ *時を選択 (00〜23):*",
        "ask_minute": "⏱️ *分を選択 (00〜59):*",
        "ask_photo": "📸 *写真を共有* (スキップ可):",
        "ask_video": "🎥 *動画を共有* (スキップ可):",
        "ask_song": "🎶 *曲を送信* (スキップ可):",
        "ask_voice": "🎙️ *音声メモを送信* (スキップ可):",
        "ask_audio": "🎵 *追加オーディオ* (スキップ可):",
        "ready": "✨ *{name} さんの準備が完了しました！*"
    },
    "ko": {
        "welcome": "✨ *서프라이즈의 세계에 오신 것을 환영합니다...*",
        "region_selected": "🌍 지역: *{region}*. 국가를 선택하세요:",
        "country_choice": "🗣️ *{country}* 언어 선택:",
        "lang_updated": "✅ 언어가 성공적으로 설정되었습니다!",
        "ask_category": "🎉 *어떤 축하 행사인가요?*",
        "ask_name": "✨ *오늘의 주인공은 누구인가요? 이름을 입력하세요:*",
        "ask_wish": "📝 *축하 메시지를 작성하세요:*",
        "ask_dob_type": "⏳ *나이 세부 정보를 어떻게 추가하시겠습니까?*",
        "ask_dob_date": "📅 날짜를 **YYYY-MM-DD** 형식으로 입력:",
        "ask_dob_direct": "🔢 나이를 숫자로 직접 입력:",
        "ask_year": "📅 *연도 선택:*",
        "ask_month": "📆 *월 선택:*",
        "ask_day": "🗓️ *일 선택:*",
        "ask_hour": "⏰ *시간 선택 (00~23):*",
        "ask_minute": "⏱️ *분 선택 (00~59):*",
        "ask_photo": "📸 *사진 공유* (또는 건너뛰기):",
        "ask_video": "🎥 *비디오 공유* (또는 건너뛰기):",
        "ask_song": "🎶 *노래 보내기* (또는 건너뛰기):",
        "ask_voice": "🎙️ *음성 메시지* (또는 건너뛰기):",
        "ask_audio": "🎵 *추가 오디오* (또는 건너뛰기):",
        "ready": "✨ *{name}님을 위한 모든 준비가 완료되었습니다!*"
    },
    "zh": {
        "welcome": "✨ *欢迎来到惊喜的世界...*",
        "region_selected": "🌍 地区: *{region}*. 请选择您的国家:",
        "country_choice": "🗣️ 选择 *{country}* 的语言:",
        "lang_updated": "✅ 语言设置已更新！",
        "ask_category": "🎉 *这是什么庆祝活动？*",
        "ask_name": "✨ *今天庆祝谁的特别日子？发送名字:*",
        "ask_wish": "📝 *写下温馨的祝福语:*",
        "ask_dob_type": "⏳ *如何添加年龄信息？*",
        "ask_dob_date": "📅 发送格式为 **YYYY-MM-DD** 的日期:",
        "ask_dob_direct": "🔢 直接输入数字年龄:",
        "ask_year": "📅 *选择年份:*",
        "ask_month": "📆 *选择月份:*",
        "ask_day": "🗓️ *选择日期:*",
        "ask_hour": "⏰ *选择小时 (00至23):*",
        "ask_minute": "⏱️ *选择分钟 (00至59):*",
        "ask_photo": "📸 *分享照片* (可跳过):",
        "ask_video": "🎥 *分享视频* (可跳过):",
        "ask_song": "🎶 *发送歌曲* (可跳过):",
        "ask_voice": "🎙️ *发送语音* (可跳过):",
        "ask_audio": "🎵 *添加额外音频* (可跳过):",
        "ready": "✨ *为 {name} 准备好了一切！*"
    },
    "vi": {
        "welcome": "✨ *Chào mừng bạn đến với thế giới của những bất ngờ...*",
        "region_selected": "🌍 Khu vực: *{region}*. Chọn quốc gia:",
        "country_choice": "🗣️ Chọn ngôn ngữ:",
        "lang_updated": "✅ Ngôn ngữ đã được cập nhật!",
        "ask_category": "🎉 *Đây là dịp kỷ niệm gì?*",
        "ask_name": "✨ *Tên người được chúc mừng:*",
        "ask_wish": "📝 *Viết lời chúc ý nghĩa:*",
        "ask_dob_type": "⏳ *Cách thêm thông tin tuổi?*",
        "ask_dob_date": "📅 Gửi ngày theo định dạng **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Nhập tuổi trực tiếp bằng số:",
        "ask_year": "📅 *Chọn năm:*",
        "ask_month": "📆 *Chọn tháng:*",
        "ask_day": "🗓️ *Chọn ngày:*",
        "ask_hour": "⏰ *Chọn Giờ (00 đến 23):*",
        "ask_minute": "⏱️ *Chọn Phút (00 đến 59):*",
        "ask_photo": "📸 *Chia sẻ ảnh* (hoặc bỏ qua):",
        "ask_video": "🎥 *Chia sẻ video* (hoặc bỏ qua):",
        "ask_song": "🎶 *Gửi bài hát* (hoặc bỏ qua):",
        "ask_voice": "🎙️ *Gửi tin nhắn thoại* (hoặc bỏ qua):",
        "ask_audio": "🎵 *Thêm âm thanh* (hoặc bỏ qua):",
        "ready": "✨ *Mọi thứ đã sẵn sàng cho {name}!*"
    },
    "fil": {
        "welcome": "✨ *Maligayang pagdating sa mundo ng mga sorpresa...*",
        "region_selected": "🌍 Rehiyon: *{region}*:",
        "country_choice": "🗣️ Wika:",
        "lang_updated": "✅ Na-update ang wika!",
        "ask_category": "🎉 *Anong pagdiriwang ito?*",
        "ask_name": "✨ *Pangalan ng nagdiriwang:*",
        "ask_wish": "📝 *Sumulat ng mensahe:*",
        "ask_dob_type": "⏳ *Paano ilalagay ang edad?*",
        "ask_dob_date": "📅 Petsa sa format na **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Ilagay ang edad bilang numero:",
        "ask_year": "📅 *Taon:*",
        "ask_month": "📆 *Buwan:*",
        "ask_day": "🗓️ *Araw:*",
        "ask_hour": "⏰ *Oras (00 hanggang 23):*",
        "ask_minute": "⏱️ *Minuto (00 hanggang 59):*",
        "ask_photo": "📸 *Larawan* (o lumaktaw):",
        "ask_video": "🎥 *Video* (o lumaktaw):",
        "ask_song": "🎶 *Kanta* (o lumaktaw):",
        "ask_voice": "🎙️ *Boses* (o lumaktaw):",
        "ask_audio": "🎵 *Karagdagang audio* (o lumaktaw):",
        "ready": "✨ *Handa na ang lahat para kay {name}!*"
    },
    "th": {
        "welcome": "✨ *ยินดีต้อนรับสู่โลกแห่งความประหลาดใจ...*",
        "region_selected": "🌍 ภูมิภาค: *{region}*:",
        "country_choice": "🗣️ เลือกภาษา:",
        "lang_updated": "✅ อัปเดตภาษาแล้ว!",
        "ask_category": "🎉 *นี่คืองานฉลองประเภทใด?*",
        "ask_name": "✨ *ส่งชื่อเจ้าของวันพิเศษ:*",
        "ask_wish": "📝 *เขียนคำอวยพรสุดพิเศษ:*",
        "ask_dob_type": "⏳ *จะใส่อายุอย่างไร?*",
        "ask_dob_date": "📅 ส่งวันที่ในรูปแบบ **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 ใส่อายุเป็นตัวเลข:",
        "ask_year": "📅 *เลือกปี:*",
        "ask_month": "📆 *เลือกเดือน:*",
        "ask_day": "🗓️ *เลือกวัน:*",
        "ask_hour": "⏰ *เลือกชั่วโมง (00 ถึง 23):*",
        "ask_minute": "⏱️ *เลือกนาที (00 ถึง 59):*",
        "ask_photo": "📸 *ส่งรูปภาพ:*",
        "ask_video": "🎥 *ส่งวิดีโอ:*",
        "ask_song": "🎶 *ส่งเพลง:*",
        "ask_voice": "🎙️ *ส่งข้อความเสียง:*",
        "ask_audio": "🎵 *เพิ่มเสียงพิเศษ:*",
        "ready": "✨ *ทุกอย่างพร้อมสำหรับ {name}!*"
    },
    "ne": {
        "welcome": "✨ *आश्चर्यको संसारमा स्वागत छ...*",
        "region_selected": "🌍 क्षेत्र: *{region}*:",
        "country_choice": "🗣️ भाषा छान्नुहोस्:",
        "lang_updated": "✅ भाषा अपडेट भयो!",
        "ask_category": "🎉 *यो कस्तो उत्सव हो?*",
        "ask_name": "✨ *नाम पठाउनुहोस्:*",
        "ask_wish": "📝 *एउटा राम्रो सन्देश लेख्नुहोस्:*",
        "ask_dob_type": "⏳ *उमेर विवरण कसरी थप्ने?*",
        "ask_dob_date": "📅 **YYYY-MM-DD** ढाँचामा मिति:",
        "ask_dob_direct": "🔢 उमेर अंकमा लेख्नुहोस्:",
        "ask_year": "📅 *वर्ष छान्नुहोस्:*",
        "ask_month": "📆 *महिना छान्नुहोस्:*",
        "ask_day": "🗓️ *दिन छान्नुहोस्:*",
        "ask_hour": "⏰ *घन्टा (00 देखि 23):*",
        "ask_minute": "⏱️ *मिनेट (00 देखि 59):*",
        "ask_photo": "📸 *फोटो पठाउनुहोस्:*",
        "ask_video": "🎥 *भिडियो पठाउनुहोस्:*",
        "ask_song": "🎶 *गीत पठाउनुहोस्:*",
        "ask_voice": "🎙️ *आवाज सन्देश:*",
        "ask_audio": "🎵 *थप अडियो:*",
        "ready": "✨ *{name} को लागि सबै तयार छ!*"
    },
    "si": {
        "welcome": "✨ *පුදුම කිරීම් ලෝකයට සාදරයෙන් පිළිගනිමු...*",
        "region_selected": "🌍 කලාපය: *{region}*:",
        "country_choice": "🗣️ භාෂාව තෝරන්න:",
        "lang_updated": "✅ භාෂාව යාවත්කාලීන විය!",
        "ask_category": "🎉 *මෙය කුමන උත්සවයක්ද?*",
        "ask_name": "✨ *නම එවන්න:*",
        "ask_wish": "📝 *සුබ පැතුම් පණිවිඩයක් ලියන්න:*",
        "ask_dob_type": "⏳ *වයස් තොරතුරු එක් කරන්නේ කෙසේද?*",
        "ask_dob_date": "📅 දිනය **YYYY-MM-DD** ආකෘතියෙන්:",
        "ask_dob_direct": "🔢 වයස ඉලක්කමෙන් ලියන්න:",
        "ask_year": "📅 *වසර තෝරන්න:*",
        "ask_month": "📆 *මාසය තෝරන්න:*",
        "ask_day": "🗓️ *දිනය තෝරන්න:*",
        "ask_hour": "⏰ *පැය (00 සිට 23):*",
        "ask_minute": "⏱️ *මිනිත්තු (00 සිට 59):*",
        "ask_photo": "📸 *ඡායාරූපය එවන්න:*",
        "ask_video": "🎥 *වීඩියෝව එවන්න:*",
        "ask_song": "🎶 *ගීතය එවන්න:*",
        "ask_voice": "🎙️ *හඬ පණිවිඩය:*",
        "ask_audio": "🎵 *තවත් ශ්‍රව්‍ය:*",
        "ready": "✨ *{name} සඳහා සියල්ල සූදානම්!*"
    },
    "az": {
        "welcome": "✨ *Sürprizlər dünyasına xoş gəlmisiniz...*",
        "region_selected": "🌍 Region: *{region}*:",
        "country_choice": "🗣️ Dil seçin:",
        "lang_updated": "✅ Dil yeniləndi!",
        "ask_category": "🎉 *Bu necə bir bayramdır?*",
        "ask_name": "✨ *Adı göndərin:*",
        "ask_wish": "📝 *Təbrik mesajı yazın:*",
        "ask_dob_type": "⏳ *Yaş necə əlavə edilsin?*",
        "ask_dob_date": "📅 **YYYY-MM-DD** formatında tarix:",
        "ask_dob_direct": "🔢 Yaşı rəqəmlə yazın:",
        "ask_year": "📅 *İl:*",
        "ask_month": "📆 *Ay:*",
        "ask_day": "🗓️ *Gün:*",
        "ask_hour": "⏰ *Saat (00 - 23):*",
        "ask_minute": "⏱️ *Dəqiqə (00 - 59):*",
        "ask_photo": "📸 *Şəkil:*",
        "ask_video": "🎥 *Video:*",
        "ask_song": "🎶 *Mahnı:*",
        "ask_voice": "🎙️ *Səs yazısı:*",
        "ask_audio": "🎵 *Əlavə audio:*",
        "ready": "✨ *{name} üçün hər şey hazırdır!*"
    },
    "hy": {
        "welcome": "✨ *Բարի գալուստ անակնկալների աշխարհ...*",
        "region_selected": "🌍 Տարածաշրջան: *{region}*:",
        "country_choice": "🗣️ Ընտրեք լեզուն:",
        "lang_updated": "✅ Լեզուն թարմացվեց:",
        "ask_category": "🎉 *Ինչ տեսակի տոն է:*",
        "ask_name": "✨ *Անունը:*",
        "ask_wish": "📝 *Շնորհավորական խոսք:*",
        "ask_dob_type": "⏳ *Տարիքը:*",
        "ask_dob_date": "📅 **YYYY-MM-DD** ձևաչափով:",
        "ask_dob_direct": "🔢 Ուղղակի տարիքը թվով:",
        "ask_year": "📅 *Տարի:*",
        "ask_month": "📆 *Ամիս:*",
        "ask_day": "🗓️ *Օր:*",
        "ask_hour": "⏰ *Ժամ (00-23):*",
        "ask_minute": "⏱️ *Րոպե (00-59):*",
        "ask_photo": "📸 *Լուսանկար:*",
        "ask_video": "🎥 *Տեսանյութ:*",
        "ask_song": "🎶 *Երգ:*",
        "ask_voice": "🎙️ *Ձայնային:*",
        "ask_audio": "🎵 *Աուդիո:*",
        "ready": "✨ *{name}-ի համար պատրաստ է:*"
    },
    "uz": {
        "welcome": "✨ *Kutilmagan sovg'alar olamiga xush kelibsiz...*",
        "region_selected": "🌍 Hudud: *{region}*:",
        "country_choice": "🗣️ Tilni tanlang:",
        "lang_updated": "✅ Til yangilandi!",
        "ask_category": "🎉 *Bu qanday bayram?*",
        "ask_name": "✨ *Ism yuboring:*",
        "ask_wish": "📝 *Tabrik yozing:*",
        "ask_dob_type": "⏳ *Yoshni qanday kiritasiz?*",
        "ask_dob_date": "📅 **YYYY-MM-DD** formatida sana:",
        "ask_dob_direct": "🔢 Yoshni raqamda kiriting:",
        "ask_year": "📅 *Yil:*",
        "ask_month": "📆 *Oy:*",
        "ask_day": "🗓️ *Kun:*",
        "ask_hour": "⏰ *Soat (00 dan 23 gacha):*",
        "ask_minute": "⏱️ *Daqiqa (00 dan 59 gacha):*",
        "ask_photo": "📸 *Rasm:*",
        "ask_video": "🎥 *Video:*",
        "ask_song": "🎶 *Qo'shiq:*",
        "ask_voice": "🎙️ *Ovozli xabar:*",
        "ask_audio": "🎵 *Qo'shimcha audio:*",
        "ready": "✨ *{name} uchun barchasi tayyor!*"
    },
    "tg": {
        "welcome": "✨ *Ба дунёи сюрпризҳо хуш омадед...*",
        "region_selected": "🌍 Минтақа: *{region}*:",
        "country_choice": "🗣️ Забонро интихоб кунед:",
        "lang_updated": "✅ Забон нав шуд!",
        "ask_category": "🎉 *Ин чӣ гуна ҷашн аст?*",
        "ask_name": "✨ *Номро фиристед:*",
        "ask_wish": "📝 *Паёми табрикӣ нависед:*",
        "ask_dob_type": "⏳ *Синну солро чӣ тавр ворид мекунед?*",
        "ask_dob_date": "📅 Сана бо шакли **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Синну солро бо рақам нависед:",
        "ask_year": "📅 *Сол:*",
        "ask_month": "📆 *Моҳ:*",
        "ask_day": "🗓️ *Рӯз:*",
        "ask_hour": "⏰ *Соат (00 то 23):*",
        "ask_minute": "⏱️ *Дақиқа (00 то 59):*",
        "ask_photo": "📸 *Акс:*",
        "ask_video": "🎥 *Видео:*",
        "ask_song": "🎶 *Суруд:*",
        "ask_voice": "🎙️ *Паёми овозӣ:*",
        "ask_audio": "🎵 *Аудиои иловагӣ:*",
        "ready": "✨ *Барои {name} ҳама чиз омода аст!*"
    },
    "fa": {
        "welcome": "✨ *به دنیای شگفتی‌ها خوش آمدید...*",
        "region_selected": "🌍 منطقه: *{region}*:",
        "country_choice": "🗣️ انتخاب زبان:",
        "lang_updated": "✅ زبان به‌روز شد!",
        "ask_category": "🎉 *این چه جشنی است؟*",
        "ask_name": "✨ *نام را بفرستید:*",
        "ask_wish": "📝 *یک پیام بنویسید:*",
        "ask_dob_type": "⏳ *سن را چگونه اضافه می‌کنید؟*",
        "ask_dob_date": "📅 تاریخ **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 سن را با عدد وارد کنید:",
        "ask_year": "📅 *سال:*",
        "ask_month": "📆 *ماه:*",
        "ask_day": "🗓️ *روز:*",
        "ask_hour": "⏰ *ساعت (00 تا 23):*",
        "ask_minute": "⏱️ *دقیقه (00 تا 59):*",
        "ask_photo": "📸 *عکس:*",
        "ask_video": "🎥 *ویدیو:*",
        "ask_song": "🎶 *آهنگ:*",
        "ask_voice": "🎙️ *ویس:*",
        "ask_audio": "🎵 *صوت اضافی:*",
        "ready": "✨ *همه چیز برای {name} آماده است!*"
    },
    "my": {
        "welcome": "✨ *အံ့သြဖွယ်ရာ ကမ္ဘာမှ ကြိုဆိုပါတယ်...*",
        "region_selected": "🌍 ဒေသ: *{region}*:",
        "country_choice": "🗣️ ဘာသာစကား ရွေးပါ:",
        "lang_updated": "✅ ဘာသာစကား ပြောင်းလဲပြီးပါပြီ!",
        "ask_category": "🎉 *ဘာပွဲကျင်းပတာလဲ?*",
        "ask_name": "✨ *နာမည် ပို့ပေးပါ:*",
        "ask_wish": "📝 *ဆုတောင်းစကား ရေးပါ:*",
        "ask_dob_type": "⏳ *အသက်အချက်အလက် ထည့်ရန်:*",
        "ask_dob_date": "📅 ရက်စွဲ **YYYY-MM-DD** ပုံစံဖြင့်:",
        "ask_dob_direct": "🔢 အသက်ကို နံပါတ်ဖြင့် ရိုက်ထည့်ပါ:",
        "ask_year": "📅 *နှစ်:*",
        "ask_month": "📆 *လ:*",
        "ask_day": "🗓️ *ရက်:*",
        "ask_hour": "⏰ *နာရီ (00 မှ 23):*",
        "ask_minute": "⏱️ *မိနစ် (00 မှ 59):*",
        "ask_photo": "📸 *ဓာတ်ပုံ:*",
        "ask_video": "🎥 *ဗီဒီယို:*",
        "ask_song": "🎶 *သီချင်း:*",
        "ask_voice": "🎙️ *အသံမက်ဆေ့ခ်ျ:*",
        "ask_audio": "🎵 *အသံဖိုင်:*",
        "ready": "✨ *{name} အတွက် အဆင်သင့်ဖြစ်ပါပြီ!*"
    },
    "nl": {
        "welcome": "✨ *Welkom in de wereld van verrassingen...*",
        "region_selected": "🌍 Regio: *{region}*:",
        "country_choice": "🗣️ Kies uw taal:",
        "lang_updated": "✅ Taal succesvol bijgewerkt!",
        "ask_category": "🎉 *Wat voor feest is dit?*",
        "ask_name": "✨ *Stuur de naam:*",
        "ask_wish": "📝 *Schrijf een lieve wens:*",
        "ask_dob_type": "⏳ *Hoe wilt u de leeftijd toevoegen?*",
        "ask_dob_date": "📅 Datum in **YYYY-MM-DD** formaat:",
        "ask_dob_direct": "🔢 Voer de leeftijd direct in als getal:",
        "ask_year": "📅 *Kies het jaar:*",
        "ask_month": "📆 *Kies de maand:*",
        "ask_day": "🗓️ *Kies de dag:*",
        "ask_hour": "⏰ *Uur (00 tot 23):*",
        "ask_minute": "⏱️ *Minuut (00 tot 59):*",
        "ask_photo": "📸 *Foto:*",
        "ask_video": "🎥 *Video:*",
        "ask_song": "🎶 *Lied:*",
        "ask_voice": "🎙️ *Spraakbericht:*",
        "ask_audio": "🎵 *Extra audio:*",
        "ready": "✨ *Alles staat klaar voor {name}!*"
    },
    "pl": {
        "welcome": "✨ *Witaj w świecie niespodzianek...*",
        "region_selected": "🌍 Region: *{region}*:",
        "country_choice": "🗣️ Wybierz język:",
        "lang_updated": "✅ Język zaktualizowany!",
        "ask_category": "🎉 *Jaka to uroczystość?*",
        "ask_name": "✨ *Podaj imię:*",
        "ask_wish": "📝 *Napisz piękne życzenia:*",
        "ask_dob_type": "⏳ *Jak dodać wiek?*",
        "ask_dob_date": "📅 Data w formacie **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Podaj wiek bezpośrednio jako liczbę:",
        "ask_year": "📅 *Wybierz rok:*",
        "ask_month": "📆 *Wybierz miesiąc:*",
        "ask_day": "🗓️ *Wybierz dzień:*",
        "ask_hour": "⏰ *Godzina (00 do 23):*",
        "ask_minute": "⏱️ *Minuta (00 do 59):*",
        "ask_photo": "📸 *Zdjęcie:*",
        "ask_video": "🎥 *Wideo:*",
        "ask_song": "🎶 *Piosenka:*",
        "ask_voice": "🎙️ *Wiadomość głosowa:*",
        "ask_audio": "🎵 *Dodatkowe audio:*",
        "ready": "✨ *Wszystko gotowe dla {name}!*"
    },
    "uk": {
        "welcome": "✨ *Ласкаво просимо у світ сюрпризів...*",
        "region_selected": "🌍 Регіон: *{region}*:",
        "country_choice": "🗣️ Оберіть мову:",
        "lang_updated": "✅ Мову оновлено!",
        "ask_category": "🎉 *Яке це свято?*",
        "ask_name": "✨ *Введіть ім'я:*",
        "ask_wish": "📝 *Напишіть щире побажання:*",
        "ask_dob_type": "⏳ *Як додати вік?*",
        "ask_dob_date": "📅 Дата у форматі **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Введіть вік числом:",
        "ask_year": "📅 *Оберіть рік:*",
        "ask_month": "📆 *Оберіть місяць:*",
        "ask_day": "🗓️ *Оберіть день:*",
        "ask_hour": "⏰ *Година (00 до 23):*",
        "ask_minute": "⏱️ *Хвилина (00 до 59):*",
        "ask_photo": "📸 *Фото:*",
        "ask_video": "🎥 *Відео:*",
        "ask_song": "🎶 *Пісня:*",
        "ask_voice": "🎙️ *Голосове повідомлення:*",
        "ask_audio": "🎵 *Додаткове аудіо:*",
        "ready": "✨ *Все готово для {name}!*"
    },
    "be": {
        "welcome": "✨ *Сардэчна запрашаем у свет сюрпрызаў...*",
        "region_selected": "🌍 Рэгіён: *{region}*:",
        "country_choice": "🗣️ Абярыце мову:",
        "lang_updated": "✅ Мова абноўлена!",
        "ask_category": "🎉 *Якое гэта свята?*",
        "ask_name": "✨ *Увядзіце імя:*",
        "ask_wish": "📝 *Напішыце пажаданне:*",
        "ask_dob_type": "⏳ *Як пазначыць узрост?*",
        "ask_dob_date": "📅 Дата ў фармаце **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Увядзіце ўзрост лічбай:",
        "ask_year": "📅 *Год:*",
        "ask_month": "📆 *Месяц:*",
        "ask_day": "🗓️ *Дзень:*",
        "ask_hour": "⏰ *Гадзіна (00 да 23):*",
        "ask_minute": "⏱️ *Хвіліна (00 да 59):*",
        "ask_photo": "📸 *Фота:*",
        "ask_video": "🎥 *Відэа:*",
        "ask_song": "🎶 *Песня:*",
        "ask_voice": "🎙️ *Галасавое паведамленне:*",
        "ask_audio": "🎵 *Дадатковае аўдыё:*",
        "ready": "✨ *Усё гатова для {name}!*"
    },
    "sv": {
        "welcome": "✨ *Välkommen till överraskningarnas värld...*",
        "region_selected": "🌍 Region: *{region}*:",
        "country_choice": "🗣️ Välj språk:",
        "lang_updated": "✅ Språket har uppdaterats!",
        "ask_category": "🎉 *Vad för slags firande är detta?*",
        "ask_name": "✨ *Skicka namn:*",
        "ask_wish": "📝 *Skriv ett fint meddelande:*",
        "ask_dob_type": "⏳ *Hur vill du ange ålder?*",
        "ask_dob_date": "📅 Datum i **YYYY-MM-DD** format:",
        "ask_dob_direct": "🔢 Ange åldern som en siffra:",
        "ask_year": "📅 *Välj år:*",
        "ask_month": "📆 *Välj månad:*",
        "ask_day": "🗓️ *Välj dag:*",
        "ask_hour": "⏰ *Timme (00 till 23):*",
        "ask_minute": "⏱️ *Minut (00 till 59):*",
        "ask_photo": "📸 *Foto:*",
        "ask_video": "🎥 *Video:*",
        "ask_song": "🎶 *Låt:*",
        "ask_voice": "🎙️ *Röstmeddelande:*",
        "ask_audio": "🎵 *Extra ljud:*",
        "ready": "✨ *Allt är klart för {name}!*"
    },
    "el": {
        "welcome": "✨ *Καλώς ήρθατε στον κόσμο των εκπλήξεων...*",
        "region_selected": "🌍 Περιοχή: *{region}*:",
        "country_choice": "🗣️ Επιλέξτε γλώσσα:",
        "lang_updated": "✅ Η γλώσσα ενημερώθηκε!",
        "ask_category": "🎉 *Τι είδους γιορτή είναι;*",
        "ask_name": "✨ *Στείλτε το όνομα:*",
        "ask_wish": "📝 *Γράψτε μια ευχή:*",
        "ask_dob_type": "⏳ *Πώς θέλετε να προσθέσετε την ηλικία;*",
        "ask_dob_date": "📅 Ημερομηνία σε μορφή **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Εισαγάγετε την ηλικία ως αριθμό:",
        "ask_year": "📅 *Έτος:*",
        "ask_month": "📆 *Μήνας:*",
        "ask_day": "🗓️ *Ημέρα:*",
        "ask_hour": "⏰ *Ώρα (00 έως 23):*",
        "ask_minute": "⏱️ *Λεπτό (00 έως 59):*",
        "ask_photo": "📸 *Φωτογραφία:*",
        "ask_video": "🎥 *Βίντεο:*",
        "ask_song": "🎶 *Τραγούδι:*",
        "ask_voice": "🎙️ *Φωνητικό μήνυμα:*",
        "ask_audio": "🎵 *Επιπλέον ήχος:*",
        "ready": "✨ *Όλα έτοιμα για τον/την {name}!*"
    },
    "ro": {
        "welcome": "✨ *Bun venit în lumea surprizelor...*",
        "region_selected": "🌍 Regiune: *{region}*:",
        "country_choice": "🗣️ Alegeți limba:",
        "lang_updated": "✅ Limba a fost actualizată!",
        "ask_category": "🎉 *Ce fel de sărbătoare este?*",
        "ask_name": "✨ *Trimiteți numele:*",
        "ask_wish": "📝 *Scrieți o urare frumoasă:*",
        "ask_dob_type": "⏳ *Cum doriți să adăugați vârsta?*",
        "ask_dob_date": "📅 Data în format **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Introduceți vârsta direct ca număr:",
        "ask_year": "📅 *Anul:*",
        "ask_month": "📆 *Luna:*",
        "ask_day": "🗓️ *Ziua:*",
        "ask_hour": "⏰ *Ora (00 - 23):*",
        "ask_minute": "⏱️ *Minutul (00 - 59):*",
        "ask_photo": "📸 *Poză:*",
        "ask_video": "🎥 *Video:*",
        "ask_song": "🎶 *Melodie:*",
        "ask_voice": "🎙️ *Mesaj vocal:*",
        "ask_audio": "🎵 *Audio suplimentar:*",
        "ready": "✨ *Totul este gata pentru {name}!*"
    },
    "cs": {
        "welcome": "✨ *Vítejte ve světě překvapení...*",
        "region_selected": "🌍 Region: *{region}*:",
        "country_choice": "🗣️ Vyberte jazyk:",
        "lang_updated": "✅ Jazyk byl úspěšně aktualizován!",
        "ask_category": "🎉 *O jakou oslavu se jedná?*",
        "ask_name": "✨ *Pošlete jméno:*",
        "ask_wish": "📝 *Napište hezké přání:*",
        "ask_dob_type": "⏳ *Jak chcete zadat věk?*",
        "ask_dob_date": "📅 Datum ve formátu **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Zadejte věk jako číslo:",
        "ask_year": "📅 *Rok:*",
        "ask_month": "📆 *Měsíc:*",
        "ask_day": "🗓️ *Den:*",
        "ask_hour": "⏰ *Hodina (00 až 23):*",
        "ask_minute": "⏱️ *Minuta (00 až 59):*",
        "ask_photo": "📸 *Fotka:*",
        "ask_video": "🎥 *Video:*",
        "ask_song": "🎶 *Písnička:*",
        "ask_voice": "🎙️ *Hlasová zpráva:*",
        "ask_audio": "🎵 *Další zvuk:*",
        "ready": "✨ *Vše je připraveno pro {name}!*"
    },
    "sw": {
        "welcome": "✨ *Karibu kwenye ulimwengu wa mshangao...*",
        "region_selected": "🌍 Eneo: *{region}*:",
        "country_choice": "🗣️ Chagua lugha:",
        "lang_updated": "✅ Lugha imesasishwa!",
        "ask_category": "🎉 *Hii ni sherehe ya aina gani?*",
        "ask_name": "✨ *Tuma jina:*",
        "ask_wish": "📝 *Andika ujumbe mtamu:*",
        "ask_dob_type": "⏳ *Jinsi ya kuongeza umri?*",
        "ask_dob_date": "📅 Tarehe kwa muundo **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Weka umri moja kwa moja kama nambari:",
        "ask_year": "📅 *Mwaka:*",
        "ask_month": "📆 *Mwezi:*",
        "ask_day": "🗓️ *Siku:*",
        "ask_hour": "⏰ *Saa (00 hadi 23):*",
        "ask_minute": "⏱️ *Dakika (00 hadi 59):*",
        "ask_photo": "📸 *Picha:*",
        "ask_video": "🎥 *Video:*",
        "ask_song": "🎶 *Wimbo:*",
        "ask_voice": "🎙️ *Ujumbe wa sauti:*",
        "ask_audio": "🎵 *Sauti ya ziada:*",
        "ready": "✨ *Kila kitu kiko tayari kwa {name}!*"
    },
    "ha": {
        "welcome": "✨ *Barka da zuwa duniyar abubuwan mamaki...*",
        "region_selected": "🌍 Yanki: *{region}*:",
        "country_choice": "🗣️ Zaɓi yare:",
        "lang_updated": "✅ An sabunta yare!",
        "ask_category": "🎉 *Wane irin biki ne wannan?*",
        "ask_name": "✨ *Aika suna:*",
        "ask_wish": "📝 *Rubuta sakon fatan alheri:*",
        "ask_dob_type": "⏳ *Yaya kake son ƙara shekaru?*",
        "ask_dob_date": "📅 Kwanan wata a tsarin **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Shigar da shekaru kai tsaye a matsayin lamba:",
        "ask_year": "📅 *Zaɓi shekara:*",
        "ask_month": "📆 *Wata:*",
        "ask_day": "🗓️ *Rana:*",
        "ask_hour": "⏰ *Awa (00 zuwa 23):*",
        "ask_minute": "⏱️ *Minti (00 zuwa 59):*",
        "ask_photo": "📸 *Hoto:*",
        "ask_video": "🎥 *Bidiyo:*",
        "ask_song": "🎶 *Waƙa:*",
        "ask_voice": "🎙️ *Saƙon murya:*",
        "ask_audio": "🎵 *Ƙarin sauti:*",
        "ready": "✨ *Komai a shirye yake don {name}!*"
    },
    "yo": {
        "welcome": "✨ *Kaabọ si agbaye ti awọn iyalẹnu...*",
        "region_selected": "🌍 Agbegbe: *{region}*:",
        "country_choice": "🗣️ Yan ede:",
        "lang_updated": "✅ Ede ti ni imudojuiwọn!",
        "ask_category": "🎉 *Iru ayẹyẹ wo ni eyi?*",
        "ask_name": "✨ *Fi orukọ ranṣẹ:*",
        "ask_wish": "📝 *Kọ ifiranṣẹ rere:*",
        "ask_dob_type": "⏳ *Bawo ni o ṣe fẹ fi ọjọ-ori kun?*",
        "ask_dob_date": "📅 Ọjọ ni ọna kika **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Tẹ ọjọ-ori sii gẹgẹbi nọmba:",
        "ask_year": "📅 *Ọdun:*",
        "ask_month": "📆 *Oṣu:*",
        "ask_day": "🗓️ *Ọjọ:*",
        "ask_hour": "⏰ *Wakati (00 si 23):*",
        "ask_minute": "⏱️ *Iṣẹju (00 si 59):*",
        "ask_photo": "📸 *Fọto:*",
        "ask_video": "🎥 *Fidio:*",
        "ask_song": "🎶 *Orin:*",
        "ask_voice": "🎙️ *Ohun:*",
        "ask_audio": "🎵 *Ohun afikun:*",
        "ready": "✨ *Gbogbo rẹ ti ṣetan fun {name}!*"
    },
    "zu": {
        "welcome": "✨ *Siyakwamukela emhlabeni wezimanga...*",
        "region_selected": "🌍 Isifunda: *{region}*:",
        "country_choice": "🗣️ Khetha ulimi:",
        "lang_updated": "✅ Ulimi lubuyekeziwe!",
        "ask_category": "🎉 *Lolu uhlobo luni lomkhosi?*",
        "ask_name": "✨ *Thumela igama:*",
        "ask_wish": "📝 *Bhala umyalezo omuhle:*",
        "ask_dob_type": "⏳ *Ungathanda ukwengeza kanjani iminyaka?*",
        "ask_dob_date": "📅 Usuku ngefomethi **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Faka iminyaka ngqo njengenombolo:",
        "ask_year": "📅 *Unyaka:*",
        "ask_month": "📆 *Inyanga:*",
        "ask_day": "🗓️ *Usuku:*",
        "ask_hour": "⏰ *Ihora (00 kuya ku 23):*",
        "ask_minute": "⏱️ *Umzuzu (00 kuya ku 59):*",
        "ask_photo": "📸 *Isithombe:*",
        "ask_video": "🎥 *Ividiyo:*",
        "ask_song": "🎶 *Ingoma:*",
        "ask_voice": "🎙️ *Izwi:*",
        "ask_audio": "🎵 *Umsindo owengeziwe:*",
        "ready": "✨ *Konke sekulungele u-{name}!*"
    },
    "xh": {
        "welcome": "✨ *Wamkelekile kwihlabathi lezimanga...*",
        "region_selected": "🌍 Ummandla: *{region}*:",
        "country_choice": "🗣️ Khetha ulwimi:",
        "lang_updated": "✅ Ulwimi luhlaziyiwe!",
        "ask_category": "🎉 *Loluphi uhlobo lombhiyozo olu?*",
        "ask_name": "✨ *Thumela igama:*",
        "ask_wish": "📝 *Bhala umyalezo omnandi:*",
        "ask_dob_type": "⏳ *Ungathanda ukongeza njani iminyaka?*",
        "ask_dob_date": "📅 Umhla ngendlela **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Faka iminyaka ngqo njengenombolo:",
        "ask_year": "📅 *Unyaka:*",
        "ask_month": "📆 *Inyanga:*",
        "ask_day": "🗓️ *Usuku:*",
        "ask_hour": "⏰ *Iyure (00 ukuya ku 23):*",
        "ask_minute": "⏱️ *Umzuzu (00 ukuya ku 59):*",
        "ask_photo": "📸 *Ifoto:*",
        "ask_video": "🎥 *Ividiyo:*",
        "ask_song": "🎶 *Ingoma:*",
        "ask_voice": "🎙️ *Ilizwi:*",
        "ask_audio": "🎵 *Isandi esongezelelweyo:*",
        "ready": "✨ *Yonke into ilungile ku-{name}!*"
    },
    "af": {
        "welcome": "✨ *Welkom in die wêreld van verrassings...*",
        "region_selected": "🌍 Streek: *{region}*:",
        "country_choice": "🗣️ Kies jou taal:",
        "lang_updated": "✅ Taal suksesvol opgedateer!",
        "ask_category": "🎉 *Watter soort viering is dit?*",
        "ask_name": "✨ *Stuur die naam:*",
        "ask_wish": "📝 *Skryf 'n lieflike boodskap:*",
        "ask_dob_type": "⏳ *Hoe wil jy ouderdomsbesonderhede byvoeg?*",
        "ask_dob_date": "📅 Datum in **YYYY-MM-DD** formaat:",
        "ask_dob_direct": "🔢 Voer ouderdom direk as 'n getal in:",
        "ask_year": "📅 *Jaar:*",
        "ask_month": "📆 *Maand:*",
        "ask_day": "🗓️ *Dag:*",
        "ask_hour": "⏰ *Uur (00 tot 23):*",
        "ask_minute": "⏱️ *Minuut (00 tot 59):*",
        "ask_photo": "📸 *Foto:*",
        "ask_video": "🎥 *Video:*",
        "ask_song": "🎶 *Liedjie:*",
        "ask_voice": "🎙️ *Stemnota:*",
        "ask_audio": "🎵 *Ekstra oudio:*",
        "ready": "✨ *Alles is gereed vir {name}!*"
    },
    "am": {
        "welcome": "✨ *ወደ አስደናቂ ነገሮች ዓለም እንኳን በደህና መጡ...*",
        "region_selected": "🌍 ክልል: *{region}*:",
        "country_choice": "🗣️ ቋንቋ ይምረጡ:",
        "lang_updated": "✅ ቋንቋው ተቀይሯል!",
        "ask_category": "🎉 *ይህ ምን ዓይነት በዓል ነው?*",
        "ask_name": "✨ *ስም ይላኩ:*",
        "ask_wish": "📝 *መልካም ምኞት ይጻፉ:*",
        "ask_dob_type": "⏳ *ዕድሜን እንዴት ማከል ይፈልጋሉ?*",
        "ask_dob_date": "📅 ቀን በ **YYYY-MM-DD** ቅርጸት:",
        "ask_dob_direct": "🔢 ዕድሜን በቀጥታ በቁጥር ያስገቡ:",
        "ask_year": "📅 *ዓመት:*",
        "ask_month": "📆 *ወር:*",
        "ask_day": "🗓️ *ቀን:*",
        "ask_hour": "⏰ *ሰዓት (00 እስከ 23):*",
        "ask_minute": "⏱️ *ደቂቃ (00 እስከ 59):*",
        "ask_photo": "📸 *ፎቶ:*",
        "ask_video": "🎥 *ቪዲዮ:*",
        "ask_song": "🎶 *ዘፈን:*",
        "ask_voice": "🎙️ *የድምጽ መልእክት:*",
        "ask_audio": "🎵 *ተጨማሪ ድምጽ:*",
        "ready": "✨ *ሁሉም ነገር ለ {name} ዝግጁ ነው!*"
    }
}

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
        [InlineKeyboardButton(text="💍 Wedding Anniversary", callback_data="cat_Wedding")],
        [InlineKeyboardButton(text="👶 New Born", callback_data="cat_NewBorn")],
        [InlineKeyboardButton(text="🎓 Graduation", callback_data="cat_Graduation")],
        [InlineKeyboardButton(text="🌟 Other Celebration", callback_data="cat_Other")]
    ])

def get_action_keyboard():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✨ Skip", callback_data="skip_step"), InlineKeyboardButton(text="↩️ Change", callback_data="change_step")]
    ])

# /start കമാൻഡ് - ചാനൽ പരിശോധന പൂർണ്ണമായി ഒഴിവാക്കി
@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
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
    # ഇൻബിൽറ്റ് "Enter Age Details" ബട്ടൺ
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

# 00 മുതൽ 59 വരെയുള്ള എല്ലാ മിനിറ്റുകളും ഇൻബിൽറ്റ്
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
    
    y = data.get("target_year", "")
    m = data.get("target_month", "")
    d = data.get("target_day", "")
    h = data.get("target_hour", "00")
    mn = data.get("target_minute", "00")
    
    target_time_str = ""
    if y and m and d:
        target_time_str = f"{y}-{m}-{d}T{h}:{mn}:00"

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
    
    share_text = f"✨ Check out this amazing surprise celebration for {params['name']}! 🎉 {view_url}"
    tg_share = f"https://t.me/share/url?url={view_url}&text=✨ Check out this amazing surprise celebration! 🎉"
    wa_share = f"https://api.whatsapp.com/send?text={share_text}"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🤍 Preview Surprise", web_app=WebAppInfo(url=preview_url)),
            InlineKeyboardButton(text="🎂 My Birthday View", web_app=WebAppInfo(url=view_url))
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

async def main():
    await asyncio.gather(web_server(), dp.start_polling(bot))

if __name__ == "__main__":
    asyncio.run(main())
