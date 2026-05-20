import customtkinter as ctk
from tkinter import simpledialog, messagebox
import socket
import json
import threading

HOST = '127.0.0.1'
PORT = 5050
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))
client_socket.recv(1024) 

def recv_full(sock, max_bytes=65536):
    """Receive a complete response — handles both normal and length-prefixed payloads."""
    first = sock.recv(8)
    if not first:
        return ""
    try:
        length_str = first.decode('utf-8').strip()
        expected_len = int(length_str)
        data = b""
        while len(data) < expected_len:
            chunk = sock.recv(min(8192, expected_len - len(data)))
            if not chunk:
                break
            data += chunk
        return data.decode('utf-8')
    except (ValueError, UnicodeDecodeError):
        data = first
        sock.settimeout(0.5)
        try:
            while True:
                chunk = sock.recv(8192)
                if not chunk:
                    break
                data += chunk
        except socket.timeout:
            pass
        finally:
            sock.settimeout(None)
        return data.decode('utf-8', errors='replace')

def send_request(request, callback=None):
    def target():
        try:
            client_socket.send(request.encode())
            response = recv_full(client_socket)
            if callback:
                root.after(0, lambda: callback(response))
        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Error", str(e)))
    threading.Thread(target=target, daemon=True).start()

def show_list_window(title, items):
    win = ctk.CTkToplevel(root)
    win.title(title)
    win.geometry("350x500")
    win.lift()
    win.focus_force()

    # Header label
    ctk.CTkLabel(win, text=title, font=("Arial", 14, "bold")).pack(pady=(10, 5))
    ctk.CTkLabel(win, text=f"{len(items)} items", font=("Arial", 10), text_color="gray").pack()

    listbox = ctk.CTkTextbox(win, width=320, height=400)
    listbox.pack(padx=15, pady=10)
    for i, item in enumerate(items, 1):
        listbox.insert("end", f"{i}. {item}\n")
    listbox.configure(state="disabled")

def handle_list_response(data, title):
    try:
        items = json.loads(data)
        show_list_window(title, items)
    except json.JSONDecodeError as e:
        messagebox.showerror("Parse Error", f"Could not parse response:\n{e}\n\nData preview: {data[:200]}")

def show_categories():
    send_request("categories", lambda r: handle_list_response(r, "Famous Categories"))

def show_areas():
    send_request("areas", lambda r: handle_list_response(r, "GCC Areas"))

def show_ingredients():
    send_request("ingredients", lambda r: handle_list_response(r, "Ingredients"))

def search_recipe():
    name = simpledialog.askstring("Search Recipe", "Enter recipe name:")
    if not name:
        return
    def callback(data):
        try:
            recipes = json.loads(data)
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid response from server.")
            return
        if not recipes:
            messagebox.showinfo("No Recipes", "No recipes found.")
            return
        output = "\n".join(f"{i+1}. {r['strMeal']}" for i, r in enumerate(recipes))
        choice = simpledialog.askinteger("Select Recipe", f"{output}\nEnter number:")
        if choice and 1 <= choice <= len(recipes):
            sel = recipes[choice-1]
            details = (
                f"Name: {sel['strMeal']}\n"
                f"Category: {sel['strCategory']}\n"
                f"Area: {sel['strArea']}\n"
                f"Instructions: {sel['strInstructions']}"
            )
            messagebox.showinfo("Recipe Details", details)
            save = messagebox.askyesno("Save Recipe", "Save this recipe?")
            if save:
                send_request(
                    f"save:{json.dumps(sel)}",
                    lambda r: messagebox.showinfo("Saved", "Recipe saved successfully!")
                )
    send_request(f"search:{name}", callback)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

root = ctk.CTk()
root.title("Stitch Recipe Discovery Hub")
root.geometry("500x550")

ctk.CTkLabel(root, text="Welcome!", font=("Arial", 20, "bold")).pack(pady=20)
ctk.CTkLabel(root, text="Discover amazing recipes with ease", font=("Arial", 12)).pack(pady=5)

btn_style = {"width": 250, "height": 40, "corner_radius": 10}
ctk.CTkButton(root, text="Show Categories",  command=show_categories, **btn_style).pack(pady=8)
ctk.CTkButton(root, text="Show GCC Areas",   command=show_areas,      **btn_style).pack(pady=8)
ctk.CTkButton(root, text="Show Ingredients", command=show_ingredients, **btn_style).pack(pady=8)
ctk.CTkButton(root, text="Search Recipe",    command=search_recipe,    **btn_style).pack(pady=8)
ctk.CTkButton(
    root, text="Quit", command=root.destroy,
    fg_color="#b83232", hover_color="#ff4c4c",
    text_color="white", corner_radius=8
).pack(pady=20)

ctk.CTkLabel(root, text="Happy Cooking! 🍳", font=("Arial", 10, "italic")).pack(side="bottom", pady=10)

root.mainloop()
try:
    client_socket.send(b"quit")
    client_socket.close()
except:
    pass