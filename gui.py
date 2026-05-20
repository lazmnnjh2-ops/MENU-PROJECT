import customtkinter as ctk
from protocol import send_message, recv_message
import socket
import json

HOST = '127.0.0.1'
PORT = 5050

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
client_socket.recv(1024) 

def send_request(request):
    send_message(client_socket, request)

def receive_response():
    return recv_message(client_socket)

def show_list(title, items):
    win = ctk.CTkToplevel(root)
    win.title(title)
    win.geometry("300x400")
    text_box = ctk.CTkTextbox(win, width=280, height=380)
    text_box.pack(padx=10, pady=10)
    for item in items:
        text_box.insert("end", item + "\n")
    text_box.configure(state="disabled")

def show_categories():
    send_request("categories")
    categories = receive_response()
    show_list("Categories", categories)

def show_areas():
    send_request("areas")
    areas = receive_response()
    show_list("Areas", areas)

def show_ingredients():
    send_request("ingredients")
    ingredients = receive_response()
    show_list("Ingredients", ingredients)

def search_recipe():
    from tkinter.simpledialog import askstring
    from tkinter.messagebox import showinfo, askyesno

    name = askstring("Search Recipe", "Enter recipe name:")
    if not name:
        return
    send_request(f"search:{name}")
    recipes = receive_response()
    if recipes:
        output = "\n".join(f"{idx+1}. {rec['strMeal']}" for idx, rec in enumerate(recipes))
        choice = askstring("Select Recipe", f"{output}\nEnter number:")
        if choice and choice.isdigit():
            choice = int(choice)
            if 1 <= choice <= len(recipes):
                sel = recipes[choice-1]
                details = (
                    f"Name: {sel['strMeal']}\n"
                    f"Category: {sel['strCategory']}\n"
                    f"Area: {sel['strArea']}\n"
                    f"Instructions: {sel['strInstructions']}"
                )
                showinfo("Recipe Details", details)
                save = askyesno("Save Recipe", "Do you want to save this recipe?")
                if save:
                    send_request(f"save:{json.dumps(sel)}")
                    client_socket.recv(1024)
                    showinfo("Saved", "Recipe saved successfully!")
    else:
        showinfo("No Recipes", "No recipes found.")

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Stitch Recipe Discovery Hub")
root.geometry("500x550")

title_label = ctk.CTkLabel(root, text="Welcome!", font=("Arial", 20, "bold"))
title_label.pack(pady=20)
subtitle_label = ctk.CTkLabel(root, text="Discover amazing recipes with ease", font=("Arial", 12))
subtitle_label.pack(pady=5)

button_style = {"width": 250, "height": 40, "corner_radius": 10}

ctk.CTkButton(root, text="Show Categories", command=show_categories, **button_style).pack(pady=8)
ctk.CTkButton(root, text="Show Areas", command=show_areas, **button_style).pack(pady=8)
ctk.CTkButton(root, text="Show Ingredients", command=show_ingredients, **button_style).pack(pady=8)
ctk.CTkButton(root, text="Search Recipe", command=search_recipe, **button_style).pack(pady=8)

ctk.CTkButton(root, text="Quit", command=lambda: [send_request("quit"), client_socket.close(), root.destroy()],
              fg_color="#b83232", hover_color="#ff4c4c", text_color="white", width=250, height=40).pack(pady=20)

root.mainloop()