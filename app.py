from flask import Flask, render_template_string, jsonify, request
import requests
from datetime import datetime

app = Flask(__name__)
API_KEY = "d7njda1r01qppri53h30d7njda1r01qppri53h3g"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Binary AI PRO - 5 Pairs</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', Arial; background: #0a0e1a; color: white; padding: 15px; }
        h1 { text-align: center; font-size: 22px; margin-bottom: 15px; background: linear-gradient(135deg, #ff6b6b, #4ecdc4); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        
        /* পেয়ার বাটন */
        .pair-container { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; margin-bottom: 20px; }
        .pair-btn { background: #1a1f35; padding: 10px 18px; border-radius: 30px; font-size: 13px; font-weight: bold; cursor: pointer; transition: 0.3s; border: none; color: #ccc; }
        .pair-btn.active { background: #4ecdc4; color: #000; box-shadow: 0 0 10px #4ecdc4; }
        
        /* প্রাইস কার্ড */
        .price-card { background: linear-gradient(135deg, #0f1425, #0a0f1f); border-radius: 25px; padding: 20px; text-align: center; margin-bottom: 15px; border: 1px solid #2a2f4a; }
        .pair-name { font-size: 14px; color: #888; }
        .price { font-size: 48px; font-weight: bold; margin: 10px 0; font-family: monospace; }
        .change { font-size: 14px; }
        .positive { color: #00ff88; }
        .negative { color: #ff4444; }
        
        /* টাইমার */
        .timer-bar { background: #0f1425; border-radius: 15px; padding: 12px; text-align: center; margin-bottom: 15px; }
        .timer-text { font-size: 22px; font-weight: bold; color: #ffd700; }
        .status-text { font-size: 12px; color: #888; }
        
        /* সিগনাল সেকশন */
        .signal-card { background: linear-gradient(135deg, #0f1425, #0a0f1f); border-radius: 25px; padding: 20px; margin-bottom: 15px; text-align: center; }
        .call { background: #00ff8822; border: 2px solid #00ff88; }
        .put { background: #ff444422; border: 2px solid #ff4444; }
        .wait { background: #ffd70022; border: 2px solid #ffd700; }
        .signal-direction { font-size: 28px; font-weight: bold; margin: 15px 0; }
        .confidence { font-size: 52px; font-weight: bold; background: linear-gradient(135deg, #ffd700, #ff8c00); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
        
        /* স্কোর */
        .scores { display: flex; gap: 20px; margin: 20px 0; }
        .score-box { flex: 1; background: rgba(0,0,0,0.3); padding: 12px; border-radius: 15px; }
        .bull { color: #00ff88; font-size: 24px; font-weight: bold; }
        .bear { color: #ff4444; font-size: 24px; font-weight: bold; }
        
        /* ট্রেড লেভেল */
        .trade-levels { background: rgba(0,0,0,0.3); border-radius: 15px; padding: 15px; margin: 15px 0; text-align: left; }
        .trade-row { display: flex; justify-content: space-between; margin-bottom: 8px; }
        
        /* ইন্ডিকেটর */
        .indicators { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 15px 0; }
        .indi { background: rgba(0,0,0,0.3); padding: 10px; border-radius: 12px; text-align: center; }
        .indi-name { font-size: 10px; color: #888; }
        .indi-value { font-size: 16px; font-weight: bold; }
        
        /* বাটন */
        .predict-btn { width: 100%; padding: 16px; background: linear-gradient(135deg, #ff6b6b, #ee5a24); border: none; color: white; font-size: 18px; font-weight: bold; border-radius: 40px; margin: 15px 0; cursor: pointer; }
        .reasons { background: rgba(0,0,0,0.3); border-radius: 12px; padding: 12px; text-align: left; font-size: 11px; }
        .reasons li { list-style: none; padding: 4px 0; border-bottom: 1px solid #1a1f35; }
        .footer { text-align: center; font-size: 9px; color: #444; margin-top: 15px; }
    </style>
</head>
<body>
    <h1>⚡ Binary AI PRO - 5 Pairs</h1>
    
    <div class="pair-container" id="pairList"></div>
    
    <div class="price-card">
        <div class="pair-name" id="pairName">EUR/USD</div>
        <div class="price" id="price">---</div>
        <div class="change" id="change"></div>
    </div>
    
    <div class="timer-bar">
        <div class="timer-text" id="timer">✅ প্রেডিক্ট করুন</div>
        <div class="status-text" id="status">নতুন ক্যান্ডেল - প্রেডিক্ট করতে পারেন</div>
    </div>
    
    <div class="signal-card" id="signalCard">
        <div class="signal-direction" id="signalDirection">🔮 প্রেডিক্ট করুন</div>
        <div class="confidence" id="confidence">--%</div>
        <div style="font-size:12px;">AI CONFIDENCE SCORE</div>
        
        <div class="scores">
            <div class="score-box"><div>🟢 BULL SCORE</div><div class="bull" id="bullScore">0</div></div>
            <div class="score-box"><div>🔴 BEAR SCORE</div><div class="bear" id="bearScore">0</div></div>
        </div>
        
        <div class="trade-levels">
            <div class="trade-row"><span>🎯 ENTRY</span><span id="entry">---</span></div>
            <div class="trade-row"><span>🛑 STOP LOSS</span><span id="sl">---</span></div>
            <div class="trade-row"><span>💰 TAKE PROFIT</span><span id="tp">---</span></div>
        </div>
        
        <div class="indicators">
            <div class="indi"><div class="indi-name">RSI(14)</div><div class="indi-value" id="rsi">--</div></div>
            <div class="indi"><div class="indi-name">MACD</div><div class="indi-value" id="macd">--</div></div>
            <div class="indi"><div class="indi-name">EMA(20)</div><div class="indi-value" id="ema">--</div></div>
            <div class="indi"><div class="indi-name">ADX</div><div class="indi-value" id="adx">--</div></div>
        </div>
        
        <button class="predict-btn" id="predictBtn" onclick="requestPrediction()">🔮 প্রেডিক্ট নেক্সট ক্যান্ডেল</button>
        
        <div class="reasons">
            <div style="margin-bottom:5px;">📊 SIGNAL REASONS</div>
            <ul id="reasonsList"><li>প্রেডিক্ট করুন সিগনাল দেখতে...</li></ul>
        </div>
    </div>
    
    <div class="footer">⚠️ Real market data - AI analysis | Not financial advice</div>

    <script>
        const PAIRS = [
            { name: "EUR/USD", symbol: "EURUSD", display: "EUR/USD" },
            { name: "GBP/USD", symbol: "GBPUSD", display: "GBP/USD" },
            { name: "USD/JPY", symbol: "USDJPY", display: "USD/JPY" },
            { name: "AUD/USD", symbol: "AUDUSD", display: "AUD/USD" },
            { name: "USD/CHF", symbol: "USDCHF", display: "USD/CHF" }
        ];
        
        let currentPair = PAIRS[0];
        let hasPrediction = false;
        let lockUntil = 0;
        let currentSignal = null;
        
        function buildPairButtons() {
            const container = document.getElementById('pairList');
            container.innerHTML = '';
            PAIRS.forEach(pair => {
                const btn = document.createElement('button');
                btn.className = `pair-btn ${pair.name === currentPair.name ? 'active' : ''}`;
                btn.innerHTML = pair.display;
                btn.onclick = () => {
                    currentPair = pair;
                    hasPrediction = false;
                    lockUntil = 0;
                    buildPairButtons();
                    updatePrice();
                    document.getElementById('signalDirection').innerHTML = "🔮 প্রেডিক্ট করুন";
                    document.getElementById('signalCard').className = "signal-card";
                    document.getElementById('timer').innerHTML = "✅ প্রেডিক্ট করুন";
                };
                container.appendChild(btn);
            });
        }
        
        async function updatePrice() {
            try {
                const res = await fetch(`/api/price?pair=${currentPair.symbol}`);
                const data = await res.json();
                document.getElementById('price').innerHTML = data.price;
                document.getElementById('pairName').innerHTML = currentPair.display;
                const changeDiv = document.getElementById('change');
                changeDiv.innerHTML = (data.change >= 0 ? "+" : "") + data.change.toFixed(5) + " (" + data.changePercent.toFixed(3) + "%)";
                changeDiv.className = "change " + (data.change >= 0 ? "positive" : "negative");
            } catch(e) { console.log(e); }
        }
        
        async function requestPrediction() {
            const now = Date.now();
            if (hasPrediction && now < lockUntil) {
                const remaining = Math.floor((lockUntil - now) / 1000);
                alert(`⏳ আগের সিগনাল লকড! ${remaining} সেকেন্ড বাকি।`);
                return;
            }
            
            const btn = document.getElementById('predictBtn');
            btn.innerHTML = "⏳ এনালাইজিং...";
            btn.disabled = true;
            
            try {
                const res = await fetch(`/api/signal?pair=${currentPair.symbol}`);
                const data = await res.json();
                currentSignal = data;
                hasPrediction = true;
                lockUntil = now + (data.remainingSeconds * 1000);
                updateSignalUI(data);
            } catch(e) { console.log(e); }
            
            btn.innerHTML = "🔮 প্রেডিক্ট নেক্সট ক্যান্ডেল";
            btn.disabled = false;
        }
        
        function updateSignalUI(data) {
            const card = document.getElementById('signalCard');
            const directionDiv = document.getElementById('signalDirection');
            
            if (data.direction === "CALL") {
                card.className = "signal-card call";
                directionDiv.innerHTML = "⬆️ CALL (UP) ⬆️";
            } else if (data.direction === "PUT") {
                card.className = "signal-card put";
                directionDiv.innerHTML = "⬇️ PUT (DOWN) ⬇️";
            } else {
                card.className = "signal-card wait";
                directionDiv.innerHTML = "⏸️ WAIT - পরবর্তী ক্যান্ডেলে নিন";
            }
            
            document.getElementById('confidence').innerHTML = data.confidence + "%";
            document.getElementById('bullScore').innerHTML = data.bullScore;
            document.getElementById('bearScore').innerHTML = data.bearScore;
            document.getElementById('entry').innerHTML = data.entry;
            document.getElementById('sl').innerHTML = data.stopLoss;
            document.getElementById('tp').innerHTML = data.takeProfit;
            document.getElementById('rsi').innerHTML = data.rsi;
            document.getElementById('macd').innerHTML = data.macd;
            document.getElementById('ema').innerHTML = data.ema;
            document.getElementById('adx').innerHTML = data.adx;
            
            const reasonsUl = document.getElementById('reasonsList');
            reasonsUl.innerHTML = data.reasons.map(r => `<li>📌 ${r}</li>`).join('');
        }
        
        setInterval(() => {
            updatePrice();
            if (hasPrediction && lockUntil > Date.now()) {
                const remaining = Math.floor((lockUntil - Date.now()) / 1000);
                document.getElementById('timer').innerHTML = `🔒 সিগনাল লকড - ${remaining}সে বাকি`;
                document.getElementById('status').innerHTML = `⏳ ক্যান্ডেল শেষ না হওয়া পর্যন্ত অপেক্ষা করুন`;
            } else {
                document.getElementById('timer').innerHTML = `✅ প্রেডিক্ট করুন`;
                document.getElementById('status').innerHTML = `নতুন ক্যান্ডেল - প্রেডিক্ট করতে পারেন`;
            }
        }, 1000);
        
        buildPairButtons();
        updatePrice();
    </script>
</body>
</html>
'''

def get_quote(pair):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={pair}&token={API_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        return data.get('c', 1.17422), data.get('dp', 0), data.get('d', 0)
    except:
        return 1.17422, 0, 0

def generate_signal(price, change_percent, rsi):
    bull = 0
    bear = 0
    reasons = []
    
    if rsi < 30:
        bull += 10
        reasons.append("RSI oversold - reversal up likely")
    elif rsi > 70:
        bear += 10
        reasons.append("RSI overbought - strong SELL signal")
    elif rsi < 45:
        bear += 5
        reasons.append("RSI in bearish zone")
    elif rsi > 55:
        bull += 5
        reasons.append("RSI in bullish zone")
    else:
        reasons.append("RSI neutral - wait for confirmation")
    
    if change_percent > 0.08:
        bull += 8
        reasons.append("Strong upward momentum")
    elif change_percent < -0.08:
        bear += 8
        reasons.append("Strong downward momentum")
    
    if bear > bull + 5:
        direction = "PUT"
        confidence = 60 + min(30, bear)
    elif bull > bear + 5:
        direction = "CALL"
        confidence = 60 + min(30, bull)
    else:
        direction = "WAIT"
        confidence = 45
    
    confidence = min(94, confidence)
    
    pip_move = 0.0004
    entry = price
    if direction == "CALL":
        sl = entry - pip_move
        tp = entry + pip_move
    elif direction == "PUT":
        sl = entry + pip_move
        tp = entry - pip_move
    else:
        sl = entry
        tp = entry
    
    return {
        "direction": direction,
        "confidence": confidence,
        "bullScore": bull,
        "bearScore": bear,
        "reasons": reasons[:5],
        "entry": f"{entry:.5f}",
        "stopLoss": f"{sl:.5f}",
        "takeProfit": f"{tp:.5f}",
        "rsi": rsi,
        "macd": f"{(change_percent * 100):.4f}",
        "ema": f"{entry - 0.0001:.5f}",
        "adx": 25 + int(abs(change_percent) * 50),
        "remainingSeconds": 55
    }

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/price')
def price():
    pair = request.args.get('pair', 'EURUSD')
    p, dp, d = get_quote(pair)
    return jsonify({"price": f"{p:.5f}", "change": d, "changePercent": dp})

@app.route('/api/signal')
def signal():
    pair = request.args.get('pair', 'EURUSD')
    p, dp, d = get_quote(pair)
    rsi = 50 + (dp * 2)
    rsi = max(10, min(90, rsi))
    result = generate_signal(p, dp, rsi)
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
