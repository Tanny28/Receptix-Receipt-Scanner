# 📄 Receptix – Smart Receipt Scanner & Expense Categorizer

**Receptix** is an intelligent OCR-based Python application that scans physical or digital receipts, extracts itemized data using Tesseract OCR, and categorizes expenses automatically. It features a simple, clean GUI built with **Tkinter**, and organizes data into categories like Food, Office, Entertainment, etc.

> 🔍 Upload a receipt → 🧠 OCR & categorize → 📊 Save and analyze your expense report!

---

## 🚀 Features

- ✅ **OCR Receipt Scanning** using Tesseract (`pytesseract`)
- ✅ **Smart Preprocessing** with OpenCV for better accuracy
- ✅ **Tkinter GUI** – clean, interactive, beginner-friendly
- ✅ **Automatic Categorization** using keyword matching
- ✅ **Detailed Expense Reports** with per-category breakdown
- ✅ **Save Reports** locally with timestamped files
- ✅ **Logging** and validation system

---


## 🧰 Technologies Used

| Module         | Purpose                                      |
|----------------|----------------------------------------------|
| `pytesseract`  | OCR engine wrapper (Tesseract)               |
| `OpenCV`       | Image preprocessing for improved OCR results |
| `Tkinter`      | GUI for image upload & results display       |
| `Pillow`       | Image enhancement (sharpening/contrast)      |
| `Regex`        | Amount and item extraction from text         |
| `logging`      | Logs events, errors, and OCR data            |

---

## 📁 Folder Structure
receptix_gui/
├── main_gui.py # GUI application
├── ocr_utils.py # OCR and image preprocessing
├── categorizer.py # Amount parsing and categorization logic
├── requirements.txt # Dependencies
├── README.md # You're reading it!
├── UserGuide.pdf # How-to-use manual
├── assets/ # Sample receipt images/screenshots
├── logs/ # Auto-generated logs
└── reports/ # Saved expense reports


---

## 📦 Installation

### 🔧 Prerequisites
- Python 3.8+
- Tesseract OCR installed (Windows users: [Install here](https://github.com/UB-Mannheim/tesseract/wiki))

---

### ✅ 1. Clone the Repository

```bash
git clone https://github.com/Tanny28/Receptix-Receipt-Scanner.git
cd Receptix-Receipt-Scanner

Star This Repo!
If you found this project useful or interesting, please ⭐️ star the repo to support the developer!


📬 Feedback
Feel free to open an issue or reach out for suggestions and improvements.

---


