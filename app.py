from flask import Flask, request, jsonify, render_template
from unidecode import unidecode
from difflib import get_close_matches
import json
import datetime
import random
import os

app = Flask(__name__)

def chuan_hoa(text):
    return unidecode(text.lower().strip())

def load_kienthuc():
    try:
        with open("kienthuc.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_kienthuc(kienthuc):
    with open("kienthuc.json", "w", encoding="utf-8") as f:
        json.dump(kienthuc, f, ensure_ascii=False, indent=2)

kienthuc = load_kienthuc()

def tim_y_dinh(cau_hoi):
    cau_hoi = chuan_hoa(cau_hoi)
    all_patterns = {}
    for y_dinh, noi_dung in kienthuc.items():
        for pattern in noi_dung.get("patterns", []):
            all_patterns[chuan_hoa(pattern)] = y_dinh
    matched = get_close_matches(cau_hoi, all_patterns.keys(), n=1, cutoff=0.6)
    return all_patterns[matched[0]] if matched else None

def tra_loi(cau_hoi):
    cau_hoi = chuan_hoa(cau_hoi)
    if "ngay" in cau_hoi:
        return f"Hôm nay là {datetime.datetime.today().strftime('%A, %d/%m/%Y')}"
    if any(x in cau_hoi for x in ["gio", "thoi gian", "mấy giờ", "mấy h"]):
        return f"Bây giờ là {datetime.datetime.now().strftime('%H:%M:%S')}"
    
    y_dinh = tim_y_dinh(cau_hoi)
    if y_dinh and y_dinh in kienthuc:
        return random.choice(kienthuc[y_dinh]["responses"])
    return "🤔 Tôi chưa hiểu rõ. Bạn có thể hỏi lại hoặc dạy tôi không?"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/hoi", methods=["POST"])
def hoi():
    user_text = request.json.get("cau_hoi", "")
    reply = tra_loi(user_text)
    return jsonify({"tra_loi": reply})

@app.route("/them_kienthuc", methods=["POST"])
def them_kienthuc():
    du_lieu = request.json
    y_dinh = chuan_hoa(du_lieu.get("y_dinh", ""))
    patterns = du_lieu.get("patterns", [])
    responses = du_lieu.get("responses", [])

    if not y_dinh or not patterns or not responses:
        return jsonify({"message": "❌ Thiếu thông tin để thêm."})

    if y_dinh in kienthuc:
        kienthuc[y_dinh]["patterns"].extend(patterns)
        kienthuc[y_dinh]["responses"].extend(responses)
    else:
        kienthuc[y_dinh] = {
            "patterns": patterns,
            "responses": responses
        }

    save_kienthuc(kienthuc)
    return jsonify({"message": "✅ Đã thêm kiến thức thành công."})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=True)
