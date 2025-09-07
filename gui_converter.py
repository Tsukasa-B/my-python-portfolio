# gui_converter.py

import tkinter as tk
from tkinter import ttk

INCH_TO_MM = 25.4

# --- ロジック部分（計算処理など） ---
def convert_unit():
    """入力欄の値を取得し、単位変換を実行して結果ラベルに表示する関数"""
    
    # 1. 入力欄(entry)からテキストを取得する
    user_input = entry.get()
    input_lower = user_input.lower()

    # try-exceptでエラー処理を行う
    try:
        if input_lower.endswith('mm'):
            value_str = input_lower.replace('mm', '')
            mm_value = float(value_str)
            inch_value = mm_value / INCH_TO_MM
            result_text = f"{mm_value} mm は {inch_value:.4f} インチです。"

        elif input_lower.endswith('inch'):
            value_str = input_lower.replace('inch', '')
            inch_value = float(value_str)
            mm_value = inch_value * INCH_TO_MM
            result_text = f"{inch_value} inch は {mm_value:.4f} ミリメートルです。"
        
        else:
            result_text = "エラー: 'mm' または 'inch' を指定してください。"
    
    except ValueError:
        result_text = "エラー: 数値を正しく入力してください。"

     # 2. 結果表示ラベル(result_label)のテキストを更新する
    result_label.config(text=result_text)

# ---GUIの組み立て部分---

# 1.メインウィンドウを作成
root = tk.Tk()      #クラス(tk.Tk())からインスタンスrootを作成
root.title("単位変換ツール")        # インスタンスの設計を変更．tk.Tk().title()だとクラスという設計方法に対する変更になってしまい，おかしい
root.geometry("400x150")

# 2.GUIの部品（ウィジェット）を作成
# -フレーム：ウィジェットをまとめるための容器
main_frame = ttk.Frame(root, padding=20)

#   - 入力欄(entry)
entry = ttk.Entry(main_frame, width=30)
entry.insert(0, "例: 50mm, 2inch")

#   -変換ボタン(button)
convert_button = ttk.Button(main_frame, text="変換実行", command=convert_unit)

#   -結果表示ラベル(Label)
result_label = ttk.Label(main_frame, text="ここに変換結果が表示されます")

# 3.ウィジェットをウィンドウに配置(レイアウト)
main_frame.pack(expand=True)
entry.pack(pady=5)
convert_button.pack(pady=10)
result_label.pack(pady=5)

root.mainloop()