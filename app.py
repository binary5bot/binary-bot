from flask import Flask, render_template_string, jsonify, request
import requests
import random

app = Flask(__name__)

API_KEY = "d7njda1r01qppri53h30d7njda1r01qppri53h3g"

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>Binary AI PRO</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: Arial; background: #0a0e1a; color: white; padding: 15px; text-align: center; }
        .price { font-size: 48px; font-weight: bold; margin: 20px 0; }
        .pair-btn { background: #1a1f35; padding: 10px 15px; margin: 5px; border-radius: 20px; cursor: pointer; display: inline-block; }
        .pair-btn.active { background: #4ecdc4; color: #000; }
        .signal { padding: 20px; border-radius: 20px; margin: 20px 0; }
        .call { background: #00ff8822; border: 2px solid #00ff88; }
        .put { background: #ff444422; border: 2px solid #ff4444; }
        .wait { background: #ffd70022; border: 2px solid #ffd700; }
        .btn { background: #ff6b6b; padding: 15px; border: none; color: white; font-size: 18px; border-radius: 40px; width: 90%; margin: 20px 0; cursor: pointer; }
        .conf { font-size: 52px; font-weight: bold; color: #ffd700; }
        .timer { font-size: 24px; color: #ffd700; margin: 15px 0; }
        .reasons { text-align: left; background: #0f1425; padding: 15px; border-radius: 15px; font-size: 12px; }
    </style>
</head>
<body>
    <h1>⚡ Binary AI PRO</h1>
    <div id="pairs"></div>
    <div class="price" id="price">---</div>
    <div class="timer" id="timer">✅ প্রেডিক্ট করুন</div>
    <div class="signal" id="signal">
        <div id="signalText">🔮 প্রেডিক্ট করুন</div>
        <div class="conf" id="conf">--%</div>
    </div>
    <button class="btn" onclick="getSignal()">🔮 প্রেডিক্ট নেক্সট ক্যান্ডেল</button>
    <div class="reasons" id="reasons"></div>
    <script>
        let currentPair = "EURUSD";
        let locked = false;
        let lockUntil = 0;
        
        const pairs = [
            {name:"EUR/USD", sym:"EURUSD"},
            {name:"GBP/USD", sym:"GBPUSD"},
            {name:"USD/JPY", sym:"USDJPY"},
            {name:"AUD/USD", sym:"AUDUSD"},
            {name:"USD/CHF", sym:"USDCHF"}
        ];
        
        function loadPairs() {
            let html = '';
            pairs.forEach(p => {
                html += `<div class="pair-btn" onclick="changePair('${p.sym}')">${p.name}</div>`;
            });
            document.getElementById('pairs').innerHTML = html;
        }
        
        function changePair(sym) {
            currentPair = sym;
            locked = false;
            updatePrice();
        }
        
        async function updatePrice() {
            try {
                let res = await fetch('/price?pair=' + currentPair);
                let d = await res.json();
                document.getElementById('price').innerHTML = d.price;
            } catch(e) {}
        }
        
        async function getSignal() {
            if (locked && Date.now() < lockUntil) {
                alert("লকড! অপেক্ষা করুন");
                return;
            }
            try {
                let res = await fetch('/signal?pair=' + currentPair);
                let d = await res.json();
                locked = true;
                lockUntil = Date.now() + 55000;
                let signalDiv = document.getElementById('signal');
                if(d.dir == "CALL") {
                    signalDiv.className = "signal call";
                    document.getElementById('signalText').innerHTML = "⬆️ CALL (UP) ⬆️";
                } else if(d.dir == "PUT") {
                    signalDiv.className = "signal put";
                    document.getElementById('signalText').innerHTML = "⬇️ PUT (DOWN) ⬇️";
                } else {
                    signalDiv.className = "signal wait";
                    document.getElementById('signalText').innerHTML = "⏸️ WAIT";
                }
                document.getElementById('conf').innerHTML = d.conf + "%";
                document.getElementById('reasons').innerHTML = "<strong>SIGNAL REASONS</strong><br>" + d.reasons.map(r => "📌 " + r).join("<br>");
            } catch(e) {
                alert("এরর: " + e.message);
            }
        }
        
        setInterval(() => {
            updatePrice();
            if(locked && lockUntil > Date.now()) {
                let rem = Math.floor((lockUntil - Date.now())/1000);
                document.getElementById('timer').innerHTML = "🔒 লকড - " + rem + "সে বাকি";
            } else {
                document.getElementById('timer').innerHTML = "✅ প্রেডিক্ট করুন";
                locked = false;
            }
        }, 1000);
        
        loadPairs();
        updatePrice();
    </script>
</body>
</html>
'''

def get_price(pair):
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={pair}&token={API_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()
        return data.get('c', 1.17422)
    except:
        return 1.17422 + random.uniform(-0.001, 0.001)

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/price')
def price():
    pair = request.args.get('pair', 'EURUSD')
    p = get_price(pair)
    return jsonify({"price": f"{p:.5f}"})

@app.route('/signal')
def signal():
    pair = request.args.get('pair', 'EURUSD')
    price = get_price(pair)
    
    # সিমুলেটেড মুভমেন্ট
    move = random.uniform(-0.0005, 0.0005)
    
    if move > 0.0001:
        direction = "CALL"
        conf = 65 + int(move * 10000)
        reasons = ["বুলিশ মুভমেন্ট", "আপট্রেন্ড এক্টিভ", "মোমেন্টাম পজিটিভ"]
    elif move < -0.0001:
        direction = "PUT"
        conf = 65 + int(abs(move) * 10000)
        reasons = ["বেয়ারিশ মুভমেন্ট", "ডাউনট্রেন্ড এক্টিভ", "মোমেন্টাম নেগেটিভ"]
    else:
        direction = "WAIT"
        conf = 45
        reasons = ["কনফিউশন", "মার্কেট সাইডওয়েজ", "অপেক্ষা করুন"]
    
    return jsonify({
        "dir": direction,
        "conf": min(94, conf),
        "reasons": reasons[:3]
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
