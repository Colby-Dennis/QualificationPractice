from tkinter import *

root = Tk()

# Creating the label widget
myLabel1 = Label(root, text="Label One")
myLabel2 = Label(root, text="Label Two")

# Putting it in the window (pack)
myLabel1.grid(row=0, column=0)
myLabel2.grid(row=0, column=1)

# Event loop
root.mainloop()