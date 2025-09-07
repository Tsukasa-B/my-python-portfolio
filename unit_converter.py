# # unit_converter.py

# #１インチが何mmかを変数に入れておく
INCH_TO_MM = 25.4                           # 定数の変数名は大文字

# 単位と数値を一緒に入力してもらう
user_input = input("変換したい数値を単位と一緒に入力してください (例: 50mm, 2inch): ")

# 入力を扱いやすいように，すべて小文字に変換する
input_lower = user_input.lower()

# もし入力が "mm" で終わっていたら
if input_lower.endswith('mm'):
    # "mm"の部分を取り除いて数値だけにする（例: "50mm" -> "50")
    value_str = input_lower.replace('mm', '')

    # 文字列を数値に変換して計算
    mm_value = float(value_str)
    inch_value = mm_value / INCH_TO_MM
    print(f"{mm_value} mm は {inch_value:.4f} インチです．")

# そうではなく，もし入力が"inch"で終わっていたら
elif input_lower.endswith('inch') :
    # "inch"の部分を取り除いて数値だけにする（例: "2inch" -> "2")
    value_str = input_lower.replace('inch', '')

    # 文字列を数値に変換して計算
    inch_value = float(value_str)
    mm_value = inch_value / INCH_TO_MM
    print(f"{inch_value} inch は {mm_value:.4f} ミリメートルです．")

# 上のどちらの条件にも当てはまらなかったら
else :
    print("エラー: 'mm' または 'inch' を単位として指定してください")