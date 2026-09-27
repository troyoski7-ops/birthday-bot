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

# --- 40+ രാജ്യങ്ങളുടെയും ഭാഷകളുടെയും സമ്പൂർണ്ണ ബോട്ട് ടെക്സ്റ്റ് ഡിക്ഷണറി ---
BOT_TEXTS = {
    "en": {
        "welcome": "✨ *Welcome to your little corner of surprises...*\n\nYour language is currently set to *English*.",
        "region_selected": "🌍 Region: *{region}*. Select your country:",
        "country_choice": "🗣️ Choose your language for *{country}*:",
        "lang_updated": "✅ Language preference updated successfully!",
        "ask_category": "🎉 *What kind of celebration is this?* Choose below:",
        "ask_name": "✨ *Whose special occasion are we celebrating today?* Send me their name:",
        "ask_wish": "📝 *Write a sweet, heartfelt wish or message for them*:",
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
        "ready": "✨ *All ready for {name}!*",
    },
    "ml": {
        "welcome": "✨ *ചെറിയ സർപ്രൈസുകളുടെ ലോകത്തേക്ക് സ്വാഗതം...*\n\nനിങ്ങളുടെ ഭാഷ ഇപ്പോൾ *മലയാളം* ആണ്.",
        "region_selected": "🌍 പ്രദേശം: *{region}*. നിങ്ങളുടെ രാജ്യം തിരഞ്ഞെടുക്കൂ:",
        "country_choice": "🗣️ *{country}*-നുള്ള ഭാഷ തിരഞ്ഞെടുക്കൂ:",
        "lang_updated": "✅ ഭാഷ വിജയകരമായി മാറ്റിയിരിക്കുന്നു!",
        "ask_category": "🎉 *ഇത് എന്തുതരം ആഘോഷമാണ്?*",
        "ask_name": "✨ *ഇന്ന് ആരുടെ വിശേഷമാണ് ആഘോഷിക്കുന്നത്? പേര് അയക്കൂ:*",
        "ask_wish": "📝 *അവർക്കായി ആശംസ എഴുതൂ:*",
        "ask_dob_type": "⏳ *സ്റ്റാറ്റിസ്റ്റിക്സിനായി തീയതി എങ്ങനെ നൽകണം?*",
        "ask_dob_date": "📅 തീയതി **YYYY-MM-DD** ഫോർമാറ്റിൽ അയക്കൂ (ഉദാഹരണത്തിന്: `2003-12-24`):",
        "ask_dob_direct": "🔢 വയസ്സ് മാത്രം നമ്പർ ആയി നൽകൂ (ഉദാഹരണത്തിന്: `22`):",
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
    },
    "hi": {
        "welcome": "✨ *सरप्राइज की इस छोटी सी दुनिया में आपका स्वागत है...*",
        "region_selected": "🌍 क्षेत्र: *{region}*. अपना देश चुनें:",
        "country_choice": "🗣️ *{country}* के लिए अपनी भाषा चुनें:",
        "lang_updated": "✅ भाषा सफलतापूर्वक अपडेट कर दी गई है!",
        "ask_category": "🎉 *यह किस प्रकार का उत्सव है?*",
        "ask_name": "✨ *आज हम किसका जश्न मना रहे हैं? नाम भेजें:*",
        "ask_wish": "📝 *एक प्यारा सा संदेश लिखें:*",
        "ask_dob_type": "⏳ *सांख्यिकी के लिए आयु विवरण कैसे जोड़ना चाहेंगे?*",
        "ask_dob_date": "📅 कृपया **YYYY-MM-DD** प्रारूप में तिथि भेजें:",
        "ask_dob_direct": "🔢 सीधी आयु संख्या में दर्ज करें:",
        "ask_year": "📅 *वर्ष चुनें:*",
        "ask_month": "📆 *महीना चुनें:*",
        "ask_day": "🗓️ *तारीख चुनें:*",
        "ask_hour": "⏰ *घंटा चुनें (00 से 23):*",
        "ask_minute": "⏱️ *मिनट चुनें (00 से 59):*",
        "ask_photo": "📸 *फोटो शेयर करें* (या छोड़ें):",
        "ask_video": "🎥 *वीडियो शेयर करें* (या छोड़ें):",
        "ask_song": "🎶 *गाना भेजें* (या छोड़ें):",
        "ask_voice": "🎙️ *वॉयस नोट भेजें* (या छोड़ें):",
        "ask_audio": "🎵 *एक और ऑडियो फाइल जोड़ें* (या छोड़ें):",
        "ready": "✨ *{name} के लिए सब तैयार है!*",
    },
    "te": {
        "welcome": "✨ *సర్ప్రైజ్ ప్రపంచానికి స్వాగతం...*",
        "region_selected": "🌍 ప్రాంతం: *{region}*. మీ దేశాన్ని ఎంచుకోండి:",
        "country_choice": "🗣️ *{country}* కోసం మీ భాషను ఎంచుకోండి:",
        "lang_updated": "✅ భాష வெற்றிகரமாக నవీకరించబడింది!",
        "ask_category": "🎉 *ఇది ఏ రకమైన వేడుక?*",
        "ask_name": "✨ *ఈరోజు ఎవరి ప్రత్యేక సందర్భం జరుపుకుంటున్నాము? పేరు పంపండి:*",
        "ask_wish": "📝 *ఒక మంచి సందేశం రాయండి:*",
        "ask_dob_type": "⏳ *వయస్సు వివరాలను ఎలా జోడించాలనుకుంటున్నారు?*",
        "ask_dob_date": "📅 **YYYY-MM-DD** ფორმატში თარიღი:",
        "ask_dob_direct": "🔢 നേരിട്ടുള്ള వయస్సును సంఖ్యగా ఇవ్వండి:",
        "ask_year": "📅 *సంవత్సరాన్ని ఎంచుకోండి:*",
        "ask_month": "📆 *నెలను ఎంచుకోండి:*",
        "ask_day": "🗓️ *తేదీని ఎంచుకోండి:*",
        "ask_hour": "⏰ *గంటను ఎంచుకోండి (00 నుండి 23):*",
        "ask_minute": "⏱️ *నిమిషాన్ని ఎంచుకోండి (00 నుండి 59):*",
        "ask_photo": "📸 *ఫోటోను పంచుకోండి* (లేదా దాటవేయి):",
        "ask_video": "🎥 *వీడియోను పంచుకోండి* (లేదా దాటవేయి):",
        "ask_song": "🎶 *పాటను పంపండి* (లేదా దాటవేయి):",
        "ask_voice": "🎙️ *వాయిస్ నోట్ పంపండి* (లేదా దాటవేయి):",
        "ask_audio": "🎵 *మరో ఆడియో ఫైల్‌ను జోడించండి* (లేదా దాటవేయి):",
        "ready": "✨ *{name} కోసం అన్నీ సిద్ధంగా ఉన్నాయి!*",
    },
    "kn": {
        "welcome": "✨ *ಅಚ್ಚರಿಗಳ ಜಗತ್ತಿಗೆ ಸ್ವಾಗತ...*",
        "region_selected": "🌍 ಪ್ರದೇಶ: *{region}*. ನಿಮ್ಮ ದೇಶವನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
        "country_choice": "🗣️ *{country}* ಗಾಗಿ ನಿಮ್ಮ ಭಾಷೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ:",
        "lang_updated": "✅ ಭಾಷೆಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ನವೀಕರಿಸಲಾಗಿದೆ!",
        "ask_category": "🎉 *ಇದು ಯಾವ ರೀತಿಯ ಹಬ್ಬ/ವೇడుಕೆ?*",
        "ask_name": "✨ *ಇವತ್ತು ಯಾರ ವಿಶೇಷ ಸಂದರ್ಭವನ್ನು ಆಚರಿಸುತ್ತಿದ್ದೇವೆ? ಹೆಸರು ಕಳುಹಿಸಿ:*",
        "ask_wish": "📝 *ಒಳ್ಳೆಯ ಸಂದೇಶವನ್ನು ಬರೆಯಿರಿ:*",
        "ask_dob_type": "⏳ *ವಯಸ್ಸಿನ ವಿವರಗಳನ್ನು ಹೇಗೆ ಸೇರಿಸಲು ಬಯಸುತ್ತೀರಿ?*",
        "ask_dob_date": "📅 **YYYY-MM-DD** ಸ್ವರೂಪದಲ್ಲಿ ದಿನಾಂಕ ಕಳುಹಿಸಿ:",
        "ask_dob_direct": "🔢 ನೇರ ವಯಸ್ಸನ್ನು ಸಂಖ್ಯೆಯಲ್ಲಿ ನಮೂದಿಸಿ:",
        "ask_year": "📅 *ವರ್ಷವನ್ನು ಆಯ್ಕೆಮಾಡಿ:*",
        "ask_month": "📆 *ತಿಂಗಳನ್ನು ಆಯ್ಕೆಮಾಡಿ:*",
        "ask_day": "🗓️ *ದಿನಾಂಕವನ್ನು ಆಯ್ಕೆಮಾಡಿ:*",
        "ask_hour": "⏰ *ಗಂಟೆಯನ್ನು ಆಯ್ಕೆಮಾಡಿ (00 ರಿಂದ 23):*",
        "ask_minute": "⏱️ *ನಿಮಿಷವನ್ನು ಆಯ್ಕೆಮಾಡಿ (00 ರಿಂದ 59):*",
        "ask_photo": "📸 *ಫೋಟೋ ಕಳುಹಿಸಿ* (ಅಥವಾ ಬಿಟ್ಟುಬಿಡಿ):",
        "ask_video": "🎥 *ವೀಡಿಯೊ ಕಳುಹಿಸಿ* (ಅಥವಾ ಬಿಟ್ಟುಬಿಡಿ):",
        "ask_song": "🎶 *ಹಾಡು ಕಳುಹಿಸಿ* (ಅಥವಾ ಬಿಟ್ಟುಬಿಡಿ):",
        "ask_voice": "🎙️ *ಧ್ವನಿ ಸಂದೇಶ ಕಳುಹಿಸಿ* (ಅಥವಾ ಬಿಟ್ಟುಬಿಡಿ):",
        "ask_audio": "🎵 *ಮತ್ತೊಂದು ಆಡಿಯೋ ಸೇರಿಸಿ* (ಅಥವಾ ಬಿಟ್ಟುಬಿಡಿ):",
        "ready": "✨ *{name} ಗಾಗಿ ಎಲ್ಲವೂ ಸಿದ್ಧವಾಗಿದೆ!*",
    },
    "bn": {
        "welcome": "✨ *سرپرائز کی دنیا میں خوش آمدید...*",
        "region_selected": "🌍 অঞ্চল: *{region}*. আপনার দেশ নির্বাচন করুন:",
        "country_choice": "🗣️ *{country}* এর জন্য ভাষা বেছে নিন:",
        "lang_updated": "✅ ভাষা সফলভাবে আপডেট করা হয়েছে!",
        "ask_category": "🎉 *এটি কি ধরণের উদযাপন?*",
        "ask_name": "✨ *আজ কার বিশেষ দিন? নাম পাঠান:*",
        "ask_wish": "📝 *একটি সুন্দর বার্তা লিখুন:*",
        "ask_dob_type": "⏳ *বয়সের বিবরণ কীভাবে যোগ করতে চান?*",
        "ask_dob_date": "📅 **YYYY-MM-DD** ফরম্যাটে তারিখ পাঠান:",
        "ask_dob_direct": "🔢 সরাসরি বয়স সংখ্যায় লিখুন:",
        "ask_year": "📅 *বছর নির্বাচন করুন:*",
        "ask_month": "📆 *মাস নির্বাচন করুন:*",
        "ask_day": "🗓️ *তারিখ নির্বাচন করুন:*",
        "ask_hour": "⏰ *ঘণ্টা নির্বাচন করুন (00 থেকে 23):*",
        "ask_minute": "⏱️ *মিনিট নির্বাচন করুন (00 থেকে 59):*",
        "ask_photo": "📸 *ছবি শেয়ার করুন* (বাদ দিন):",
        "ask_video": "🎥 *ভিডিও শেয়ার করুন* (বাদ দিন):",
        "ask_song": "🎶 *গান পাঠান* (বাদ দিন):",
        "ask_voice": "🎙️ *ভয়েস নোট পাঠান* (বাদ দিন):",
        "ask_audio": "🎵 *আরেকটি অডিও যোগ করুন* (বাদ দিন):",
        "ready": "✨ *{name} এর জন্য সবকিছু প্রস্তুত!*",
    },
    "ja": {
        "welcome": "✨ *サプライズの世界へようこそ...*",
        "region_selected": "🌍 地域: *{region}*. 国を選択してください:",
        "country_choice": "🗣️ *{country}* の言語を選択してください:",
        "lang_updated": "✅ 言語設定が更新されました！",
        "ask_category": "🎉 *どんなお祝いですか？*",
        "ask_name": "✨ *今日は誰のお祝いですか？名前を送信してください:*",
        "ask_wish": "📝 *メッセージを入力してください:*",
        "ask_dob_type": "⏳ *年齢の詳細を追加する方法を選択してください:*",
        "ask_dob_date": "📅 **YYYY-MM-DD** 形式で日付送信:",
        "ask_dob_direct": "🔢 年齢を数字で入力:",
        "ask_year": "📅 *年を選択:*",
        "ask_month": "📆 *月を選択:*",
        "ask_day": "🗓️ *日付を選択:*",
        "ask_hour": "⏰ *時間を選択 (00〜23):*",
        "ask_minute": "⏱️ *分を選択 (00〜59):*",
        "ask_photo": "📸 *写真を共有* (スキップ可):",
        "ask_video": "🎥 *動画を共有* (スキップ可):",
        "ask_song": "🎶 *曲を送信* (スキップ可):",
        "ask_voice": "🎙️ *ボイスメッセージを送信* (スキップ可):",
        "ask_audio": "🎵 *音声ファイルを追加* (スキップ可):",
        "ready": "✨ *{name} の準備ができました！*",
    },
    "ko": {
        "welcome": "✨ *서프라이즈의 세계에 오신 것을 환영합니다...*",
        "region_selected": "🌍 지역: *{region}*. 국가를 선택하세요:",
        "country_choice": "🗣️ *{country}* 언어를 선택하세요:",
        "lang_updated": "✅ 언어 설정이 업데이트되었습니다!",
        "ask_category": "🎉 *어떤 축하 행사인가요?*",
        "ask_name": "✨ *오늘 누구를 축하하나요? 이름을 입력하세요:*",
        "ask_wish": "📝 *따뜻한 메시지를 작성하세요:*",
        "ask_dob_type": "⏳ *나이 세부 정보를 어떻게 추가하시겠습니까?*",
        "ask_dob_date": "📅 **YYYY-MM-DD** 형식으로 날짜 입력:",
        "ask_dob_direct": "🔢 나이를 숫자로 입력:",
        "ask_year": "📅 *연도 선택:*",
        "ask_month": "📆 *월 선택:*",
        "ask_day": "🗓️ *일 선택:*",
        "ask_hour": "⏰ *시간 선택 (00~23):*",
        "ask_minute": "⏱️ *분 선택 (00~59):*",
        "ask_photo": "📸 *사진 공유* (건너뛰기 가능):",
        "ask_video": "🎥 *동영상 공유* (건너뛰기 가능):",
        "ask_song": "🎶 *노래 보내기* (건너뛰기 가능):",
        "ask_voice": "🎙️ *음성 메시지 보내기* (건너뛰기 가능):",
        "ask_audio": "🎵 *오디오 추가* (건너뛰기 가능):",
        "ready": "✨ *{name}님을 위한 준비가 완료되었습니다!*",
    },
    "az": {
        "welcome": "✨ *Sürprizlər dünyasına xoş gəlmisiniz...*",
        "region_selected": "🌍 Bölgə: *{region}*. Ölkənizi seçin:",
        "country_choice": "🗣️ *{country}* üçün dil seçin:",
        "lang_updated": "✅ Dil uğurla yeniləndi!",
        "ask_category": "🎉 *Bu nə cür bayramdır?*",
        "ask_name": "✨ *Bu gün kimin xüsusi gününü qeyd edirik? Adını göndərin:*",
        "ask_wish": "📝 *Gözəl bir arzu yazın:*",
        "ask_dob_type": "⏳ *Yaş detallarını necə əlavə etmək istəyirsiniz?*",
        "ask_dob_date": "📅 **YYYY-MM-DD** formatında tarix göndərin:",
        "ask_dob_direct": "🔢 Yaşı bir rəqəm olaraq daxil edin:",
        "ask_year": "📅 *İli seçin:*",
        "ask_month": "📆 *Ayı seçin:*",
        "ask_day": "🗓️ *Günü seçin:*",
        "ask_hour": "⏰ *Saat seçin (00 - 23):*",
        "ask_minute": "⏱️ *Dəqiqə seçin (00 - 59):*",
        "ask_photo": "📸 *Şəkil paylaşın* (və ya keçin):",
        "ask_video": "🎥 *Video paylaşın* (və ya keçin):",
        "ask_song": "🎶 *Mahnı göndərin* (və ya keçin):",
        "ask_voice": "🎙️ *Səs yazısı göndərin* (və ya keçin):",
        "ask_audio": "🎵 *Başqa bir səs faylı əlavə edin* (və ya keçin):",
        "ready": "✨ *{name} üçün hər şey hazırdır!*",
    },
    "hy": {
        "welcome": "✨ *Բարի գալուստ անակնկալների աշխարհ...*",
        "region_selected": "🌍 Տարածաշրջան՝ *{region}*. Ընտրեք ձեր երկիրը:",
        "country_choice": "🗣️ Ընտրեք լեզուն *{country}*-ի համար:",
        "lang_updated": "✅ Լեզուն հաջողությամբ թարմացվեց:",
        "ask_category": "🎉 *Ինչ տեսակի տոն է սա:*",
        "ask_name": "✨ *Ում հատուկ օրն ենք այսօր նշում: Ուղարկեք նրա անունը:*",
        "ask_wish": "📝 *Գրեք ջերմ մաղթանք:*",
        "ask_dob_type": "⏳ *Ինչպես՞ կցանկանաք ավելացնել տարիքի տվյալները:*",
        "ask_dob_date": "📅 Ուղարկեք ամսաթիվը **YYYY-MM-DD** ձևաչափով:",
        "ask_dob_direct": "🔢 Մուտքագրեք ուղղակի տարիքը թիվով:",
        "ask_year": "📅 *Ընտրեք տարին:*",
        "ask_month": "📆 *Ընտրեք ամիսը:*",
        "ask_day": "🗓️ *Ընտրեք օրը:*",
        "ask_hour": "⏰ *Ընտրեք ժամը (00-ից 23):*",
        "ask_minute": "⏱️ *Ընտրեք րոպեն (00-ից 59):*",
        "ask_photo": "📸 *Կիսվեք լուսանկարով* (կամ բաց թողնել):",
        "ask_video": "🎥 *Կիսվեք տեսանյութով* (կամ բաց թողնել):",
        "ask_song": "🎶 *Ուղարկեք երգ* (կամ բաց թողնել):",
        "ask_voice": "🎙️ *Ուղարկեք ձայնային հաղորդագրություն* (կամ բաց թողնել):",
        "ask_audio": "🎵 *Ավելացրեք ևս մեկ աուդիո* (կամ բաց թողնել):",
        "ready": "✨ *Ամեն ինչ պատրաստ է {name}-ի համար:*",
    },
    "ru": {
        "welcome": "✨ *Добро пожаловать в мир сюрпризов...*",
        "region_selected": "🌍 Регион: *{region}*. Выберите страну:",
        "country_choice": "🗣️ Выберите язык для *{country}*:",
        "lang_updated": "✅ Язык успешно обновлен!",
        "ask_category": "🎉 *Какой это праздник?*",
        "ask_name": "✨ *Чей праздник мы сегодня отмечаем? Введите имя:*",
        "ask_wish": "📝 *Напишите теплое пожелание:*",
        "ask_dob_type": "⏳ *Как вы хотите указать возраст для статистики?*",
        "ask_dob_date": "📅 Отправьте дату в формате **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Введите возраст цифрой:",
        "ask_year": "📅 *Выберите год:*",
        "ask_month": "📆 *Выберите месяц:*",
        "ask_day": "🗓️ *Выберите день:*",
        "ask_hour": "⏰ *Выберите час (от 00 до 23):*",
        "ask_minute": "⏱️ *Выберите минуту (от 00 до 59):*",
        "ask_photo": "📸 *Загрузите фото* (или пропустить):",
        "ask_video": "🎥 *Загрузите видео* (или пропустить):",
        "ask_song": "🎶 *Отправьте песню* (или пропустить):",
        "ask_voice": "🎙️ *Отправьте голосовое сообщение* (или пропустить):",
        "ask_audio": "🎵 *Добавьте еще аудио* (или пропустить):",
        "ready": "✨ *Все готово для {name}!*",
    },
    "id": {
        "welcome": "✨ *Selamat datang di dunia kejutan...*",
        "region_selected": "🌍 Wilayah: *{region}*. Pilih negara Anda:",
        "country_choice": "🗣️ Pilih bahasa Anda untuk *{country}*:",
        "lang_updated": "✅ Bahasa berhasil diperbarui!",
        "ask_category": "🎉 *Perayaan apa ini?*",
        "ask_name": "✨ *Siapa yang merayakan hari spesial hari ini? Kirim namanya:*",
        "ask_wish": "📝 *Tulis pesan ucapan yang manis:*",
        "ask_dob_type": "⏳ *Bagaimana Anda ingin menambahkan detail usia?*",
        "ask_dob_date": "📅 Kirim tanggal dalam format **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Masukkan usia langsung sebagai angka:",
        "ask_year": "📅 *Pilih tahun:*",
        "ask_month": "📆 *Pilih bulan:*",
        "ask_day": "🗓️ *Pilih hari:*",
        "ask_hour": "⏰ *Pilih Jam (00 sampai 23):*",
        "ask_minute": "⏱️ *Pilih Menit (00 sampai 59):*",
        "ask_photo": "📸 *Bagikan foto* (atau lewati):",
        "ask_video": "🎥 *Bagikan video* (atau lewati):",
        "ask_song": "🎶 *Kirim lagu* (atau lewati):",
        "ask_voice": "🎙️ *Kirim pesan suara* (atau lewati):",
        "ask_audio": "🎵 *Tambahkan audio lain* (atau lewati):",
        "ready": "✨ *Semuanya siap untuk {name}!*",
    },
    "tr": {
        "welcome": "✨ *Sürprizler dünyasına hoş geldiniz...*",
        "region_selected": "🌍 Bölge: *{region}*. Ülkenizi seçin:",
        "country_choice": "🗣️ *{country}* için dilinizi seçin:",
        "lang_updated": "✅ Dil başarıyla güncellendi!",
        "ask_category": "🎉 *Bu ne tür bir kutlama?*",
        "ask_name": "✨ *Bugün kimin özel gününü kutluyoruz? Adını gönderin:*",
        "ask_wish": "📝 *Tatlı bir dilek yazın:*",
        "ask_dob_type": "⏳ *Yaş bilgilerini nasıl eklemekistersiniz?*",
        "ask_dob_date": "📅 **YYYY-MM-DD** formatında tarih gönderin:",
        "ask_dob_direct": "🔢 Yaşı sayı olarak girin:",
        "ask_year": "📅 *Yılı seçin:*",
        "ask_month": "📆 *Ayı seçin:*",
        "ask_day": "🗓️ *Günü seçin:*",
        "ask_hour": "⏰ *Saati seçin (00 - 23):*",
        "ask_minute": "⏱️ *Dakikayı seçin (00 - 59):*",
        "ask_photo": "📸 *Bir fotoğraf paylaşın* (veya atlayın):",
        "ask_video": "🎥 *Bir video paylaşın* (veya atlayın):",
        "ask_song": "🎶 *Bir şarkı gönderin* (veya atlayın):",
        "ask_voice": "🎙️ *Sesli not gönderin* (veya atlayın):",
        "ask_audio": "🎵 *Başka bir ses dosyası ekleyin* (veya atlayın):",
        "ready": "✨ *{name} için her şey hazır!*",
    },
    "ar": {
        "welcome": "✨ *مرحباً بك في عالم المفاجآت...*",
        "region_selected": "🌍 المنطقة: *{region}*. اختر دولتك:",
        "country_choice": "🗣️ اختر لغتك لـ *{country}*:",
        "lang_updated": "✅ تم تحديث اللغة بنجاح!",
        "ask_category": "🎉 *ما هي المناسبة؟*",
        "ask_name": "✨ *من هو صاحب المناسبة اليوم؟ أرسل اسمه:*",
        "ask_wish": "📝 *اكتب رسالة جميلة:*",
        "ask_dob_type": "⏳ *كيف تريد إضافة تفاصيل العمر للإحصائيات؟*",
        "ask_dob_date": "📅 أرسل التاريخ بالصيغة **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 أدخل العمر المباشر برقم:",
        "ask_year": "📅 *اختر السنة:*",
        "ask_month": "📆 *اختر الشهر:*",
        "ask_day": "🗓️ *اختر اليوم:*",
        "ask_hour": "⏰ *اختر الساعة (00 إلى 23):*",
        "ask_minute": "⏱️ *اختر الدقيقة (00 إلى 59):*",
        "ask_photo": "📸 *شارك صورة* (أو تخطي):",
        "ask_video": "🎥 *شارك فيديو* (أو تخطي):",
        "ask_song": "🎶 *أرسل أغنية* (أو تخطي):",
        "ask_voice": "🎙️ *أرسل رسالة صوتية* (أو تخطي):",
        "ask_audio": "🎵 *أضف ملف صوتي آخر* (أو تخطي):",
        "ready": "✨ *كل شيء جاهز لـ {name}!*",
    },
    "ms": {
        "welcome": "✨ *Selamat datang ke dunia kejutan...*",
        "region_selected": "🌍 Wilayah: *{region}*. Pilih negara anda:",
        "country_choice": "🗣️ Pilih bahasa anda untuk *{country}*:",
        "lang_updated": "✅ Bahasa berjaya dikemas kini!",
        "ask_category": "🎉 *Apakah jenis perayaan ini?*",
        "ask_name": "✨ *Siapa yang kita sambut hari ini? Hantar nama mereka:*",
        "ask_wish": "📝 *Tulis ucapan yang manis:*",
        "ask_dob_type": "⏳ *Bagaimana anda ingin menambah butiran umur?*",
        "ask_dob_date": "📅 Hantar tarikh dalam format **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Masukkan umur sebagai nombor:",
        "ask_year": "📅 *Pilih tahun:*",
        "ask_month": "📆 *Pilih bulan:*",
        "ask_day": "🗓️ *Pilih hari:*",
        "ask_hour": "⏰ *Pilih Jam (00 hingga 23):*",
        "ask_minute": "⏱️ *Pilih Minit (00 hingga 59):*",
        "ask_photo": "📸 *Kongsi foto* (atau langkau):",
        "ask_video": "🎥 *Kongsi video* (atau langkau):",
        "ask_song": "🎶 *Hantar lagu* (atau langkau):",
        "ask_voice": "🎙️ *Hantar nota suara* (atau langkau):",
        "ask_audio": "🎵 *Tambah fail audio lain* (atau langkau):",
        "ready": "✨ *Semuanya bersedia untuk {name}!*",
    },
    "zh": {
        "welcome": "✨ *欢迎来到惊喜世界...*",
        "region_selected": "🌍 地区：*{region}*。请选择您的国家：",
        "country_choice": "🗣️ 请为 *{country}* 选择您的语言：",
        "lang_updated": "✅ 语言设置已成功更新！",
        "ask_category": "🎉 *这是什么类型的庆祝活动？*",
        "ask_name": "✨ *今天我们要庆祝谁的节日？发送名字：*",
        "ask_wish": "📝 *写一条祝福消息：*",
        "ask_dob_type": "⏳ *您想如何添加年龄统计信息？*",
        "ask_dob_date": "📅 请发送 **YYYY-MM-DD** 格式的日期：",
        "ask_dob_direct": "🔢 请以数字形式输入年龄：",
        "ask_year": "📅 *选择年份：*",
        "ask_month": "📆 *选择月份：*",
        "ask_day": "🗓️ *选择日期：*",
        "ask_hour": "⏰ *选择小时 (00至23)：*",
        "ask_minute": "⏱️ *选择分钟 (00至59)：*",
        "ask_photo": "📸 *分享照片*（可跳过）：",
        "ask_video": "🎥 *分享视频*（可跳过）：",
        "ask_song": "🎶 *发送歌曲*（可跳过）：",
        "ask_voice": "🎙️ *发送语音*（可跳过）：",
        "ask_audio": "🎵 *添加音频*（可跳过）：",
        "ready": "✨ *一切为 {name} 准备就绪！*",
    },
    "ta": {
        "welcome": "✨ *ஆச்சரியங்கள் நிறைந்த உலகத்திற்கு உங்களை வரவேற்கிறோம்...*",
        "region_selected": "🌍 பிராந்தியம்: *{region}*. உங்கள் நாட்டைத் தேர்ந்தெடுக்கவும்:",
        "country_choice": "🗣️ *{country}*-க்கான மொழியைத் தேர்ந்தெடுக்கவும்:",
        "lang_updated": "✅ மொழி வெற்றிகரமாக மாற்றப்பட்டது!",
        "ask_category": "🎉 *இது என்ன வகையான விழா?*",
        "ask_name": "✨ *இன்று யாருடைய சிறப்பு நிகழ்வைக் கொண்டாடுகிறோம்? பெயர் அனுப்பவும்:*",
        "ask_wish": "📝 *ஒரு இனிய வாழ்த்துச் செய்தியை எழுதவும்:*",
        "ask_dob_type": "⏳ *வயது விவரங்களை எவ்வாறு சேர்க்க விரும்புகிறீர்கள்?*",
        "ask_dob_date": "📅 **YYYY-MM-DD** வடிவத்தில் தேதியை அனுப்பவும்:",
        "ask_dob_direct": "🔢 நேரடி வயதை எண்ணாக உள்ளிடவும்:",
        "ask_year": "📅 *ஆண்டைத் தேர்ந்தெடுக்கவும்:*",
        "ask_month": "📆 *மாதத்தைத் தேர்ந்தெடுக்கவும்:*",
        "ask_day": "🗓️ *தேதியைத் தேர்ந்தெடுக்கவும்:*",
        "ask_hour": "⏰ *மணிநேரத்தைத் தேர்ந்தெடுக்கவும் (00 முதல் 23):*",
        "ask_minute": "⏱️ *நிமிடத்தைத் தேர்ந்தெடுக்கவும் (00 முதல் 59):*",
        "ask_photo": "📸 *புகைப்படத்தைப் பகிரவும்* (தவிர்க்கலாம்):",
        "ask_video": "🎥 *வீடியோவைப் பகிரவும்* (தவிர்க்கலாம்):",
        "ask_song": "🎶 *பாட்டை அனுப்பவும்* (தவிர்க்கலாம்):",
        "ask_voice": "🎙️ *குரல் பதிவை அனுப்பவும்* (தவிர்க்கலாம்):",
        "ask_audio": "🎵 *மற்றொரு ஆடியோ கோப்பைச் சேர்க்கவும்* (தவிர்க்கலாம்):",
        "ready": "✨ *{name}-க்கான அனைத்து ஏற்பாடுகளும் தயார்!*",
    },
    "uz": {
        "welcome": "✨ *Kutilmagan sovg'alar olamiga xush kelibsiz...*",
        "region_selected": "🌍 Hudud: *{region}*. O'z mamlakatingizni tanlang:",
        "country_choice": "🗣️ *{country}* uchun tilingizni tanlang:",
        "lang_updated": "✅ Til muvaffaqiyatli yangilandi!",
        "ask_category": "🎉 *Bu qanday bayram?*",
        "ask_name": "✨ *Bugun kimning bayramini nishonlayapmiz? Ismini yuboring:*",
        "ask_wish": "📝 *Chiroyli tilak yozing:*",
        "ask_dob_type": "⏳ *Yosh ma'lumotlarini qanday qo'shishni xohlaysiz?*",
        "ask_dob_date": "📅 Sana **YYYY-MM-DD** formatida yuboring:",
        "ask_dob_direct": "🔢 To'g'ridan-to'g'ri yoshni raqam bilan kiriting:",
        "ask_year": "📅 *Yilni tanlang:*",
        "ask_month": "📆 *Oyni tanlang:*",
        "ask_day": "🗓️ *Kunni tanlang:*",
        "ask_hour": "⏰ *Soatni tanlang (00 dan 23 gacha):*",
        "ask_minute": "⏱️ *Dqiqani tanlang (00 dan 59 gacha):*",
        "ask_photo": "📸 *Rasm ulashing* (yoki o'tkazib yuboring):",
        "ask_video": "🎥 *Video ulashing* (yoki o'tkazib yuboring):",
        "ask_song": "🎶 *Qo'shiq yuboring* (yoki o'tkazib yuboring):",
        "ask_voice": "🎙️ *Ovozli xabar yuboring* (yoki o'tkazib yuboring):",
        "ask_audio": "🎵 *Boshqa audio qo'shing* (yoki o'tkazib yuboring):",
        "ready": "✨ *{name} uchun hamma narsa tayyor!*",
    },
    "tg": {
        "welcome": "✨ *به دنیای شگفتی‌ها خوش آمدید...*",
        "region_selected": "🌍 منطقه: *{region}*. کشور خود را انتخاب کنید:",
        "country_choice": "🗣️ زبان خود را برای *{country}* انتخاب کنید:",
        "lang_updated": "✅ زبان با موفقیت به‌روز شد!",
        "ask_category": "🎉 *این چه نوع جشنی است؟*",
        "ask_name": "🎉 *امروز مناسبت چه کسی است؟ نام را بفرستید:*",
        "ask_wish": "📝 *یک پیام زیبا بنویسید:*",
        "ask_dob_type": "⏳ *چگونه می‌خواهید جزئیات سن را اضافه کنید؟*",
        "ask_dob_date": "📅 تاریخ را با فرمت **YYYY-MM-DD** بفرستید:",
        "ask_dob_direct": "🔢 سن مستقیم را به صورت عدد وارد کنید:",
        "ask_year": "📅 *سال را انتخاب کنید:*",
        "ask_month": "📆 *ماه را انتخاب کنید:*",
        "ask_day": "🗓️ *روز را انتخاب کنید:*",
        "ask_hour": "⏰ *ساعت را انتخاب کنید (00 تا 23):*",
        "ask_minute": "⏱️ *دقیقه را انتخاب کنید (00 تا 59):*",
        "ask_photo": "📸 *اشتراک‌گذاری عکس* (یا رد کردن):",
        "ask_video": "🎥 *اشتراک‌گذاری ویدیو* (یا رد کردن):",
        "ask_song": "🎶 *ارسال آهنگ* (یا رد کردن):",
        "ask_voice": "🎙️ *ارسال یادداشت صوتی* (یا رد کردن):",
        "ask_audio": "🎵 *افزودن صوتی دیگر* (یا رد کردن):",
        "ready": "✨ *همه چیز برای {name} آماده است!*",
    },
    "fa": {
        "welcome": "✨ *به دنیای شگفتی‌ها خوش آمدید...*",
        "region_selected": "🌍 منطقه: *{region}*. کشور خود را انتخاب کنید:",
        "country_choice": "🗣️ زبان خود را برای *{country}* انتخاب کنید:",
        "lang_updated": "✅ زبان با موفقیت به‌روز شد!",
        "ask_category": "🎉 *این چه نوع جشنی است؟*",
        "ask_name": "✨ *امروز مناسبت چه کسی است؟ نام او را بفرستید:*",
        "ask_wish": "📝 *یک پیام صمیمانه بنویسید:*",
        "ask_dob_type": "⏳ *چگونه می‌خواهید جزئیات سن را اضافه کنید؟*",
        "ask_dob_date": "📅 تاریخ را با فرمت **YYYY-MM-DD** بفرستید:",
        "ask_dob_direct": "🔢 سن را به عنوان عدد وارد کنید:",
        "ask_year": "📅 *سال را انتخاب کنید:*",
        "ask_month": "📆 *ماه را انتخاب کنید:*",
        "ask_day": "🗓️ *روز را انتخاب کنید:*",
        "ask_hour": "⏰ *ساعت را انتخاب کنید (00 تا 23):*",
        "ask_minute": "⏱️ *دقیقه را انتخاب کنید (00 تا 59):*",
        "ask_photo": "📸 *اشتراک‌گذاری عکس* (یا رد کردن):",
        "ask_video": "🎥 *اشتراک‌گذاری ویدیو* (یا رد کردن):",
        "ask_song": "🎶 *ارسال آهنگ* (یا رد کردن):",
        "ask_voice": "🎙️ *ارسال ویس* (یا رد کردن):",
        "ask_audio": "🎵 *افزودن فایل صوتی دیگر* (یا رد کردن):",
        "ready": "✨ *همه چیز برای {name} آماده است!*",
    },
    "my": {
        "welcome": "✨ *အံ့သြဖွယ်ရာ ကမ္ဘာလေးမှ ကြိုဆိုပါတယ်...*",
        "region_selected": "🌍 ဒေသ: *{region}*. သင်၏နိုင်ငံကို ရွေးပါ:",
        "country_choice": "🗣️ *{country}* အတွက် ဘာသာစကားကို ရွေးပါ:",
        "lang_updated": "✅ ဘာသာစကား အောင်မြင်စွာ ပြောင်းလဲပြီးပါပြီ။",
        "ask_category": "🎉 *ဘာပွဲကျင်းပတာလဲ?*",
        "ask_name": "✨ *ဒီနေ့ ဘယ်သူ့ရဲ့ အထူးနေ့လဲ? နာမည်ပို့ပေးပါ:*",
        "ask_wish": "📝 *ဆုတောင်းစကား ရေးပေးပါ:*",
        "ask_dob_type": "⏳ *အသက်အချက်အလက်ကို ဘယ်လိုထည့်ချင်ပါလဲ?*",
        "ask_dob_date": "📅 ရက်စွဲကို **YYYY-MM-DD** ပုံစံဖြင့် ပို့ပါ:",
        "ask_dob_direct": "🔢 အသက်ကို နံပါတ်ဖြင့် ရိုက်ထည့်ပါ:",
        "ask_year": "📅 *နှစ်ကို ရွေးပါ:*",
        "ask_month": "📆 *လကို ရွေးပါ:*",
        "ask_day": "🗓️ *ရက်ကို ရွေးပါ:*",
        "ask_hour": "⏰ *နာရီကို ရွေးပါ (00 မှ 23):*",
        "ask_minute": "⏱️ *မိနစ်ကို ရွေးပါ (00 မှ 59):*",
        "ask_photo": "📸 *ဓာတ်ပုံမျှဝေပါ* (သို့) ကျော်ရန်:",
        "ask_video": "🎥 *ဗီဒီယိုမျှဝေပါ* (သို့) ကျော်ရန်:",
        "ask_song": "🎶 *သီချင်းပို့ပါ* (သို့) ကျော်ရန်:",
        "ask_voice": "🎙️ *အသံဖိုင်ပို့ပါ* (သို့) ကျော်ရန်:",
        "ask_audio": "🎵 *အခြားအသံဖိုင် ထပ်ထည့်ပါ* (သို့) ကျော်ရန်:",
        "ready": "✨ *{name} အတွက် အားလုံးအဆင်သင့်ဖြစ်ပါပြီ!*",
    },
    "vi": {
        "welcome": "✨ *Chào mừng bạn đến với thế giới bất ngờ...*",
        "region_selected": "🌍 Khu vực: *{region}*. Chọn quốc gia của bạn:",
        "country_choice": "🗣️ Chọn ngôn ngữ cho *{country}*:",
        "lang_updated": "✅ Đã cập nhật ngôn ngữ thành công!",
        "ask_category": "🎉 *Đây là lễ kỷ niệm gì?*",
        "ask_name": "✨ *Hôm nay chúng ta mừng dịp đặc biệt của ai? Gửi tên:*",
        "ask_wish": "📝 *Viết một lời chúc ngọt ngào:*",
        "ask_dob_type": "⏳ *Bạn muốn thêm chi tiết tuổi như thế nào?*",
        "ask_dob_date": "📅 Gửi ngày theo định dạng **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Nhập tuổi trực tiếp dưới dạng số:",
        "ask_year": "📅 *Chọn năm:*",
        "ask_month": "📆 *Chọn tháng:*",
        "ask_day": "🗓️ *Chọn ngày:*",
        "ask_hour": "⏰ *Chọn Giờ (00 đến 23):*",
        "ask_minute": "⏱️ *Chọn Phút (00 đến 59):*",
        "ask_photo": "📸 *Chia sẻ ảnh* (hoặc bỏ qua):",
        "ask_video": "🎥 *Chia sẻ video* (hoặc bỏ qua):",
        "ask_song": "🎶 *Gửi bài hát* (hoặc bỏ qua):",
        "ask_voice": "🎙️ *Gửi tin nhắn thoại* (hoặc bỏ qua):",
        "ask_audio": "🎵 *Thêm tệp âm thanh khác* (hoặc bỏ qua):",
        "ready": "✨ *Mọi thứ đã sẵn sàng cho {name}!*",
    },
    "fil": {
        "welcome": "✨ *Maligayang pagdating sa mundo ng mga sorpresa...*",
        "region_selected": "🌍 Rehiyon: *{region}*. Piliin ang iyong bansa:",
        "country_choice": "🗣️ Piliin ang iyong wika para sa *{country}*:",
        "lang_updated": "✅ Matagumpay na na-update ang wika!",
        "ask_category": "🎉 *Anong klaseng pagdiriwang ito?*",
        "ask_name": "✨ *Kanino tayo magdiriwang ngayon? Ipadala ang pangalan:*",
        "ask_wish": "📝 *Sumulat ng magandang mensahe:*",
        "ask_dob_type": "⏳ *Paano mo gustong idagdag ang detalye ng edad?*",
        "ask_dob_date": "📅 Magpadala ng petsa sa format na **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Ilagay ang edad bilang numero:",
        "ask_year": "📅 *Piliin ang taon:*",
        "ask_month": "📆 *Piliin ang buwan:*",
        "ask_day": "🗓️ *Piliin ang araw:*",
        "ask_hour": "⏰ *Piliin ang Oras (00 hanggang 23):*",
        "ask_minute": "⏱️ *Piliin ang Minuto (00 hanggang 59):*",
        "ask_photo": "📸 *Magbahagi ng larawan* (o laktawan):",
        "ask_video": "🎥 *Magbahagi ng video* (o laktawan):",
        "ask_song": "🎶 *Magpadala ng kanta* (o laktawan):",
        "ask_voice": "🎙️ *Magpadala ng voice note* (o laktawan):",
        "ask_audio": "🎵 *Magdagdag ng isa pang audio* (o laktawan):",
        "ready": "✨ *Handa na ang lahat para kay {name}!*",
    },
    "be": {
        "welcome": "✨ *Сардэчна запрашаем у свет сюрпрызаў...*",
        "region_selected": "🌍 Рэгіён: *{region}*. Выберыце краіну:",
        "country_choice": "🗣️ Выберыце мову для *{country}*:",
        "lang_updated": "✅ Мова паспяхова абноўлена!",
        "ask_category": "🎉 *Якое гэта свята?*",
        "ask_name": "✨ *Чыё свята мы сёння святкуем? Увядзіце імя:*",
        "ask_wish": "📝 *Напишыце цёплае пажаданне:*",
        "ask_dob_type": "⏳ *Як вы хочаце дадаць дэталі ўзросту?*",
        "ask_dob_date": "📅 Адпраўце дату ў фармаце **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Увядзіце ўзрост лічбай:",
        "ask_year": "📅 *Выберыце год:*",
        "ask_month": "📆 *Выберыце месяц:*",
        "ask_day": "🗓️ *Выберыце дзень:*",
        "ask_hour": "⏰ *Выберыце гадзіну (ад 00 да 23):*",
        "ask_minute": "⏱️ *Выберыце хвіліну (ад 00 да 59):*",
        "ask_photo": "📸 *Падзяліцеся фота* (або прапусціць):",
        "ask_video": "🎥 *Падзяліцеся відэа* (або прапусціць):",
        "ask_song": "🎶 *Адпраўце песню* (або прапусціць):",
        "ask_voice": "🎙️ *Адпраўце галасавое паведамленне* (або прапусціць):",
        "ask_audio": "🎵 *Дадайце яшчэ аўдыё* (або прапусціць):",
        "ready": "✨ *Усё гатова для {name}!*",
    },
    "it": {
        "welcome": "✨ *Benvenuto nel tuo angolo di sorprese...*",
        "region_selected": "🌍 Regione: *{region}*. Seleziona il tuo paese:",
        "country_choice": "🗣️ Scegli la tua lingua per *{country}*:",
        "lang_updated": "✅ Lingua aggiornata con successo!",
        "ask_category": "🎉 *Che tipo di celebrazione è?*",
        "ask_name": "✨ *Di chi è l'occasione speciale che festeggiamo oggi? Invia il nome:*",
        "ask_wish": "📝 *Scrivi un messaggio affettuoso:*",
        "ask_dob_type": "⏳ *Come vorresti aggiungere i dettagli dell'età?*",
        "ask_dob_date": "📅 Invia la data nel formato **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Inserisci l'età direttamente come numero:",
        "ask_year": "📅 *Seleziona l'anno:*",
        "ask_month": "📆 *Seleziona il mese:*",
        "ask_day": "🗓️ *Seleziona il giorno:*",
        "ask_hour": "⏰ *Seleziona l'Ora (da 00 a 23):*",
        "ask_minute": "⏱️ *Seleziona il Minuto (da 00 a 59):*",
        "ask_photo": "📸 *Condividi una foto* (o salta):",
        "ask_video": "🎥 *Condividi un video* (o salta):",
        "ask_song": "🎶 *Invia una canzone* (o salta):",
        "ask_voice": "🎙️ *Invia un messaggio vocale* (o salta):",
        "ask_audio": "🎵 *Aggiungi un altro audio* (o salta):",
        "ready": "✨ *Tutto pronto per {name}!*",
    },
    "de": {
        "welcome": "✨ *Willkommen in Ihrer kleinen Welt der Überraschungen...*",
        "region_selected": "🌍 Region: *{region}*. Wählen Sie Ihr Land:",
        "country_choice": "🗣️ Wählen Sie Ihre Sprache für *{country}*:",
        "lang_updated": "✅ Spracheinstellung erfolgreich aktualisiert!",
        "ask_category": "🎉 *Welche Art von Feier ist das?*",
        "ask_name": "✨ *Wessen besonderen Anlass feiern wir heute? Name senden:*",
        "ask_wish": "📝 *Schreiben Sie eine liebevolle Nachricht:*",
        "ask_dob_type": "⏳ *Wie möchten Sie Altersdetails hinzufügen?*",
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
        "ready": "✨ *Alles bereit für {name}!*",
    },
    "es": {
        "welcome": "✨ *Bienvenido a tu rincón de sorpresas...*",
        "region_selected": "🌍 Región: *{region}*. Selecciona tu país:",
        "country_choice": "🗣️ Elige tu idioma para *{country}*:",
        "lang_updated": "✅ ¡Preferencia de idioma actualizada!",
        "ask_category": "🎉 *¿Qué tipo de celebración es?*",
        "ask_name": "✨ *¿A quién celebramos hoy? Envía su nombre:*",
        "ask_wish": "📝 *Escribe un mensaje cariñoso:*",
        "ask_dob_type": "⏳ *¿Cómo te gustaría agregar los detalles de edad?*",
        "ask_dob_date": "📅 Envía la fecha en formato **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Ingresa la edad directamente como número:",
        "ask_year": "📅 *Selecciona el año:*",
        "ask_month": "📆 *Selecciona el mes:*",
        "ask_day": "🗓️ *Selecciona el día:*",
        "ask_hour": "⏰ *Selecciona la Hora (00 a 23):*",
        "ask_minute": "⏱️ *Selecciona el Minuto (00 a 59):*",
        "ask_photo": "📸 *Comparte una foto* (o saltar):",
        "ask_video": "🎥 *Comparte un video* (o saltar):",
        "ask_song": "🎶 *Envía una canción* (o saltar):",
        "ask_voice": "🎙️ *Envía una nota de voz* (o saltar):",
        "ask_audio": "🎵 *Añade otro audio* (o saltar):",
        "ready": "✨ *¡Todo listo para {name}!*",
    },
    "fr": {
        "welcome": "✨ *Bienvenue dans votre petit coin de surprises...*",
        "region_selected": "🌍 Région : *{region}*. Sélectionnez votre pays :",
        "country_choice": "🗣️ Choisissez votre langue pour *{country}* :",
        "lang_updated": "✅ Préférence de langue mise à jour !",
        "ask_category": "🎉 *Quel type de célébration est-ce ?*",
        "ask_name": "✨ *Quelle occasion spéciale célébrons-nous ? Nom :*",
        "ask_wish": "📝 *Écrivez un message chaleureux :*",
        "ask_dob_type": "⏳ *Comment souhaitez-vous ajouter les détails d'âge ?*",
        "ask_dob_date": "📅 Envoyez la date au format **YYYY-MM-DD** :",
        "ask_dob_direct": "🔢 Entrez l'âge directement sous forme de nombre :",
        "ask_year": "📅 *Sélectionnez l'année :*",
        "ask_month": "📆 *Sélectionnez le mois :*",
        "ask_day": "🗓️ *Sélectionnez le jour :*",
        "ask_hour": "⏰ *Sélectionnez l'heure (00 à 23) :*",
        "ask_minute": "⏱️ *Sélectionnez la minute (00 à 59) :*",
        "ask_photo": "📸 *Partagez une photo* (ou ignorer) :",
        "ask_video": "🎥 *Partagez une vidéo* (ou ignorer) :",
        "ask_song": "🎶 *Envoyez une chanson* (ou ignorer) :",
        "ask_voice": "🎙️ *Envoyez un message vocal* (ou ignorer) :",
        "ask_audio": "🎵 *Ajoutez un autre audio* (ou ignorer) :",
        "ready": "✨ *Tout est prêt pour {name} !*",
    },
    "uk": {
        "welcome": "✨ *Ласкаво просимо у світ сюрпризів...*",
        "region_selected": "🌍 Регіон: *{region}*. Виберіть свою країну:",
        "country_choice": "🗣️ Виберіть мову для *{country}*:",
        "lang_updated": "✅ Мову успішно оновлено!",
        "ask_category": "🎉 *Яке це свято?*",
        "ask_name": "✨ *Чиє свято мы сьогодні святкуємо? Введіть ім'я:*",
        "ask_wish": "📝 *Напишіть тепле побажання:*",
        "ask_dob_type": "⏳ *Як ви хочете додати дані про вік?*",
        "ask_dob_date": "📅 Надішліть дату у форматі **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Введіть вік числом:",
        "ask_year": "📅 *Виберіть рік:*",
        "ask_month": "📆 *Виберіть місяць:*",
        "ask_day": "🗓️ *Виберіть день:*",
        "ask_hour": "⏰ *Виберіть годину (від 00 до 23):*",
        "ask_minute": "⏱️ *Виберіть хвилину (від 00 до 59):*",
        "ask_photo": "📸 *Поділіться фото* (або пропустити):",
        "ask_video": "🎥 *Поділіться відео* (або пропустити):",
        "ask_song": "🎶 *Надішліть пісню* (або пропустити):",
        "ask_voice": "🎙️ *Надішліть голосове повідомлення* (або пропустити):",
        "ask_audio": "🎵 *Додайте ще аудіо* (або пропустити):",
        "ready": "✨ *Все готово для {name}!*",
    },
    "sw": {
        "welcome": "✨ *Karibu kwenye ulimwengu wa mshangao...*",
        "region_selected": "🌍 Eneo: *{region}*. Chagua nchi yako:",
        "country_choice": "🗣️ Chagua lugha yako kwa ajili ya *{country}*:",
        "lang_updated": "✅ Lugha imesasishwa kikamilifu!",
        "ask_category": "🎉 *Hii ni sherehe ya aina gani?*",
        "ask_name": "✨ *Tunasherehekea nani leo? Tuma jina lake:*",
        "ask_wish": "📝 *Andika ujumbe mtamu na wenye upendo:*",
        "ask_dob_type": "⏳ *Ungependa kuongeza vipi maelezo ya umri?*",
        "ask_dob_date": "📅 Tuma tarehe katika muundo wa **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Ingiza umri moja kwa moja kama namba:",
        "ask_year": "📅 *Chagua mwaka:*",
        "ask_month": "📆 *Chagua mwezi:*",
        "ask_day": "🗓️ *Chagua siku:*",
        "ask_hour": "⏰ *Chagua Saa (00 hadi 23):*",
        "ask_minute": "⏱️ *Chagua Dakika (00 hadi 59):*",
        "ask_photo": "📸 *Shiriki picha* (au ruka):",
        "ask_video": "🎥 *Shiriki video* (au ruka):",
        "ask_song": "🎶 *Tuma wimbo* (au ruka):",
        "ask_voice": "🎙️ *Tuma ujumbe wa sauti* (au ruka):",
        "ask_audio": "🎵 *Ongeza faili lingine la sauti* (au ruka):",
        "ready": "✨ *Kila kitu kiko tayari kwa ajili ya {name}!*",
    },
    "zu": {
        "welcome": "✨ *Uyemukelվել emhlabeni wezimanga...*",
        "region_selected": "🌍 Isifunda: *{region}*. Khetha izwe lakho:",
        "country_choice": "🗣️ Khetha ulimi lwakho lwe-*{country}*:",
        "lang_updated": "✅ Ulimi luvuselelwe ngempumelelo!",
        "ask_category": "🎉 *Lolu uhlobo luni lomkhosi?*",
        "ask_name": "✨ *Ubani esigubha usuku lwakhe namuhla? Thumela igama lakhe:*",
        "ask_wish": "📝 *Bhala umyalezo omuhle:*",
        "ask_dob_type": "⏳ *Ungathanda ukungeza kanjani imininingwane yobudala?*",
        "ask_dob_date": "📅 Thumela usuku ngefomethi **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Faka iminyaka ngqo njengonombolo:",
        "ask_year": "📅 *Khetha unyaka:*",
        "ask_month": "📆 *Khetha inyanga:*",
        "ask_day": "🗓️ *Khetha usuku:*",
        "ask_hour": "⏰ *Khetha iHora (00 kuya ku-23):*",
        "ask_minute": "⏱️ *Khetha iMizuzu (00 kuya ku-59):*",
        "ask_photo": "📸 *Yabelana ngesithombe* (noma yeqa):",
        "ask_video": "🎥 *Yabelana ngevidiyo* (noma yeqa):",
        "ask_song": "🎶 *Thumela ingoma* (noma yeqa):",
        "ask_voice": "🎙️ *Thumela umlayezo wezwi* (noma yeqa):",
        "ask_audio": "🎵 *Engeza elinye ifayela lomsindo* (noma yeqa):",
        "ready": "✨ *Konke sekulungele u-{name}!*",
    },
    "xh": {
        "welcome": "✨ *Wamkelekile kwihlabathi lezimanga...*",
        "region_selected": "🌍 Ummandla: *{region}*. Khetha ilizwe lakho:",
        "country_choice": "🗣️ Khetha ulwimi lwakho lwe-*{country}*:",
        "lang_updated": "✅ Ulwimi luhlaziywe ngempumelelo!",
        "ask_category": "🎉 *Lolu hlobo luni lombhiyozo?*",
        "ask_name": "✨ *Ngubani esimbhiyozelayo namhlanje? Thumela igama lakhe:*",
        "ask_wish": "📝 *Bhala umyalezo omnandi:*",
        "ask_dob_type": "⏳ *Ungathanda ukongeza njani iinkcukacha zeminyaka?*",
        "ask_dob_date": "📅 Thumela umhla ngefomathi **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Faka iminyaka ngqo njengonombolo:",
        "ask_year": "📅 *Khetha unyaka:*",
        "ask_month": "📆 *Khetha inyanga:*",
        "ask_day": "🗓️ *Khetha usuku:*",
        "ask_hour": "⏰ *Khetha iyure (00 ukuya ku-23):*",
        "ask_minute": "⏱️ *Khetha umzuzu (00 ukuya ku-59):*",
        "ask_photo": "📸 *Yabelana ngefoto* (okanye tsiba):",
        "ask_video": "🎥 *Yabelana ngevidiyo* (okanye tsiba):",
        "ask_song": "🎶 *Thumela ingoma* (okanye tsiba):",
        "ask_voice": "🎙️ *Thumela umyalezo welizwi* (okanye tsiba):",
        "ask_audio": "🎵 *Yongeza olunye uncedo lwesandi* (okanye tsiba):",
        "ready": "✨ *Konke kulungele u-{name}!*",
    },
    "af": {
        "welcome": "✨ *Welkom by jou klein wêreld van verrassings...*",
        "region_selected": "🌍 Streek: *{region}*. Kies jou land:",
        "country_choice": "🗣️ Kies jou taal vir *{country}*:",
        "lang_updated": "✅ Taal met sukses opgedateer!",
        "ask_category": "🎉 *Watter tipe viering is dit?*",
        "ask_name": "✨ *Wie se spesiale geleentheid vier ons vandag? Stuur hul naam:*",
        "ask_wish": "📝 *Skryf 'n lieflike wens of boodskap:*",
        "ask_dob_type": "⏳ *Hoe wil jy ouderdomsdetails byvoeg?*",
        "ask_dob_date": "📅 Stuur datum in **YYYY-MM-DD** formaat:",
        "ask_dob_direct": "🔢 Voer ouderdom direk as 'n nommer in:",
        "ask_year": "📅 *Kies die jaar:*",
        "ask_month": "📆 *Kies die maand:*",
        "ask_day": "🗓️ *Kies die dag:*",
        "ask_hour": "⏰ *Kies die uur (00 tot 23):*",
        "ask_minute": "⏱️ *Kies die minuut (00 tot 59):*",
        "ask_photo": "📸 *Deel 'n foto* (of slaan oor):",
        "ask_video": "🎥 *Deel 'n video* (of slaan oor):",
        "ask_song": "🎶 *Stuur 'n gunsteling liedjie* (of slaan oor):",
        "ask_voice": "🎙️ *Stuur 'n stemnota* (of slaan oor):",
        "ask_audio": "🎵 *Voeg nog 'n oudiolêer by* (of slaan oor):",
        "ready": "✨ *Alles gereed vir {name}!*",
    },
    "pt": {
        "welcome": "✨ *Bem-vindo ao seu cantinho de surpresas...*",
        "region_selected": "🌍 Região: *{region}*. Selecione seu país:",
        "country_choice": "🗣️ Escolha seu idioma para *{country}*:",
        "lang_updated": "✅ Idioma atualizado com sucesso!",
        "ask_category": "🎉 *Que tipo de celebração é esta?*",
        "ask_name": "✨ *De quem é a ocasião especial que estamos comemorando? Envie o nome:*",
        "ask_wish": "📝 *Escreva uma mensagem carinhosa:*",
        "ask_dob_type": "⏳ *Como você gostaria de adicionar os detalhes da idade?*",
        "ask_dob_date": "📅 Envie a data no formato **YYYY-MM-DD**:",
        "ask_dob_direct": "🔢 Digite a idade diretamente como número:",
        "ask_year": "📅 *Selecione o ano:*",
        "ask_month": "📆 *Selecione o mês:*",
        "ask_day": "🗓️ *Selecione o dia:*",
        "ask_hour": "⏰ *Selecione a Hora (00 a 23):*",
        "ask_minute": "⏱️ *Selecione o Minuto (00 a 59):*",
        "ask_photo": "📸 *Compartilhe uma foto* (ou pular):",
        "ask_video": "🎥 *Compartilhe um vídeo* (ou pular):",
        "ask_song": "🎶 *Envie uma música* (ou pular):",
        "ask_voice": "🎙️ *Envie uma nota de voz* (ou pular):",
        "ask_audio": "🎵 *Adicione outro áudio* (ou pular):",
        "ready": "✨ *Tudo pronto para {name}!*",
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
    await state.update_data(name=message.text)
    await state.set_state(BirthdayForm.wish)
    await message.answer(get_bot_text(message.from_user.id, "ask_wish"), reply_markup=get_action_keyboard(), parse_mode="Markdown")

@dp.message(BirthdayForm.wish)
async def process_wish(message: types.Message, state: FSMContext):
    await state.update_data(wish=message.text)
    await state.set_state(BirthdayForm.dob_choice)
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Enter Date (DOB)", callback_data="dob_date")],
        [InlineKeyboardButton(text="🔢 Enter Direct Details", callback_data="dob_direct")],
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
    await state.update_data(dob="")
    await ask_target_year(callback.message, state)
    await callback.answer()

@dp.message(BirthdayForm.dob_input)
async def process_dob_input(message: types.Message, state: FSMContext):
    await state.update_data(dob=message.text)
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
