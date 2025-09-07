# # unit_converter.py

# #１インチが何mmかを変数に入れておく
INCH_TO_MM = 25.4                           # 定数の変数名は大文字

# # 変換したいミリメートル
# mm_value = 10.0

# # ミリメートルをインチに変換する計算
# inch_value = mm_value / INCH_TO_MM

# # 結果を表示する
# # f-string (f"...")を使うと，文字列の中に変数を埋め込めて便利
# print(f"{mm_value} mm は {inch_value} インチです．")        # f-stringという書き方

# ユーザに入力を促すメッセージを表示し，入力された値を受け取る
input_str = input("変換したいミリメートルを入力してください")

# 入力された文字列を数値（浮動小数点）に変換する
mm_value = float(input_str)

# ミリメートルをインチに変換する計算
inch_value = mm_value / INCH_TO_MM

# 小数点以下の桁数を調整して見やすく表示する
# :.4fは「小数点以下４桁まで表示する」という意味
print(f"{mm_value} mm は {inch_value:.4f} インチです．")