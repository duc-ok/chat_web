from flask import Flask, request, jsonify, render_template
import json, random, datetime
from difflib import get_close_matches
from unidecode import unidecode
from deep_translator import GoogleTranslator
import os

app = Flask(__name__)

def chuan_hoa(text):
    return unidecode(text.lower().strip())

def load_kienthuc():
    if os.path.exists("kienthuc.json"):
        with open("kienthuc.json", "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {}

def luu_kienthuc():
    with open("kienthuc.json", "w", encoding="utf-8") as f:
        json.dump(kienthuc, f, ensure_ascii=False, indent=2)

kienthuc = load_kienthuc()

def tim_y_dinh(cau_hoi):
    cau_hoi = chuan_hoa(cau_hoi)
    danh_sach_pattern = []
    mapping_pattern_y_dinh = {}

    for y_dinh, noi_dung in kienthuc.items():
        for pattern in noi_dung["patterns"]:
            pattern_chuan = chuan_hoa(pattern)
            danh_sach_pattern.append(pattern_chuan)
            mapping_pattern_y_dinh[pattern_chuan] = y_dinh
            if cau_hoi == pattern_chuan:
                return y_dinh

    khop = get_close_matches(cau_hoi, danh_sach_pattern, n=1, cutoff=0.8)
    if khop:
        return mapping_pattern_y_dinh[khop[0]]

    for pattern_chuan in danh_sach_pattern:
        if pattern_chuan in cau_hoi or cau_hoi in pattern_chuan:
            return mapping_pattern_y_dinh[pattern_chuan]

    return None

def tra_loi(cau_hoi):
    try:
        cau_hoi = GoogleTranslator(source='auto', target='vi').translate(cau_hoi)
    except:
        pass

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

@app.route("/hoc", methods=["POST"])
def hoc():
    du_lieu = request.json
    khoa = chuan_hoa(du_lieu.get("khoa", ""))
    pattern = chuan_hoa(du_lieu.get("pattern", ""))
    response = du_lieu.get("response", "")

    if not khoa or not pattern or not response:
        return jsonify({"thong_bao": "❌ Vui lòng nhập đầy đủ từ khóa, pattern và câu trả lời."})

    if khoa in kienthuc:
        if pattern not in kienthuc[khoa]["patterns"]:
            kienthuc[khoa]["patterns"].append(pattern)
        kienthuc[khoa]["responses"].append(response)
    else:
        kienthuc[khoa] = {
            "patterns": [pattern],
            "responses": [response]
        }

    luu_kienthuc()
    return jsonify({"thong_bao": "✅ Tôi đã học kiến thức mới!"})

if __name__ == "__main__":
    app.run(debug=True, port=10000, host='0.0.0.0')
