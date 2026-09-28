<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>✨ Aura Luxury Realistic Celebrations ✨</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/canvas-confetti@1.6.0/dist/confetti.browser.min.js"></script>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: radial-gradient(circle at center, #130f23 0%, #030207 100%);
            color: #fff;
            font-family: 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            padding: 15px;
            text-align: center;
            overflow-y: auto;
            position: relative;
            transition: background 0.8s ease-in-out;
        }

        #liveBgCanvas, #effectsCanvas {
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; pointer-events: none;
        }
        #liveBgCanvas { z-index: 0; }
        #effectsCanvas { z-index: 99999; }

        .top-bar { width: 100%; max-width: 380px; display: flex; justify-content: flex-end; margin-bottom: 10px; z-index: 10; }
        .lang-select {
            background: rgba(255, 215, 0, 0.12); border: 1px solid rgba(255, 215, 0, 0.35); color: #ffd700;
            padding: 6px 14px; border-radius: 20px; font-size: 0.8rem; cursor: pointer; outline: none; backdrop-filter: blur(8px);
        }
        .lang-select option { background: #130f23; color: #fff; }

        .container {
            width: 100%; max-width: 380px; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 215, 0, 0.2);
            border-radius: 24px; padding: 18px; backdrop-filter: blur(16px); box-shadow: 0 15px 35px rgba(0,0,0,0.8);
            margin-bottom: 14px; position: relative; z-index: 2;
        }

        .header-box-base { border-radius: 20px; padding: 18px 14px; margin-bottom: 14px; transition: all 0.5s ease-in-out; }
        
        body.theme-Birthday-bg { background: radial-gradient(circle at center, #2b1235 0%, #040106 100%); }
        .theme-Birthday { background: linear-gradient(135deg, rgba(255,215,0,0.2), rgba(255,0,127,0.2)); border: 1px solid #ffd700; box-shadow: 0 0 25px rgba(255,215,0,0.3); }

        body.theme-Wedding-bg, body.theme-WeddingWish-bg { background: radial-gradient(circle at center, #092032 0%, #010407 100%); }
        .theme-Wedding, .theme-WeddingWish { background: linear-gradient(135deg, rgba(0,242,254,0.2), rgba(255,215,0,0.15)); border: 1px solid #00f2fe; box-shadow: 0 0 30px rgba(0,242,254,0.4); }

        body.theme-HouseWarming-bg { background: radial-gradient(circle at center, #1b382b 0%, #020604 100%); }
        .theme-HouseWarming { background: linear-gradient(135deg, rgba(0,255,150,0.2), rgba(255,215,0,0.2)); border: 1px solid #00ffaa; box-shadow: 0 0 30px rgba(0,255,150,0.4); }

        body.theme-Graduation-bg { background: radial-gradient(circle at center, #062b25 0%, #010504 100%); }
        .theme-Graduation { background: linear-gradient(135deg, rgba(0,255,150,0.15), rgba(0,242,254,0.2)); border: 1px solid #00ffaa; box-shadow: 0 0 30px rgba(0,255,150,0.4); }

        body.theme-NewBorn-bg { background: radial-gradient(circle at center, #2d1326 0%, #050104 100%); }
        .theme-NewBorn { background: linear-gradient(135deg, rgba(255,182,193,0.25), rgba(173,216,230,0.25)); border: 1px solid #ffb6c1; box-shadow: 0 0 30px rgba(255,182,193,0.5); }

        .category-title-text { font-size: 1.35rem; font-weight: 800; line-height: 1.4; letter-spacing: 0.5px; color: #ffd700; }

        .details-box {
            background: rgba(255, 215, 0, 0.04); border: 1px dashed rgba(255, 215, 0, 0.3); border-radius: 14px;
            padding: 10px; margin-bottom: 12px; font-size: 0.85rem; color: #f8fafc;
        }
        .details-box span { color: #ffd700; font-weight: 600; }

        .stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 8px; }
        .stat-card { background: rgba(255, 215, 0, 0.04); border: 1px solid rgba(255, 215, 0, 0.15); border-radius: 12px; padding: 8px; text-align: center; }
        .stat-card .num { font-size: 1rem; font-weight: bold; color: #ffd700; }
        .stat-card .label { font-size: 0.7rem; color: #cbd5e1; margin-top: 2px; }

        .open-when-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 8px; }
        .envelope-btn {
            background: rgba(255, 215, 0, 0.06); border: 1px solid rgba(255, 215, 0, 0.25); border-radius: 12px;
            padding: 10px 8px; color: #fff; font-size: 0.78rem; cursor: pointer; transition: all 0.2s; text-align: center;
        }

        #giftSection { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 40px 10px; cursor: pointer; }
        .gift-box { font-size: 5.5rem; cursor: pointer; animation: bounceGift 1.3s infinite ease-in-out; transition: transform 0.3s; user-select: none; }
        @keyframes bounceGift { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-12px); } }

        .scratch-container {
            position: relative; width: 100%; height: 240px; border-radius: 16px; overflow: hidden;
            background: linear-gradient(135deg, #22223b, #111122); border: 1px solid rgba(255, 215, 0, 0.3); color: #fff; margin: 8px auto; display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 12px;
        }
        canvas#scratchCanvas { position: absolute; top: 0; left: 0; width: 100%; height: 100%; cursor: pointer; touch-action: none; z-index: 2; }
        
        .hidden-content { width: 100%; height: 100%; overflow-y: auto; padding: 10px; z-index: 1; display: flex; flex-direction: column; justify-content: center; }
        .hidden-content h3 { color: #ffd700; margin-bottom: 6px; font-size: 1rem; }
        .hidden-content p { color: #e2e8f0; font-size: 0.85rem; line-height: 1.4; white-space: pre-wrap; word-wrap: break-word; }

        .single-photo-box { width: 100%; max-height: 240px; border-radius: 14px; overflow: hidden; margin-bottom: 10px; background: #000; display: flex; align-items: center; justify-content: center; border: 1px solid rgba(255, 215, 0, 0.3); }
        .single-photo-box img { width: 100%; max-height: 230px; object-fit: contain; }

        .media-box video { width: 100%; max-height: 280px; border-radius: 12px; background: #000; margin-bottom: 6px; }
        .media-box audio { width: 100%; margin-top: 6px; border-radius: 10px; margin-bottom: 8px; height: 36px; }

        .fs-btn { background: rgba(255, 215, 0, 0.15); border: 1px solid #ffd700; color: #ffd700; font-size: 0.75rem; padding: 6px 14px; border-radius: 15px; margin-bottom: 8px; cursor: pointer; font-weight: 600; }

        .story-stage {
            width: 100%; min-height: 290px;
            background: radial-gradient(circle at bottom, rgba(255,215,0,0.15) 0%, rgba(6,4,12,0.98) 85%);
            border-radius: 20px; border: 1px solid rgba(255,215,0,0.4);
            margin: 12px 0; padding: 20px; position: relative;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
            box-shadow: inset 0 0 35px rgba(0,0,0,0.95), 0 0 25px rgba(255,215,0,0.2);
            overflow: hidden;
        }

        .visual-world-card {
            width: 100%; padding: 16px; border-radius: 16px;
            background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01));
            border: 1px solid rgba(255,215,0,0.3); backdrop-filter: blur(10px);
            box-shadow: 0 10px 25px rgba(0,0,0,0.5); margin-bottom: 10px;
            display: flex; flex-direction: column; align-items: center; justify-content: center;
        }
        .world-title { font-size: 1.1rem; font-weight: 700; color: #ffd700; margin-bottom: 4px; }
        .world-subtitle { font-size: 0.78rem; color: #e2e8f0; line-height: 1.3; }

        .birthday-cake-stage {
            position: relative; width: 100%; height: 120px; display: flex; flex-direction: column; align-items: center; justify-content: flex-end; margin-bottom: 10px;
        }
        .cake-body {
            width: 110px; height: 45px; background: linear-gradient(135deg, #ff007f, #ff758c); border-radius: 10px 10px 0 0; position: relative; box-shadow: 0 0 20px rgba(255,0,127,0.5);
        }
        .cake-top {
            width: 120px; height: 18px; background: #fff; border-radius: 10px; position: absolute; top: -9px; left: -5px; box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        }
        .candle {
            width: 7px; height: 28px; background: linear-gradient(to top, #00f2fe, #4facfe); position: absolute; top: -30px; border-radius: 4px;
        }
        .candle.c1 { left: 30px; }
        .candle.c2 { left: 52px; }
        .candle.c3 { left: 74px; }
        .flame {
            width: 10px; height: 14px; background: #ffd700; border-radius: 50% 50% 20% 20%; position: absolute; top: -13px; left: -1px;
            box-shadow: 0 0 15px #ffaa00; animation: flameFlicker 0.6s infinite alternate;
        }
        .flame.extinguished { display: none; }
        @keyframes flameFlicker {
            0% { transform: scale(1) rotate(-3deg); background: #ffd700; }
            100% { transform: scale(1.15) rotate(3deg); background: #ff4500; }
        }

        .lamp-stage { font-size: 4rem; animation: lampGlow 1.5s infinite alternate; margin-bottom: 5px; }
        @keyframes lampGlow { 0% { filter: drop-shadow(0 0 5px #ffd700); } 100% { filter: drop-shadow(0 0 25px #ff4500); } }

        .story-caption { font-size: 0.88rem; color: #ffd700; margin-top: 8px; font-weight: 600; min-height: 26px; }

        .btn-group { display: flex; flex-wrap: wrap; justify-content: center; gap: 6px; margin-top: 8px; }
        .btn {
            background: linear-gradient(45deg, #ffd700, #ffaa00); color: #130f23; border: none; padding: 10px 18px; font-size: 0.82rem;
            border-radius: 22px; cursor: pointer; font-weight: 700; box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3); transition: all 0.2s;
        }
        .btn:active { transform: scale(0.95); }
        .btn-heart { background: linear-gradient(45deg, #ff3366, #ff6b81); color: #fff; }

        .locked-screen { display: none; padding: 30px 15px; }
        .timer-digits { font-size: 1.4rem; color: #ffd700; font-weight: bold; margin: 12px 0; }

        .modal-overlay {
            display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.85); z-index: 9999; align-items: center; justify-content: center; padding: 20px;
        }
        .modal-box {
            background: #130f23; border: 1px solid #ffd700; border-radius: 20px; padding: 20px;
            width: 100%; max-width: 320px; text-align: center; box-shadow: 0 0 30px rgba(255, 215, 0, 0.3);
        }
        .modal-box p { font-size: 0.95rem; line-height: 1.5; color: #f8fafc; margin-bottom: 16px; white-space: pre-wrap; }

        .video-fullscreen-overlay {
            position: fixed !important; top: 0 !important; left: 0 !important; width: 100vw !important; height: 100vh !important; max-height: 100vh !important;
            z-index: 999999 !important; background: #000 !important; object-fit: contain !important; border-radius: 0 !important; margin: 0 !important;
        }
        .close-fs-btn {
            position: fixed; top: 20px; right: 20px; z-index: 1000000; background: rgba(0, 0, 0, 0.7); color: #ffd700; border: 2px solid #ffd700;
            border-radius: 50%; width: 44px; height: 44px; font-size: 1.3rem; cursor: pointer; display: none;
        }
    </style>
</head>
<body>

    <canvas id="liveBgCanvas"></canvas>
    <canvas id="effectsCanvas"></canvas>

    <button id="closeFsBtn" class="close-fs-btn" onclick="exitCustomFullscreen()">✕</button>

    <div class="top-bar">
        <select id="langSwitcher" class="lang-select" onchange="changeLanguage(this.value)">
            <option value="en">English</option>
            <option value="ml">മലയാളം</option>
            <option value="ru">Русский</option>
            <option value="fa">فارسی</option>
            <option value="it">Italiano</option>
            <option value="id">Bahasa Indonesia</option>
            <option value="uz">Oʻzbekcha</option>
            <option value="tg">Тоҷикӣ</option>
            <option value="az">Azərbaycan</option>
            <option value="my">မြန်မာ</option>
            <option value="zh">中文</option>
            <option value="hi">हिन्दी</option>
        </select>
    </div>

    <div id="lockSection" class="container locked-screen">
        <h2 id="lockTitle">⏳ Portal Locked!</h2>
        <p id="lockSubtitle" style="color: #cbd5e1; font-size: 0.85rem; margin-top: 4px;">This exclusive surprise opens on:</p>
        <p id="targetTimeDisplay" style="color: #ffd700; font-weight: bold; margin: 6px 0; font-size: 1rem;"></p>
        <div class="timer-digits" id="countdownTimer">Loading countdown...</div>
    </div>

    <div id="giftSection" class="container" onclick="openGift()">
        <h2 id="giftPrompt" style="font-size: 1.2rem;">🎁 Tap the Gift Box to Unwrap!</h2>
        <div class="gift-box">🎁</div>
        <p id="giftSubPrompt" style="font-size: 0.8rem; color: #cbd5e1; margin-top: 8px;">Tap anywhere to reveal your special surprise...</p>
    </div>

    <div id="mainContent" style="display: none; width: 100%; max-width: 380px;">

        <div class="header-box-base" id="royalHeaderContainer">
            <h1 class="category-title-text" id="royalTitleBox">
                <span id="mainTitle">Celebration</span>, <span id="recipientName">Friend</span>! ✨
            </h1>
        </div>
        
        <div class="details-box" id="infoBox">
            <div>📅 <span id="targetTimeText">Target Time</span>: <span id="displayDate">-</span></div>
        </div>

        <div class="container" style="padding: 12px;" id="statsContainer">
            <h4 id="statsTitle" style="color: #ffd700; font-size: 0.9rem; margin-bottom: 6px;">⏳ Journey Statistics</h4>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="num" id="statDays">-</div>
                    <div class="label" id="labelDays">Days</div>
                </div>
                <div class="stat-card">
                    <div class="num" id="statHours">-</div>
                    <div class="label" id="labelHours">Hours</div>
                </div>
            </div>
        </div>

        <div class="container" style="padding: 12px;" id="openWhenContainer">
            <h4 id="openWhenTitle" style="color: #ffd700; font-size: 0.9rem; margin-bottom: 6px;">💌 Open When...</h4>
            <div class="open-when-grid">
                <button class="envelope-btn" onclick="openEnvelope('sad')">💙 You're Sad</button>
                <button class="envelope-btn" onclick="openEnvelope('laugh')">😂 Need a Laugh</button>
                <button class="envelope-btn" onclick="openEnvelope('miss')">🥰 You Miss Me</button>
                <button class="envelope-btn" onclick="openEnvelope('vibe')">✨ Special Vibe</button>
            </div>
        </div>

        <p id="scratchInstruction" style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 8px;">👇 Scratch the card below to reveal your surprise!</p>

        <div class="container">
            <div class="scratch-container">
                <div class="hidden-content">
                    <h3 id="surpriseHeader">🎉 SPECIAL SURPRISE 🎁</h3>
                    <p id="wishMessage">Wishing you an extraordinary day filled with joy and success!</p>
                </div>
                <canvas id="scratchCanvas"></canvas>
            </div>
        </div>

        <div class="container" id="mediaSection" style="margin-top: 10px;">
            <h3 id="celebrationHeader" style="font-size: 1.1rem; margin-bottom: 8px;">✨ Celebration Stage</h3>
            
            <div id="singlePhotoWrapper" class="single-photo-box" style="display:none;">
                <img id="singlePhotoImg" src="" alt="Surprise Photo">
            </div>
            
            <div id="mediaContainer" class="media-box"></div>
            
            <div class="story-stage" id="storyStageContainer"></div>
            
            <div class="btn-group" id="primaryActionButtons"></div>
            
            <div class="btn-group">
                <button class="btn" style="background: linear-gradient(45deg, #ff007f, #ffd700); font-size: 0.88rem;" onclick="fireExtremeDualPoppers()" id="btnPopper">🎊 3D Stage Popper</button>
            </div>
            <div class="btn-group">
                <button class="btn btn-heart" onclick="send3DLoveHearts()" id="btnLove">❤️ Send Love</button>
                <button class="btn" style="background: linear-gradient(45deg, #00ffcc, #00b894);" onclick="launchGrandFireworks()" id="btnFireworks">🎆 Grand Fireworks</button>
            </div>
        </div>
    </div>

    <div class="modal-overlay" id="customModal">
        <div class="modal-box">
            <p id="modalMsgText"></p>
            <button class="btn" onclick="closeModal()">Close ✨</button>
        </div>
    </div>

    <script>
        const BOT_API_URL = "https://aura-birthday-production-3f7a.up.railway.app";

        const bgCanvas = document.getElementById('liveBgCanvas');
        const bgCtx = bgCanvas.getContext('2d');
        const fxCanvas = document.getElementById('effectsCanvas');
        const fxCtx = fxCanvas.getContext('2d');
        let particles = [], customPetals = [], customBalloons = [], customHearts = [];

        function resizeCanvases() {
            bgCanvas.width = fxCanvas.width = window.innerWidth;
            bgCanvas.height = fxCanvas.height = window.innerHeight;
        }
        window.addEventListener('resize', resizeCanvases);
        resizeCanvases();

        for (let i = 0; i < 40; i++) {
            particles.push({
                x: Math.random() * bgCanvas.width,
                y: Math.random() * bgCanvas.height,
                radius: Math.random() * 2 + 0.5,
                alpha: Math.random() * 0.7 + 0.2,
                speedY: Math.random() * 0.4 + 0.1,
                color: ['#ffd700', '#ff007f', '#00f2fe', '#ffffff'][Math.floor(Math.random() * 4)]
            });
        }

        function animateCanvas() {
            bgCtx.clearRect(0, 0, bgCanvas.width, bgCanvas.height);
            particles.forEach(p => {
                p.y -= p.speedY;
                if (p.y < 0) p.y = bgCanvas.height;
                bgCtx.beginPath();
                bgCtx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                bgCtx.fillStyle = p.color;
                bgCtx.globalAlpha = p.alpha;
                bgCtx.fill();
            });

            fxCtx.clearRect(0, 0, fxCanvas.width, fxCanvas.height);

            for (let i = customPetals.length - 1; i >= 0; i--) {
                let pt = customPetals[i];
                pt.y += pt.speedY;
                pt.x += Math.sin(pt.wobble) * 1.6;
                pt.wobble += 0.04;
                pt.rotation += pt.rotSpeed;

                fxCtx.save();
                fxCtx.translate(pt.x, pt.y);
                fxCtx.rotate(pt.rotation);
                fxCtx.beginPath();
                fxCtx.ellipse(0, 0, pt.size, pt.size * 0.65, 0, 0, Math.PI * 2);
                fxCtx.fillStyle = pt.color;
                fxCtx.shadowColor = "#800020";
                fxCtx.shadowBlur = 6;
                fxCtx.fill();
                fxCtx.restore();

                if (pt.y > fxCanvas.height + 50) customPetals.splice(i, 1);
            }

            for (let i = customBalloons.length - 1; i >= 0; i--) {
                let bl = customBalloons[i];
                bl.y -= bl.speedY;
                bl.x += Math.sin(bl.wobble) * 1.2;
                bl.wobble += 0.03;

                fxCtx.save();
                fxCtx.beginPath();
                fxCtx.ellipse(bl.x, bl.y, bl.radius * 0.85, bl.radius, 0, 0, Math.PI * 2);
                fxCtx.fillStyle = bl.color;
                fxCtx.shadowColor = bl.color;
                fxCtx.shadowBlur = 10;
                fxCtx.fill();

                fxCtx.beginPath();
                fxCtx.moveTo(bl.x, bl.y + bl.radius);
                fxCtx.lineTo(bl.x + Math.sin(bl.wobble) * 4, bl.y + bl.radius + 20);
                fxCtx.strokeStyle = "rgba(255,255,255,0.4)";
                fxCtx.lineWidth = 1;
                fxCtx.stroke();
                fxCtx.restore();

                if (bl.y < -80) customBalloons.splice(i, 1);
            }

            for (let i = customHearts.length - 1; i >= 0; i--) {
                let h = customHearts[i];
                h.y += h.speedY;
                h.x += Math.sin(h.wobble) * 1.5;
                h.wobble += 0.05;

                fxCtx.save();
                fxCtx.translate(h.x, h.y);
                fxCtx.font = `${h.size}px serif`;
                fxCtx.shadowColor = "#ff007f";
                fxCtx.shadowBlur = 8;
                fxCtx.fillText("❤️", 0, 0);
                fxCtx.restore();

                if (h.y > fxCanvas.height + 40) customHearts.splice(i, 1);
            }

            requestAnimationFrame(animateCanvas);
        }
        animateCanvas();

        const translations = {
            'en': {
                lockTitle: "⏳ Portal Locked!", lockSubtitle: "This exclusive surprise opens on:",
                giftPrompt: "🎁 Tap the Gift Box to Unwrap!", giftSubPrompt: "Tap anywhere to reveal your special surprise...",
                targetTimeText: "Target Time", scratchInstruction: "👇 Scratch the card below to reveal your surprise!",
                surpriseHeader: "🎉 SPECIAL SURPRISE 🎁", celebrationHeader: "✨ Celebration Stage",
                statsTitle: "⏳ Journey Statistics", labelDays: "Days", labelHours: "Hours",
                openWhenTitle: "💌 Open When...", btnPopper: "🎊 3D Stage Popper", btnLove: "❤️ Send Love", btnFireworks: "🎆 Grand Fireworks",
                btnBirthdayStory: "🎂 Birthday Cake Story", btnWeddingStory: "💒 Wedding Story",
                btnAnniversaryStory: "💍 Anniversary Story", btnGraduationStory: "🎓 Graduation Story",
                btnBabyStory: "👶 Baby Born Story", btnHouseWarmingStory: "🏡 House Warming Story", btnFestivalStory: "🏮 Festival Story",
                categories: {
                    "Birthday": "🎂 Happy Birthday",
                    "Proposal": "💍 Magical Proposal",
                    "WeddingWish": "💒 Happy Married Life",
                    "Wedding": "💍 Happy Wedding Anniversary",
                    "NewBorn": "👶 Welcome Little Angel",
                    "Graduation": "🎓 Congratulations on Graduation",
                    "HouseWarming": "🏡 Happy House Warming",
                    "Festival": "🏮 Happy Festival"
                }
            },
            'ml': {
                lockTitle: "⏳ പോർട്ടൽ ലോക്ക് ചെയ്തിരിക്കുന്നു!", lockSubtitle: "ഈ പ്രത്യേക സർപ്രൈസ് തുറക്കുന്ന സമയം:",
                giftPrompt: "🎁 തുറക്കാൻ ഗിഫ്റ്റ് ബോക്സിൽ അമർത്തൂ!", giftSubPrompt: "നിങ്ങളുടെ സർപ്രൈസ് കാണാൻ ടാപ്പ് ചെയ്യൂ...",
                targetTimeText: "ലഭ്യമാകുന്ന സമയം", scratchInstruction: "👇 സർപ്രൈസ് കാണാൻ താഴെ സ്ക്രാച്ച് ചെയ്യുക!",
                surpriseHeader: "🎉 പ്രത്യേക സർപ്രൈസ് 🎁", celebrationHeader: "✨ ആഘോഷ വേദി",
                statsTitle: "⏳ യാത്രയുടെ കണക്കുകൾ", labelDays: "ദിവസങ്ങൾ", labelHours: "മണിക്കൂറുകൾ",
                openWhenTitle: "💌 ഈ സമയങ്ങളിൽ തുറക്കൂ...", btnPopper: "🎊 3D സ്റ്റേജ് പോപ്പർ", btnLove: "❤️ സ്നേഹം അയക്കുക", btnFireworks: "🎆 കരിമരുന്ന് പ്രയോഗം",
                btnBirthdayStory: "🎂 കേക്ക് കട്ടിംഗ് സ്റ്റോറി", btnWeddingStory: "💒 വെഡ്ഡിംഗ് സ്റ്റോറി",
                btnAnniversaryStory: "💍 ആനിവേഴ്സറി സ്റ്റോറി", btnGraduationStory: "🎓 ഗ്രാജുവേഷൻ സ്റ്റോറി",
                btnBabyStory: "👶 ബേബി ബോൺ സ്റ്റോറി", btnHouseWarmingStory: "🏡 ഗൃഹപ്രവേശ സ്റ്റോറി", btnFestivalStory: "🏮 ഫെസ്റ്റിവൽ സ്റ്റോറി",
                categories: {
                    "Birthday": "🎂 ജന്മദിനാശംസകൾ",
                    "Proposal": "💍 മാന്ത്രിക പ്രൊപ്പോസൽ",
                    "WeddingWish": "💒 മംഗളകരമായ ദാമ്പത്യജീവിതം",
                    "Wedding": "💍 വിവാഹ വാർഷികാശംസകൾ",
                    "NewBorn": "👶 കുഞ്ഞുമാലാഖയ്ക്ക് സ്വാഗതം",
                    "Graduation": "🎓 ബിരുദ ആശംസകൾ",
                    "HouseWarming": "🏡 ഗൃഹപ്രവേശ ആശംസകൾ",
                    "Festival": "🏮 ആഘോഷ ആശംസകൾ"
                }
            }
        };

        function getTranslation(lang, key) {
            if (translations[lang] && translations[lang][key]) return translations[lang][key];
            if (translations['en'][key]) return translations['en'][key];
            return '';
        }

        let currentLang = 'en';
        let currentCategory = 'Birthday';
        let currentGender = 'boy';

        const openWhenMessages = {
            'sad': "💙 Cheer up! Remember that storms don't last forever. You are stronger, brighter, and more loved than you can ever imagine. Smile! 😊",
            'laugh': "😂 Just a reminder: You are delightfully funny, wonderfully unique, and completely irreplaceable! Keep smiling!",
            'miss': "🥰 Distance means so little when love and friendship mean so much. I'm always right here with you in spirit! ❤️",
            'vibe': "✨ Turn up the music, close your eyes, and soak in this beautiful day. This celebration is all about you! 🎉"
        };

        function openEnvelope(type) {
            document.getElementById('modalMsgText').innerText = openWhenMessages[type] || "You are special!";
            document.getElementById('customModal').style.display = 'flex';
            confetti({ particleCount: 40, spread: 60, origin: { y: 0.6 } });
        }

        function closeModal() {
            document.getElementById('customModal').style.display = 'none';
        }

        function changeLanguage(selectedLang) {
            currentLang = selectedLang;
            applyTranslations(selectedLang);
            renderCategoryActions();
        }

        function applyTranslations(lang) {
            ['lockTitle', 'lockSubtitle', 'giftPrompt', 'giftSubPrompt', 'targetTimeText', 'scratchInstruction', 'surpriseHeader', 'celebrationHeader', 'statsTitle', 'labelDays', 'labelHours', 'openWhenTitle', 'btnPopper', 'btnLove', 'btnFireworks'].forEach(id => {
                let el = document.getElementById(id);
                if (el) el.innerText = getTranslation(lang, id);
            });
            let catMap = (translations[lang] && translations[lang].categories) ? translations[lang].categories : translations['en'].categories;
            document.getElementById('mainTitle').innerText = catMap[currentCategory] || currentCategory;

            let themeKey = ['Birthday', 'Proposal', 'WeddingWish', 'Wedding', 'NewBorn', 'Graduation', 'HouseWarming', 'Festival'].includes(currentCategory) ? currentCategory : 'Birthday';
            let headerBox = document.getElementById('royalHeaderContainer');
            if (headerBox) headerBox.className = 'header-box-base theme-' + themeKey;
            document.body.className = `theme-${themeKey}-bg`;
        }

        function playBirthdayStory() {
            const flame1 = document.getElementById('candleFlame1');
            const flame2 = document.getElementById('candleFlame2');
            const flame3 = document.getElementById('candleFlame3');
            const caption = document.getElementById('storyCaptionText');
            caption.innerText = "🎂 Glowing candles are lit... Making a wish! ✨";
            setTimeout(() => {
                if (flame1) flame1.classList.add('extinguished');
                if (flame2) flame2.classList.add('extinguished');
                if (flame3) flame3.classList.add('extinguished');
                caption.innerText = "🎉 Candles blown out! Cutting the delicious cake! 🍰";
                confetti({ particleCount: 80, spread: 70, origin: { y: 0.6 } });
            }, 1800);
            setTimeout(() => {
                caption.innerText = "✨ Happy Birthday! Wishing you joy and success! 🎈";
                launchGrandFireworks();
            }, 3500);
        }

        function playWeddingStory() {
            const caption = document.getElementById('storyCaptionText');
            caption.innerText = "💒 Romantic background music playing as they walk and dance together... 🎶";
            shower3DRedRoses();
            fireExtremeDualPoppers();
            setTimeout(() => {
                caption.innerText = "✨ Wishing you a lifetime of shared love and grace! 💍🥂";
                launchGrandFireworks();
            }, 2500);
        }

        function playAnniversaryStory() {
            const caption = document.getElementById('storyCaptionText');
            caption.innerText = "💞 Golden memories lighting up as romantic golden dust particles surround the dancing couple...";
            shower3DRedRoses();
            fireExtremeDualPoppers();
            setTimeout(() => {
                caption.innerText = "✨ Happy Anniversary! Cherishing every beautiful moment together. 🥂💫";
                launchGrandFireworks();
            }, 2500);
        }

        function playGraduationStory() {
            const caption = document.getElementById('storyCaptionText');
            let gradIcon = currentGender === 'girl' ? '👩‍🎓' : '👨‍🎓';
            caption.innerText = `🎓 University auditorium stage under bright spotlights, ${gradIcon} walking proudly with diploma in hand!`;
            fireExtremeDualPoppers();
            setTimeout(() => {
                caption.innerText = "🌟 Congratulations on your remarkable academic milestone! ✨🎓";
                launchGrandFireworks();
            }, 2500);
        }

        function playBabyStory() {
            const caption = document.getElementById('storyCaptionText');
            let babyEmoji = currentGender === 'girl' ? '👶🎀' : '👶💙';
            caption.innerText = `${babyEmoji} Soft nursery lights, gentle music playing under a starry night sky...`;
            release3DPastelBalloons();
            setTimeout(() => {
                caption.innerText = "✨ Welcome little angel, bringing boundless warmth and joy! 🌟👶";
                launchGrandFireworks();
            }, 2500);
        }

        function playHouseWarmingStory() {
            const caption = document.getElementById('storyCaptionText');
            caption.innerText = "🏡 Lighting the traditional lamp, welcoming prosperity, love, and light into the new home... ✨";
            fireExtremeDualPoppers();
            setTimeout(() => {
                caption.innerText = "✨ May your new house turn into a blessed and happy home! 🌸";
                launchGrandFireworks();
            }, 2500);
        }

        function renderCategoryActions() {
            let container = document.getElementById('primaryActionButtons');
            let stage = document.getElementById('storyStageContainer');
            let texts = translations[currentLang] || translations['en'];

            if (currentCategory === 'WeddingWish') {
                stage.innerHTML = `
                    <div class="visual-world-card">
                        <div class="world-title">Elegant Wedding Venue</div>
                        <div class="world-subtitle">Soft rose petals, golden rings, and glowing couple aura</div>
                    </div>
                    <div class="story-caption" id="storyCaptionText">✨ Tap below to experience wedding magic! ✨</div>
                `;
                container.innerHTML = `<button class="btn" style="background:linear-gradient(45deg,#00f2fe,#4facfe); color:#000;" onclick="playWeddingStory()">${texts.btnWeddingStory}</button>`;
            } else if (currentCategory === 'Wedding') {
                stage.innerHTML = `
                    <div class="visual-world-card">
                        <div class="world-title">Anniversary Memory Lane</div>
                        <div class="world-subtitle">Precious photographs floating through golden dust particles</div>
                    </div>
                    <div class="story-caption" id="storyCaptionText">✨ Tap below to begin anniversary story! ✨</div>
                `;
                container.innerHTML = `<button class="btn" style="background:linear-gradient(45deg,#ffd700,#ffaa00); color:#000;" onclick="playAnniversaryStory()">${texts.btnAnniversaryStory}</button>`;
            } else if (currentCategory === 'Graduation') {
                stage.innerHTML = `
                    <div class="visual-world-card">
                        <div class="world-title">University Spotlight Stage</div>
                        <div class="world-subtitle">Prestigious diploma presentation under bright spotlights</div>
                    </div>
                    <div class="story-caption" id="storyCaptionText">✨ Tap below to walk the graduation stage! ✨</div>
                `;
                container.innerHTML = `<button class="btn" style="background:linear-gradient(45deg,#00ffaa,#00f2fe); color:#000;" onclick="playGraduationStory()">${texts.btnGraduationStory}</button>`;
            } else if (currentCategory === 'NewBorn') {
                stage.innerHTML = `
                    <div class="visual-world-card">
                        <div class="world-title">Soft Nursery & Starlit Sky</div>
                        <div class="world-subtitle">Warm soothing light, twinkling stars, and gentle moon glow</div>
                    </div>
                    <div class="story-caption" id="storyCaptionText">✨ Tap below to welcome the little angel! ✨</div>
                `;
                container.innerHTML = `<button class="btn" style="background:linear-gradient(45deg,#ff9ff3,#feca57); color:#000;" onclick="playBabyStory()">${texts.btnBabyStory}</button>`;
            } else if (currentCategory === 'HouseWarming') {
                stage.innerHTML = `
                    <div class="lamp-stage">🪔</div>
                    <div class="story-caption" id="storyCaptionText">✨ Tap below to light the traditional lamp! ✨</div>
                `;
                container.innerHTML = `<button class="btn" style="background:linear-gradient(45deg,#00ffaa,#ffd700); color:#000;" onclick="playHouseWarmingStory()">${texts.btnHouseWarmingStory}</button>`;
            } else {
                stage.innerHTML = `
                    <div class="birthday-cake-stage">
                        <div class="cake-body">
                            <div class="cake-top"></div>
                            <div class="candle c1"><div id="candleFlame1" class="flame"></div></div>
                            <div class="candle c2"><div id="candleFlame2" class="flame"></div></div>
                            <div class="candle c3"><div id="candleFlame3" class="flame"></div></div>
                        </div>
                    </div>
                    <div class="story-caption" id="storyCaptionText">✨ Tap below to blow candles & cut cake! ✨</div>
                `;
                container.innerHTML = `<button class="btn" style="background:linear-gradient(45deg,#ff007f,#ffd700); font-size:0.9rem;" onclick="playBirthdayStory()">${texts.btnBirthdayStory}</button>`;
            }
        }

        let urlParams = new URLSearchParams(window.location.search);
        let surpriseId = urlParams.get('id');
        let targetTimeStr = '';

        function calculateLifeStats(dobOrAge) {
            let diffDays = 20 * 365, diffHours = 20 * 365 * 24;
            if (dobOrAge) {
                let strVal = dobOrAge.toString().trim();
                if (strVal.includes('-')) {
                    let birthDate = new Date(strVal);
                    if (!isNaN(birthDate)) {
                        let diffTime = Math.abs(new Date() - birthDate);
                        diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
                        diffHours = Math.floor(diffTime / (1000 * 60 * 60));
                    }
                } else if (!isNaN(strVal)) {
                    let age = parseInt(strVal);
                    diffDays = age * 365;
                    diffHours = age * 365 * 24;
                }
            }
            document.getElementById('statDays').innerText = diffDays.toLocaleString();
            document.getElementById('statHours').innerText = diffHours.toLocaleString();
        }

        async function loadSurpriseData() {
            let name = 'Friend', msg = 'Wishing you an extraordinary day!', photoUrl = '', video = '', song = '', voice = '', extraAudio = '', dobOrAge = '';

            if (surpriseId) {
                try {
                    let response = await fetch(`${BOT_API_URL}/api/surprise?id=${surpriseId}`);
                    if (response.ok) {
                        let data = await response.json();
                        name = data.name || name;
                        msg = data.msg || msg;
                        currentCategory = data.category || 'Birthday';
                        currentGender = data.gender || 'boy';
                        targetTimeStr = data.target_time || '';
                        photoUrl = data.photo || '';
                        video = data.video || '';
                        song = data.song || '';
                        voice = data.voice || '';
                        extraAudio = data.extra_audio || '';
                        currentLang = data.lang || 'en';
                        dobOrAge = data.dob || data.age || '';
                    }
                } catch (e) {
                    console.error("API Error:", e);
                }
            }

            document.getElementById('langSwitcher').value = currentLang;
            applyTranslations(currentLang);
            renderCategoryActions();

            document.getElementById('recipientName').innerText = name;
            document.getElementById('wishMessage').innerText = msg;
            if (targetTimeStr) {
                document.getElementById('displayDate').innerText = targetTimeStr.replace('T', ' ');
            }

            calculateLifeStats(dobOrAge);

            let photoWrapper = document.getElementById('singlePhotoWrapper');
            let photoImg = document.getElementById('singlePhotoImg');
            if (photoUrl) {
                photoWrapper.style.display = 'flex';
                photoImg.src = photoUrl;
            }

            let mediaContainer = document.getElementById('mediaContainer');
            mediaContainer.innerHTML = '';
            if (video) {
                mediaContainer.innerHTML += `
                    <div style="margin-top:10px;">
                        <video id="surpriseVideo" controls playsinline preload="auto" src="${video}"></video>
                        <br>
                        <button class="fs-btn" onclick="openFullscreenVideo()">⛶ Fullscreen Video</button>
                    </div>`;
            }
            if (song) mediaContainer.innerHTML += `<div style="margin-top:8px;"><p style="font-size:0.8rem; color:#ffd700;">🎶 Song / Music</p><audio controls src="${song}"></audio></div>`;
            if (voice) mediaContainer.innerHTML += `<div style="margin-top:8px;"><p style="font-size:0.8rem; color:#ffd700;">🎙️ Voice Greeting</p><audio controls src="${voice}"></audio></div>`;
            if (extraAudio) mediaContainer.innerHTML += `<div style="margin-top:8px;"><p style="font-size:0.8rem; color:#ffd700;">🎵 Extra Audio</p><audio controls src="${extraAudio}"></audio></div>`;

            checkTimeLock();
        }

        function openFullscreenVideo() {
            let vid = document.getElementById('surpriseVideo');
            let closeBtn = document.getElementById('closeFsBtn');
            if (!vid) return;
            vid.classList.add('video-fullscreen-overlay');
            if (closeBtn) closeBtn.style.display = 'block';
            vid.play();
        }

        function exitCustomFullscreen() {
            let vid = document.getElementById('surpriseVideo');
            let closeBtn = document.getElementById('closeFsBtn');
            if (vid) vid.classList.remove('video-fullscreen-overlay');
            if (closeBtn) closeBtn.style.display = 'none';
        }

        function openGift() {
            confetti({ particleCount: 200, spread: 110, origin: { y: 0.5 } });
            document.getElementById('giftSection').style.display = 'none';
            document.getElementById('mainContent').style.display = 'block';
            setTimeout(initCanvas, 150);
        }

        function checkTimeLock() {
            let isPreview = urlParams.get('preview') === 'true';
            if (!targetTimeStr || isPreview) { 
                document.getElementById('lockSection').style.display = 'none';
                return; 
            }
            let targetTime = new Date(targetTimeStr).getTime();
            let now = new Date().getTime();
            let distance = targetTime - now;

            if (distance <= 0) {
                document.getElementById('lockSection').style.display = 'none';
                document.getElementById('giftSection').style.display = 'flex';
            } else {
                document.getElementById('lockSection').style.display = 'block';
                document.getElementById('giftSection').style.display = 'none';
                document.getElementById('targetTimeDisplay').innerText = targetTimeStr.replace('T', ' ');
                let timerInterval = setInterval(() => {
                    let dist = targetTime - new Date().getTime();
                    if (dist <= 0) {
                        clearInterval(timerInterval);
                        location.reload();
                    } else {
                        let d = Math.floor(dist / (1000 * 60 * 60 * 24));
                        let h = Math.floor((dist % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                        let m = Math.floor((dist % (1000 * 60 * 60)) / (1000 * 60));
                        let s = Math.floor((dist % (1000 * 60)) / 1000);
                        document.getElementById('countdownTimer').innerText = `${d}d ${h}h ${m}m ${s}s`;
                    }
                }, 1000);
            }
        }

        let canvas = document.getElementById('scratchCanvas');
        let ctx = canvas ? canvas.getContext('2d') : null;

        function initCanvas() {
            if (!canvas) return;
            canvas.width = canvas.parentElement.clientWidth;
            canvas.height = canvas.parentElement.clientHeight;
            ctx.globalCompositeOperation = 'source-over';
            let grad = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
            grad.addColorStop(0, '#bdc3c7'); grad.addColorStop(1, '#2c3e50');
            ctx.fillStyle = grad; ctx.fillRect(0, 0, canvas.width, canvas.height);
            ctx.fillStyle = '#ffd700'; ctx.font = 'bold 15px sans-serif';
            ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
            ctx.fillText('✨ SCRATCH HERE ✨', canvas.width / 2, canvas.height / 2);
        }

        let isDrawing = false;
        function scratch(x, y) {
            ctx.globalCompositeOperation = 'destination-out';
            ctx.beginPath(); ctx.arc(x, y, 22, 0, Math.PI * 2); ctx.fill();
        }
        function getPos(e) {
            let rect = canvas.getBoundingClientRect();
            let cx = e.touches ? e.touches[0].clientX : e.clientX;
            let cy = e.touches ? e.touches[0].clientY : e.clientY;
            return { x: cx - rect.left, y: cy - rect.top };
        }
        if (canvas) {
            canvas.addEventListener('mousedown', (e) => { isDrawing = true; let p = getPos(e); scratch(p.x, p.y); });
            canvas.addEventListener('mousemove', (e) => { if (isDrawing) { let p = getPos(e); scratch(p.x, p.y); } });
            window.addEventListener('mouseup', () => isDrawing = false);
            canvas.addEventListener('touchstart', (e) => { isDrawing = true; let p = getPos(e); scratch(p.x, p.y); e.preventDefault(); });
            canvas.addEventListener('touchmove', (e) => { if (isDrawing) { let p = getPos(e); scratch(p.x, p.y); e.preventDefault(); } });
            canvas.addEventListener('touchend', () => isDrawing = false);
        }

        function fireExtremeDualPoppers() {
            confetti({ particleCount: 90, angle: 60, spread: 80, origin: { x: 0, y: 0.95 }, colors: ['#ffd700', '#ff007f', '#00f2fe', '#ffffff'] });
            confetti({ particleCount: 90, angle: 120, spread: 80, origin: { x: 1, y: 0.95 }, colors: ['#ffd700', '#ff007f', '#00f2fe', '#ffffff'] });
        }

        function shower3DRedRoses() {
            let shades = ['#b3002d', '#cc0033', '#800020', '#e6004c'];
            for (let i = 0; i < 45; i++) {
                customPetals.push({
                    x: Math.random() * fxCanvas.width,
                    y: -20 - Math.random() * 80,
                    size: Math.random() * 10 + 9,
                    color: shades[Math.floor(Math.random() * shades.length)],
                    speedY: Math.random() * 2.5 + 2,
                    wobble: Math.random() * 5,
                    rotation: Math.random() * Math.PI,
                    rotSpeed: (Math.random() - 0.5) * 0.08
                });
            }
        }

        function send3DLoveHearts() {
            for (let i = 0; i < 30; i++) {
                customHearts.push({
                    x: Math.random() * fxCanvas.width,
                    y: -20 - Math.random() * 60,
                    size: Math.random() * 14 + 18,
                    speedY: Math.random() * 3 + 2,
                    wobble: Math.random() * 5
                });
            }
        }

        function launchGrandFireworks() {
            let count = 0;
            let fireInterval = setInterval(() => {
                confetti({ particleCount: 120, spread: 100, origin: { x: 0.2 + Math.random() * 0.6, y: 0.2 + Math.random() * 0.4 }, colors: ['#ffd700', '#ff007f', '#00f2fe', '#ffffff', '#ffaa00'] });
                count++;
                if (count >= 4) clearInterval(fireInterval);
            }, 300);
        }

,       if (window.Telegram && window.Telegram.WebApp) {
            window.Telegram.WebApp.ready();
            window.Telegram.WebApp.expand();
        }

        loadSurpriseData();
    </script>
</body>
</html>
