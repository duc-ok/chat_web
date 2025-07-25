from flask import Flask, request, render_template
import json
import random
import os

app = Flask(__name__)

# Load dữ liệu từ file JSON
with open("kienthuc.json", "r", encoding="utf-8") as f:
    data = json.load(f)

@app.route("/", methods=["GET", "POST"])
def index():
    ketqua = ""
    if request.method == "POST":
        noidung = request.form["noidung"].lower().strip()
        if noidung in data:
            ketqua = random.choice(data[noidung])
        else:
            ketqua = "Xin lỗi, tôi chưa hiểu. Bạn có thể hỏi lại câu khác?"
    return render_template("index.html", ketqua=ketqua)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Để Render tự cấp cổng
    app.run(host="0.0.0.0", port=port)


@app.route("/hoi", methods=["POST"])
def hoi():
    user_text = request.json.get("cau_hoi")
    reply = tra_loi(user_text)
    return jsonify({"tra_loi": reply})

if __name__ == "__main__":
    app.run(debug=True)
