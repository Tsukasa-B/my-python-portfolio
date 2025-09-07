import datetime 
import tkinter as tk
import tkinter.messagebox
import tkinter.font as tkfont

def show_current_time():
    now = datetime.datetime.now()
    tkinter.messagebox.showinfo('現在の日付と時刻', f'現在の日付と時刻: \n{now}')

def main():
    #メインウインドウの作成
    root = tk.Tk()
    root.title("時刻表示プログラム")
    root.geometry("300x150")  #ウィンドウの設定サイズ

    # フォントの定義
    # システムにインストールされている日本語フォントを指定
    # 例: メイリオ, Yu Gothic, Hiragino Kaku Gothic ProNなど
    japanese_font = tkfont.Font(family="メイリオ", size=12)

    # ボタンの作成
    label = tk.Label(root, text="下のボタンをクリックしてください", font=japanese_font)
    label.pack(pady=10)

    button = tk.Button(root, text="時刻を表示", command=show_current_time, font=japanese_font)
    button.pack(pady=10)

    #ウィンドウの実行
    root.mainloop()

if __name__ == '__main__':
    main()