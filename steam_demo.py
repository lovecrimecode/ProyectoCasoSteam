import tkinter as tk
from tkinter import ttk, filedialog, messagebox
#from tkinter.scrolledtext import ScrolledText
from textblob import TextBlob
import sqlite3
import csv
from collections import Counter
from nltk import ngrams
from functools import partial

# List of positive and negative keywords
positive_keywords = [
    "fun", "exciting", "awesome", "amazing", "great", "fantastic", "incredible", "enjoyable", "engaging", "creative",
    "challenging", "beautiful", "innovative", "interesting", "entertaining", "joyful", "cool", "impressive", "good",
    "friendly", "satisfying", "addictive", "dynamic", "playful", "immersive", "rewarding", "motivating", "stimulating",
    "thought-provoking", "uplifting", "positive", "motivational", "compelling", "brilliant", "outstanding", "inspiring",
    "captivating", "fantasy", "charming", "exceptional", "unforgettable", "original", "thrilling", "mind-blowing",
    "hilarious", "refreshing", "successful", "heartwarming", "cooperative", "masterful", "effective", "clever",
    "vibrant"
]
negative_keywords = [
    "boring", "frustrating", "slow", "unresponsive", "dull", "annoying", "terrible", "disappointing", "bad",
    "useless", "horrible", "lame", "repetitive", "ugly", "buggy", "glitchy", "clunky", "unplayable", "confusing",
    "poor", "stupid", "uninspired", "difficult", "predictable", "hard", "awful", "unpolished", "unoptimized",
    "disorganized", "unintuitive", "complicated", "lackluster", "tedious", "unoriginal", "pointless", "clumsy",
    "laggy", "unbalanced", "shallow", "monotonous", "underwhelming", "horrendous", "chaotic"
]

