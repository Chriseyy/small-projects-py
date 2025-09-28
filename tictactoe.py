## tictaccccii toeee pyoyoyy


import tkinter as tk
from tkinter import messagebox
import random

window = tk.Tk()
window.title("Tic Tac Toe")
window.resizable(False, False) 

current_player = "X"
board = [["" for _ in range(3)] for _ in range(3)]
game_over = False
game_mode = None

start_frame = tk.Frame(window)
start_frame.pack(pady=50, padx=50)

board_frame = tk.Frame(window)
status_label = tk.Label(window, text=f"Spieler {current_player} ist am Zug", font=("Helvetica", 16))
reset_button = tk.Button(window, text="Neues Spiel", font=("Helvetica", 12))

buttons = [[None for _ in range(3)] for _ in range(3)]

def computer_move():
    if game_over:
        return

    empty_cells = []
    for r in range(3):
        for c in range(3):
            if board[r][c] == "":
                empty_cells.append((r, c))

    if empty_cells:
        row, col = random.choice(empty_cells)
        handle_click(row, col)


def check_winner():
    global game_over
    for row in range(3):
        if board[row][0] == board[row][1] == board[row][2] != "":
            end_game(board[row][0])
            return
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != "":
            end_game(board[0][col])
            return
    if board[0][0] == board[1][1] == board[2][2] != "":
        end_game(board[0][0])
        return
    if board[0][2] == board[1][1] == board[2][0] != "":
        end_game(board[0][2])
        return
    if all(board[row][col] != "" for row in range(3) for col in range(3)):
        end_game(None) 


def end_game(winner):
    global game_over
    game_over = True
    if winner:
        status_label.config(text=f"Spieler {winner} hat gewonnen!")
        messagebox.showinfo("Spielende", f"Glückwunsch! Spieler {winner} hat gewonnen!")
    else:
        status_label.config(text="Unentschieden!")
        messagebox.showinfo("Spielende", "Das Spiel ist unentschieden!")

def handle_click(row, col):
    global current_player
    if board[row][col] == "" and not game_over:
        board[row][col] = current_player
        buttons[row][col].config(text=current_player, state=tk.DISABLED, disabledforeground="black")
        
        check_winner()
        
        if not game_over:
            current_player = "O" if current_player == "X" else "X"
            status_label.config(text=f"Spieler {current_player} ist am Zug")

            if game_mode == 'Computer' and current_player == 'O':
                window.after(500, computer_move)

def create_board():
    for row in range(3):
        for col in range(3):
            button = tk.Button(board_frame, text="", font=("Helvetica", 24, "bold"), width=5, height=2,
                               command=lambda r=row, c=col: handle_click(r, c))
            button.grid(row=row, column=col, padx=5, pady=5)
            buttons[row][col] = button

def reset_game():
    global board, current_player, game_over
    board = [["" for _ in range(3)] for _ in range(3)]
    current_player = "X"
    game_over = False
    
    board_frame.pack_forget()
    status_label.pack_forget()
    reset_button.pack_forget()

    start_frame.pack(pady=50, padx=50)

def start_game(mode):
    global game_mode
    game_mode = mode
    
    start_frame.pack_forget()

    board_frame.pack(pady=10)
    status_label.pack(pady=10)
    reset_button.pack(pady=10)
    
    current_player = "X"
    status_label.config(text=f"Spieler {current_player} ist am Zug")
    for row in range(3):
        for col in range(3):
            board[row][col] = ""
            buttons[row][col].config(text="", state=tk.NORMAL)


title_label = tk.Label(start_frame, text="Wähle einen Spielmodus", font=("Helvetica", 18))
title_label.pack(pady=10)

pvp_button = tk.Button(start_frame, text="Mensch vs. Mensch", font=("Helvetica", 14), command=lambda: start_game('Mensch'))
pvp_button.pack(pady=10)

pvc_button = tk.Button(start_frame, text="Mensch vs. Computer", font=("Helvetica", 14), command=lambda: start_game('Computer'))
pvc_button.pack(pady=10)

reset_button.config(command=reset_game)

create_board()

window.mainloop()