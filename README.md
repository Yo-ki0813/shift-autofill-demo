# Shift Autofill Demo
シフトキャンセルが発生したとき、自動で代替ヘルパーを選定する Python デモ  
Python demo that automatically selects a substitute helper when a shift is cancelled.

---

## 📂 ファイル構成 / File Structure
- `shift_replace.py` : メインプログラム / Main script  
- `shifts.csv` : 入力データ（現在のシフト一覧）/ Input data (current shifts)  
- `選考過程.csv` : 実行後に出力される、補充候補のスコア・理由 / Output: selection trace with scores & reasons  
- `更新後シフト.csv` : 実行後に出力される、補充済みの最終シフト / Output: updated shifts after substitution  

---

## ⚙️ 実行方法 / How to Run

### 前提 / Prerequisites
- macOS or Windows  
- Python 3.10+ がインストールされていること  
- Python 3.10+ installed  

### 手順 / Steps
1. このリポジトリをクローン / Clone this repo  
   ```bash
   git clone https://github.com/Yo-ki0813/shift-autofill-demo.git
   cd shift-autofill-demo