# Create or connect to the SQLite database
def create_database():
    conn = sqlite3.connect('comments.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS comments
                 (game TEXT, comment TEXT, sentiment TEXT, label TEXT)''')
    conn.commit()
    conn.close()

# Save comment to the database
def save_comment(game, comment):
    blob = TextBlob(comment)
    sentiment = 'Positive' if blob.sentiment.polarity > 0 else 'Negative'
    label = extract_label(comment)

    conn = sqlite3.connect('comments.db')
    c = conn.cursor()
    c.execute('INSERT INTO comments (game, comment, sentiment, label) VALUES (?, ?, ?, ?)',
              (game, comment, sentiment, label))
    conn.commit()
    conn.close()

# Extract keyword from comment using ngrams
def extract_label(comment):
    comment_words = comment.lower().split()

    for n in range(3, 1, -1):  # Check for bigrams and trigrams
        n_grams = ngrams(comment_words, n)
        for grams in n_grams:
            phrase = ' '.join(grams)
            if phrase in positive_keywords:
                return phrase.capitalize()
            if phrase in negative_keywords:
                return phrase.capitalize()

    for word in comment_words:  # Check unigrams
        if word in positive_keywords:
            return word.capitalize()
        if word in negative_keywords:
            return word.capitalize()

    return 'Neutral'

# Get comments from the database for a specific game
def get_comments(game):
    conn = sqlite3.connect('comments.db')
    c = conn.cursor()
    c.execute('''SELECT comment, sentiment, label FROM comments WHERE game=?''', (game,))
    comments = c.fetchall()
    conn.close()
    return comments

# Update the comments frame
def update_comments_frame(game, comments_frame):
    comments = get_comments(game)
    for widget in comments_frame.winfo_children():
        widget.destroy()

    for comment, sentiment, label in comments:
        tk.Label(comments_frame, text=f"{comment}\n(Sentiment: {sentiment}, Label: {label})",
                 wraplength=550, justify="left", bg="#2E2E2E", fg="white", anchor="w").pack(fill="x", padx=10, pady=5)

# Load CSV data and analyze
def load_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if not file_path:
        return

    # Read the input CSV and add sentiment and label
    processed_rows = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        fieldnames = reader.fieldnames + ['Sentiment', 'Label']  # Add new columns

        for row in reader:
            comment = row['comment']
            sentiment = 'Positive' if TextBlob(comment).sentiment.polarity > 0 else 'Negative'
            label = extract_label(comment)

            row['Sentiment'] = sentiment
            row['Label'] = label
            processed_rows.append(row)

    # Save the processed CSV
    save_path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")])
    if not save_path:
        return

    with open(save_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(processed_rows)

    messagebox.showinfo("Success", f"CSV processed and saved to {save_path}")

# Extract keyword from comment using ngrams
def extract_label(comment):
    comment_words = comment.lower().split()

    for n in range(3, 1, -1):  # Check for bigrams and trigrams
        n_grams = ngrams(comment_words, n)
        for grams in n_grams:
            phrase = ' '.join(grams)
            if phrase in positive_keywords:
                return phrase.capitalize()
            if phrase in negative_keywords:
                return phrase.capitalize()

    for word in comment_words:  # Check unigrams
        if word in positive_keywords:
            return word.capitalize()
        if word in negative_keywords:
            return word.capitalize()

    return 'Neutral'


# Show game page
def show_game_page(game):
    def back_to_list():
        game_page_window.destroy()  # Cerrar la ventana actual del juego
        show_game_list()  # Regresar a la lista de juegos en la ventana principal
    
    # Crear una nueva ventana para el juego
    game_page_window = tk.Toplevel(root)
    game_page_window.title(f"{game} - Steam")
    game_page_window.geometry("600x650")
    game_page_window.config(bg="#2E2E2E")

    # Definir las descripciones de los juegos
    game_descriptions = {
        "Minecraft": "Minecraft is a sandbox video game developed by Mojang Studios.",
        "Fortnite": "Fortnite is a battle royale game developed by Epic Games.",
        "Sparking Zero": "Sparking Zero is an action-adventure video game."
    }
    
    game_description = game_descriptions.get(game, "Description not available.")
    
    # Game title
    game_title = tk.Label(game_page_window, text=game, font=("Arial", 24, "bold"), fg="#FFF", bg="#2E2E2E")
    game_title.pack(pady=20)

    # Game description
    description_label = tk.Label(game_page_window, text=game_description, font=("Arial", 12), fg="#A3A3A3", bg="#2E2E2E", padx=10, pady=10)
    description_label.pack(pady=10)

    # Buttons frame (Install and Back)
    button_frame = tk.Frame(game_page_window, bg="#2E2E2E")
    button_frame.pack(pady=10)

    install_button = tk.Button(button_frame, text="Install", bg="#1DB954", fg="white", font=("Arial", 12), relief="flat", bd=0, padx=20, pady=10)
    install_button.pack(side="left", padx=10)

    back_button = tk.Button(button_frame, text="Back to Game List", command=back_to_list, font=("Arial", 12), bg="#444", fg="white", relief="flat", bd=0, padx=20, pady=10)
    back_button.pack(side="left", padx=10)

    # Comments section label
    comments_section_label = tk.Label(game_page_window, text="Comments Section", font=("Arial", 14, "bold"), fg="#FFF", bg="#2E2E2E")
    comments_section_label.pack(pady=10)

    # Create canvas and scrollbar for comments
    comments_canvas = tk.Canvas(game_page_window, bg="#2E2E2E", highlightthickness=0)
    comments_canvas.pack(pady=10, fill="both", expand=True)

    scrollbar = tk.Scrollbar(game_page_window, orient="vertical", command=comments_canvas.yview)
    scrollbar.pack(side="right", fill="y")

    comments_canvas.configure(yscrollcommand=scrollbar.set)

    # Frame inside the canvas
    comments_frame = tk.Frame(comments_canvas, bg="#2E2E2E")
    comments_canvas.create_window((0, 0), window=comments_frame, anchor="nw")

    # Populate comments on load
    update_comments_frame(game, comments_frame)

    comments_frame.update_idletasks()
    comments_canvas.config(scrollregion=comments_canvas.bbox("all"))

    # Input frame for new comments
    comment_input_frame = tk.Frame(game_page_window, bg="#2E2E2E")
    comment_input_frame.pack(side="bottom", fill="x", pady=10)

    # Comment input field
    comment_entry = tk.Entry(comment_input_frame, font=("Arial", 12), fg="#FFFFFF", bg="#3C3C3C", bd=0, insertbackground="white", relief="flat")
    comment_entry.pack(side="left", fill="x", expand=True, padx=10)

    def submit_comment():
        comment = comment_entry.get()
        if comment:
            save_comment(game, comment)
            comment_entry.delete(0, tk.END)
            update_comments_frame(game, comments_frame)
            comments_frame.update_idletasks()
            comments_canvas.config(scrollregion=comments_canvas.bbox("all"))

    # Submit button
    submit_button = tk.Button(comment_input_frame, text="Submit Comment", command=submit_comment, font=("Arial", 12), bg="#4CAF50", fg="white", relief="flat", bd=0, padx=20, pady=10)
    submit_button.pack(side="right", padx=10)

# Show game list
def show_game_list():
    game_list_frame.grid(row=0, column=0, sticky='nsew')
    game_page_frame.grid_forget()

# Configuring the main window
root = tk.Tk()
root.title("Steam")
root.geometry("600x650")
root.config(bg="#1B1B1B")

# Create database
create_database()

# Main game list frame
game_list_frame = tk.Frame(root, bg="#1B1B1B")
game_list_frame.grid(row=0, column=0, sticky='nsew')

# Game page frame
game_page_frame = tk.Frame(root, bg="#2E2E2E")

# Steam header with exit button
header_frame = tk.Frame(game_list_frame, bg="#1E1E1E", height=50)
header_frame.pack(fill='x')

steam_title = tk.Label(header_frame, text="Steam", font=("Arial", 20, "bold"), fg="#FFF", bg="#1E1E1E")
steam_title.pack(side="left", padx=20)

exit_button = tk.Button(header_frame, text="Exit", command=root.quit, font=("Arial", 12), fg="white", bg="#FF4C4C", relief="flat", bd=0, padx=10, pady=5)
exit_button.pack(side="right", padx=20)

# Title for game list
game_list_title = tk.Label(game_list_frame, text="Select a Game", font=("Arial", 24, "bold"), fg="#FFF", bg="#1B1B1B")
game_list_title.pack(pady=20)

# Game buttons
minecraft_button = tk.Button(game_list_frame, text="Minecraft", command=lambda: show_game_page("Minecraft"), font=("Arial", 14), bg="#444", fg="white", relief="flat", bd=0, padx=20, pady=10)
minecraft_button.pack(pady=10)

fortnite_button = tk.Button(game_list_frame, text="Fortnite", command=lambda: show_game_page("Fortnite"), font=("Arial", 14), bg="#444", fg="white", relief="flat", bd=0, padx=20, pady=10)
fortnite_button.pack(pady=10)

sparking_zero_button = tk.Button(game_list_frame, text="Sparking Zero", command=lambda: show_game_page("Sparking Zero"), font=("Arial", 14), bg="#444", fg="white", relief="flat", bd=0, padx=20, pady=10)
sparking_zero_button.pack(pady=10)

load_csv_button = tk.Button(game_list_frame, text="Load CSV", command=load_csv, bg="#4CAF50", fg="white", bd=0, padx=20, pady=10)
load_csv_button.pack(pady=10)

# Start the application
root.mainloop()