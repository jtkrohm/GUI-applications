import tkinter as tk
from tkinter import filedialog

# Create a new tkinter window
root = tk.Tk()

# Create a Text widget that will be used as the text editor
text_editor = tk.Text(root)
text_editor.pack()

def open_file():
    # Use a dialog to let the user open a file
    filepath = filedialog.askopenfilename()
    with open(filepath, 'r') as file:
        # Delete the current contents of the text editor
        text_editor.delete('1.0', tk.END)
        # Insert the contents of the file into the text editor
        text_editor.insert(tk.END, file.read())

def save_file():
    # Use a dialog to let the user save a file
    filepath = filedialog.asksaveasfilename()
    with open(filepath, 'w') as file:
        # Write the contents of the text editor to the file
        file.write(text_editor.get('1.0', tk.END))

# Create a Menu widget
menu = tk.Menu(root)
root.config(menu=menu)

# Add an "Open" command to the menu
file_menu = tk.Menu(menu)
menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open", command=open_file)

# Add a "Save" command to the menu
file_menu.add_command(label="Save", command=save_file)

# Run the tkinter event loop
root.mainloop()
