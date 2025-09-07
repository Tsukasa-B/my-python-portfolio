# unit_converter.py

#１インチが何mmかを変数に入れておく
INCH_TO_MM = 25.4                           # 定数の変数名は大文字

# 変換したいミリメートル
mm_value = 10.0

# ミリメートルをインチに変換する計算
inch_value = mm_value / INCH_TO_MM

# 結果を表示する
# f-string (f"...")を使うと，文字列の中に変数を埋め込めて便利
print(f"{mm_value} mm は {inch_value} インチです．")        # f-stringという書き方