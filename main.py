from tkinter import ttk
import tkinter as tk
import pyperclip
from password_manager.manager import *

def center_window(win, width, height):
    win.update_idletasks()
    screen_w = win.winfo_screenwidth()
    screen_h = win.winfo_screenheight()

    x = (screen_w // 2) - (width // 2)
    y = (screen_h // 2) - (height // 2)

    win.geometry(f"{width}x{height}+{x}+{y}")

def create_scrollable_container(parent):
    canvas = tk.Canvas(parent, highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)

    scroll_frame = tk.Frame(canvas)

    window_id = canvas.create_window(
        (0, 0),
        window=scroll_frame,
        anchor="nw"
    )

    def _on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _on_canvas_configure(event):
        canvas.itemconfigure(window_id, width=event.width)

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    scroll_frame.bind("<Configure>", _on_frame_configure)
    canvas.bind("<Configure>", _on_canvas_configure)

    canvas.bind("<Enter>", lambda e: canvas.bind_all("<MouseWheel>", _on_mousewheel))
    canvas.bind("<Leave>", lambda e: canvas.unbind_all("<MouseWheel>"))

    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return scroll_frame

window = tk.Tk()
center_window(window, 600, 800)
window.title("Password Manager")
window.columnconfigure(0, weight=1)
window.rowconfigure(0, weight=1)
window.config(background="#9abed6")
frame = ttk.Frame(window, padding=10)
frame.columnconfigure(0, weight=1)
frame.grid(row=0, column=0)

style = ttk.Style(window)
style.theme_use("clam")

style.configure(
    "Big.TButton",
    font=("Roboto", 20),
)

style.configure(
    "Pass.TButton",
    font=("Roboto", 20),
    padding=(15, 10)
)

style.configure(
    "Pass.TEntry",
    font=("Segoe UI", 50),
    padding=(80, 15)
)

style.configure(
    "Form.TEntry",
    font=("Roboto", 20),
    padding=(15, 10)
)

style.configure(
    "Form.TLabel",
    font=("Roboto", 20),
    padding=(15, 10)
)

def ask_for_passphrase() -> str:
    pass_window = tk.Toplevel(window)
    center_window(pass_window, 500, 150)
    pass_window.title("Password Window")

    result = tk.StringVar(master=pass_window)

    entry_frame = tk.Frame(
        pass_window,
        bg="white",
        padx=15,
        pady=0
    )
    entry_frame.pack(fill="x", padx=10, pady=(0, 15))

    entry = tk.Entry(
        entry_frame,
        textvariable=result,
        font=("Segoe UI", 24),
        show="*",
        relief="flat",
        bd=1
    )
    entry.pack(fill="x", ipady=10)
    entry.focus()

    def submit():
        pass_window.destroy()

    ttk.Button(pass_window, text="Submit", style="Pass.TButton", command=submit).pack()

    pass_window.bind("<Return>", lambda e: submit())

    pass_window.wait_window()
    return result.get()

def print_entries(entries: list[dict[str, str]]) -> None:
    entry_window = tk.Toplevel(window)
    center_window(entry_window, 500, 600)
    entry_window.title("List Window")
    entry_window.configure(background="#cbd5e1")

    container = create_scrollable_container(entry_window)
    container.configure(bg="#0f172a")
    if not entries:
        entry_frame = tk.Frame(
            container,
            bg="#cbd5e1",
            padx=15,
            pady=0
        )
        entry_frame.pack(fill="x", padx=10, pady=(0, 15))

        entry_frame.columnconfigure(0, weight=1)
        entry_frame.columnconfigure(1, weight=0)

        # Service name
        tk.Label(
            entry_frame,
            text="The vault is empty",
            font=("Segoe UI", 16, "bold"),
            fg="black",
            bg="#cbd5e1",
            anchor="w"
        ).grid(row=0, column=0, sticky="ew")
    else:
        for entry in entries:
            entry_frame = tk.Frame(
                container,
                bg="#cbd5e1",
                padx=15,
                pady=0
            )
            entry_frame.pack(fill="x", padx=10, pady=(0, 15))

            entry_frame.columnconfigure(0, weight=1)
            entry_frame.columnconfigure(1, weight=0)

            # Service name
            tk.Label(
                entry_frame,
                text=entry["service"],
                font=("Segoe UI", 16, "bold"),
                fg="black",
                bg="#cbd5e1",
                anchor="w"
            ).grid(row=0, column=0, sticky="ew")

            ttk.Button(
                entry_frame,
                text="Password",
                style="Big.TButton",
                command=lambda s=entry["service"]: pyperclip.copy(retrieve_password(s, ask_for_passphrase()))
            ).grid(row=0, column=1, rowspan=3, sticky="e", padx=(10, 0))


            # Username
            tk.Label(
                entry_frame,
                text=f'Username: {entry["username"]}',
                font=("Segoe UI", 12),
                fg="black",
                bg="#cbd5e1",
                anchor="w"
            ).grid(row=1, column=0, sticky="ew")

            # URL
            tk.Label(
                entry_frame,
                text=f'URL: {entry["url"]}',
                font=("Segoe UI", 12),
                fg="black",
                bg="#cbd5e1",
                anchor="w"
            ).grid(row=2, column=0, sticky="ew")


def add_entry() -> dict[str, str]:
    entry_window = tk.Toplevel(window)
    center_window(entry_window, 500, 600)
    entry_window.title("List Window")

    container = ttk.Frame(entry_window, padding=20)
    container.pack(fill="both", expand=True)

    result = {}
    service_var  = tk.StringVar()
    url_var = tk.StringVar()
    username_var = tk.StringVar()
    password_var = tk.StringVar()

    ttk.Label(container, text="Service", style="Form.TLabel").grid(row=0, column=0, sticky="w", pady=5)
    ttk.Entry(container, textvariable=service_var, style="Form.TEntry").grid(row=0, column=1, sticky="ew")

    ttk.Label(container, text="Url", style="Form.TLabel").grid(row=1, column=0, sticky="w", pady=5)
    ttk.Entry(container, textvariable=url_var, style="Form.TEntry").grid(row=1, column=1, sticky="ew")

    ttk.Label(container, text="Username", style="Form.TLabel").grid(row=2, column=0, sticky="w", pady=5)
    ttk.Entry(container, textvariable=username_var, style="Form.TEntry").grid(row=2, column=1, sticky="ew")

    ttk.Label(container, text="Password", style="Form.TLabel").grid(row=3, column=0, sticky="w", pady=5)
    ttk.Entry(container, textvariable=password_var, show="*", style="Form.TEntry").grid(row=3, column=1, sticky="ew")

    def submit():
        result["data"] = {
            "service": service_var.get(),
            "url": url_var.get(),
            "username": username_var.get(),
            "password": password_var.get()
        }
        entry_window.destroy()


    ttk.Button(container, text="Submit", style="Big.TButton", command=submit).grid(row=4, column=1, columnspan=2, pady=15)
    entry_window.bind("<Return>", lambda e: submit())

    entry_window.wait_window()
    return result.get("data")


ttk.Button(frame, text="Initialize Vault", style="Big.TButton", command=lambda: init_vault(ask_for_passphrase()), padding=(45,30)).grid(row=0, column=0, sticky="ew", pady=5)

ttk.Button(frame, text="List Entries", style="Big.TButton", command=lambda: print_entries(list_entries(ask_for_passphrase())), padding=(50,30)).grid(row=1, column=0, sticky="ew", pady=5)

ttk.Button(frame, text="New Entry", style="Big.TButton", command=lambda: new_entry(ask_for_passphrase(), add_entry()), padding=(50,30)).grid(row=2, column=0, sticky="ew", pady=5)

ttk.Button(frame, text="Quit", style="Big.TButton", command=window.destroy, padding=(50,30)).grid(row=5, column=0, sticky="ew", pady=5)

window.mainloop()

