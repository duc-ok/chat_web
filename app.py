from flask import Flask, render_template, request, jsonify
import json, random, datetime
from unidecode import unidecode
from difflib import get_close_matches
import os

app = Flask(__name__)

def chuan_hoa(text):
    return unidecode(text.lower().strip())

def load_kienthuc():
    with open("kienthuc.json", "r", encoding="utf-8") as f:
        return json.load(f)

def save_kienthuc(kienthuc):
    with open("kienthuc.json", "w", encoding="utf-8") as f:
        json.dump(kienthuc, f, ensure_ascii=False, indent=4)

kienthuc = load_kienthuc()

def tim_y_dinh(cau_hoi):
    cau_hoi = chuan_hoa(cau_hoi)
    all_patterns = {}
    for y_dinh, noi_dung in kienthuc.items():
        for pattern in noi_dung["patterns"]:
            all_patterns[pattern] = y_dinh
    matched = get_close_matches(cau_hoi, all_patterns.keys(), n=1, cutoff=0.6)
    return all_patterns[matched[0]] if matched else None

def tra_loi(cau_hoi):
    cau_hoi = chuan_hoa(cau_hoi)
    if "ngay" in cau_hoi:
        return f"Hôm nay là {datetime.datetime.today().strftime('%A, %d/%m/%Y')}"
    if any(x in cau_hoi for x in ["gio", "thoi gian", "may gio"]):
        return f"Bây giờ là {datetime.datetime.now().strftime('%H:%M:%S')}"
    y_dinh = tim_y_dinh(cau_hoi)
    if y_dinh:
        return random.choice(kienthuc[y_dinh]["responses"])
    return "🤔 Tôi chưa hiểu rõ. Bạn có thể hỏi lại hoặc dạy tôi không?"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/hoi", methods=["POST"])
def hoi():
    user_text = request.json.get("cau_hoi")
    reply = tra_loi(user_text)
    return jsonify({"tra_loi": reply})

@app.route("/them", methods=["POST"])
def them():
    du_lieu = request.json
    tu_khoa = chuan_hoa(du_lieu.get("tu_khoa", ""))
    pattern = chuan_hoa(du_lieu.get("pattern", ""))
    response = du_lieu.get("response", "")

    if not tu_khoa or not pattern or not response:
        return jsonify({"message": "❌ Thiếu thông tin!"}), 400

    if tu_khoa in kienthuc:
        if pattern not in kienthuc[tu_khoa]["patterns"]:
            kienthuc[tu_khoa]["patterns"].append(pattern)
        if response not in kienthuc[tu_khoa]["responses"]:
            kienthuc[tu_khoa]["responses"].append(response)
    else:
        kienthuc[tu_khoa] = {
            "patterns": [pattern],
            "responses": [response]
        }

    save_kienthuc(kienthuc)
    return jsonify({"message": "✅ Đã thêm kiến thức!"})

if __name__ == "__main__":
    app.run(debug=True)


@app.route("/hoi", methods=["POST"])
def hoi():
    user_text = request.json.get("cau_hoi")
    print("Người dùng hỏi:", user_text)
    reply = tra_loi(user_text)
    return jsonify({"tra_loi": reply})

if __name__ == "__main__":
    app.run(debug=True)
