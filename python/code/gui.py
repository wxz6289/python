from tkinter import *
from tkinter.scrolledtext import ScrolledText

def load():
  print(filename.get(), 'filename')
  with open(filename.get()) as file:
    print('open')
    content.delete('1.0', END)
    content.insert(INSERT, file.read())

def save():
  with open(filename.get(), 'w') as file:
    print("save")
    file.write(content.get('1.0', END))

top = Tk()
top.title("Simple Editor")

content = ScrolledText()
content.pack(side=BOTTOM, expand=True, fill=BOTH)

filename = Entry()
filename.pack(side=LEFT, expand=True, fill=X)

Button(text='Open', command=load).pack(side=LEFT)

btn = Button()
btn['text'] = "Save"
btn["command"] = save
btn.pack(side=LEFT)

mainloop()