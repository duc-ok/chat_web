from flask import Flask, request, jsonify, render_template
import json, random, datetime
from difflib import get_close_matches
from unidecode import unidecode
from deep_translator import GoogleTranslator

app = Flask(__name__)

def chuan_hoa(text):
    return unidecode(text.lower().strip())

def load_kienthuc():
    with open("kienthuc.json", "r", encoding="utf-8") as f:
        return json.load(f)

kienthuc = load_kienthuc()

def tim_y_dinh(cau_hoi):
    cau_hoi = chuan_hoa(cau_hoi)
    for y_dinh, noi_dung in kienthuc.items():
        for pattern in noi_dung["patterns"]:
            if cau_hoi == chuan_hoa(pattern):
                return y_dinh
    return None
def tra_loi(cau_hoi):
    try:
        # Dịch sang tiếng Việt trước
        cau_hoi = GoogleTranslator(source='auto', target='vi').translate(cau_hoi)
    except:
        pass  # nếu lỗi vẫn dùng nguyên câu hỏi

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
    print("Người dùng hỏi:", user_text)
    reply = tra_loi(user_text)
    return jsonify({"tra_loi": reply})

if __name__ == "__main__":
    app.run(debug=True, port=10000, host='0.0.0.0')
