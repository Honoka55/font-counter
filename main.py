import tkinter as tk
from tkinter import filedialog
from fontTools.ttLib import TTFont
import os

def open_font():
    file_path = filedialog.askopenfilename(defaultextension=".ttf",
                                           filetypes=[("Font", "*.ttf *.otf"),
                                                      ("All Files", "*.*")])
    if file_path:
        font = TTFont(file_path)
        characters = font['cmap'].getBestCmap().keys()
        valid_characters = set()
        with open('Unicode/UnicodeData.txt', 'r') as f:
            lines = f.readlines()
            index = 0
            while index < len(lines):
                line = lines[index].strip()
                if '<control>' in line or not line:
                    index += 1
                    continue
                if ', First>' in line:
                    start = int(line.split(';')[0], 16)
                    end_line = lines[index + 1].strip()
                    end = int(end_line.split(';')[0], 16)
                    valid_characters.update(range(start, end + 1))
                    index += 2
                else:
                    code = int(line.split(';')[0], 16)
                    valid_characters.add(code)
                    index += 1
        blocks_info = {}
        with open('Unicode/Blocks.txt', 'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                start, end = line.split('; ')[0].split('..')
                name = line.split('; ')[1].rstrip()
                start, end = int(start, 16), int(end, 16)
                blocks_info[name] = (start, end - start + 1, 0, 0)
        for code in characters:
            for block, (start, total, count, invalid) in blocks_info.items():
                end = start + total - 1
                if start <= code <= end:
                    count += 1
                    if code not in valid_characters:
                        count -= 1
                        invalid += 1
                    blocks_info[block] = (start, total, count, invalid)
        for block, (start, total, count, invalid) in blocks_info.items():
            total = len(valid_characters & set(range(start, start + total)))
            blocks_info[block] = (start, total, count, invalid)
        unicode_text_box.delete(1.0, tk.END)
        for block, (start, total, count, invalid) in blocks_info.items():
            if count > 0:
                if invalid > 0:
                    unicode_text_box.insert(
                        tk.END, f'{block}: {count}({invalid}!)/{total}\n')
                else:
                    unicode_text_box.insert(
                        tk.END, f'{block}: {count}/{total}\n')
        custom_text_box.delete(1.0, tk.END)
        for filename in os.listdir('Custom'):
            if filename.endswith('.txt'):
                with open(os.path.join('Custom', filename), 'r', encoding='utf-8') as f:
                    content = f.read()
                    count = 0
                    for char in content:
                        if ord(char) in characters:
                            count += 1
                    custom_text_box.insert(
                        tk.END, f'{os.path.splitext(filename)[0]}: {count}/{len(content)}\n')
        file_name_label.config(text=file_path)


root = tk.Tk()
root.title('Font Counter')
root.resizable(False, False)

open_button = tk.Button(root, text='Open', command=open_font)
open_button.grid(row=0, column=0, columnspan=3, pady=10)

file_name_label = tk.Label(root, text='')
file_name_label.grid(row=1, column=0, columnspan=3)

unicode_label = tk.Label(root, text='Unicode')
unicode_label.grid(row=2, column=0, padx=10)

unicode_text_box = tk.Text(root, width=50, height=40)
unicode_text_box.grid(row=3, column=0, padx=10)

unicode_scroll_y = tk.Scrollbar(root, orient='vertical',
                        command=unicode_text_box.yview)
unicode_scroll_y.grid(row=3, column=1, sticky='ns')
unicode_text_box.config(yscrollcommand=unicode_scroll_y.set)

custom_label = tk.Label(root, text='Custom')
custom_label.grid(row=2, column=2, padx=10)

custom_text_box = tk.Text(root, width=50, height=40)
custom_text_box.grid(row=3, column=2, padx=10)

custom_scroll_y = tk.Scrollbar(root, orient='vertical',
                         command=custom_text_box.yview)
custom_scroll_y.grid(row=3, column=3, sticky='ns')
custom_text_box.config(yscrollcommand=custom_scroll_y.set)

root.mainloop()
