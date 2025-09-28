## tictaccccii toeee pyoyoyy


import tkinter as tk
from tkinter import messagebox
import random
import time

window = tk.Tk()
window.title("Tic Tac Toe")
window.resizable(False, False) 

current_player = "X"
board = [["" for _ in range(3)] for _ in range(3)]
game_over = False
game_mode = None
difficulty = None

start_frame = tk.Frame(window)
start_frame.pack(pady=50, padx=50)

board_frame = tk.Frame(window)
status_label = tk.Label(window, text=f"Spieler {current_player} ist am Zug", font=("Helvetica", 16))
difficulty_frame = tk.Frame(window)
reset_button = tk.Button(window, text="Neues Spiel", font=("Helvetica", 12))

buttons = [[None for _ in range(3)] for _ in range(3)]


def check_for_win(player, current_board=None):
    b = current_board if current_board else board
    for i in range(3):
        if all(b[i][j] == player for j in range(3)): return True
        if all(b[j][i] == player for j in range(3)): return True
    if all(b[i][i] == player for i in range(3)): return True
    if all(b[i][2-i] == player for i in range(3)): return True
    return False

def computer_move_random():
    empty_cells = [(r, c) for r in range(3) for c in range(3) if board[r][c] == ""]
    if empty_cells:
        r, c = random.choice(empty_cells)
        handle_click(r, c)

def computer_move_medium():
    for r in range(3):
        for c in range(3):
            if board[r][c] == "":
                board[r][c] = 'O' 
                if check_for_win('O'):
                    board[r][c] = "" 
                    handle_click(r, c) 
                    return
                board[r][c] = "" 


    for r in range(3):
        for c in range(3):
            if board[r][c] == "":
                board[r][c] = 'X'
                if check_for_win('X'):
                    board[r][c] = "" 
                    handle_click(r, c) 
                    return
                board[r][c] = ""


    if board[1][1] == "":
        handle_click(1, 1)
        return

    ecken = [(0, 0), (0, 2), (2, 0), (2, 2)]
    freie_ecken = [e for e in ecken if board[e[0]][e[1]] == ""]
    if freie_ecken:
        handle_click(freie_ecken[0][0], freie_ecken[0][1])
        return

    computer_move_random()


def minimax(current_board, is_maximizing):
    if check_for_win('O', current_board): return 10
    if check_for_win('X', current_board): return -10
    if all(cell != '' for row in current_board for cell in row): return 0

    if is_maximizing:
        best_score = -float('inf')
        for r in range(3):
            for c in range(3):
                if current_board[r][c] == '':
                    current_board[r][c] = 'O'
                    score = minimax(current_board, False)
                    current_board[r][c] = ''
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = float('inf')
        for r in range(3):
            for c in range(3):
                if current_board[r][c] == '':
                    current_board[r][c] = 'X'
                    score = minimax(current_board, True)
                    current_board[r][c] = ''
                    best_score = min(score, best_score)
        return best_score

def computer_move_hard():
    best_score = -float('inf')
    best_move = None
    for r in range(3):
        for c in range(3):
            if board[r][c] == '':
                board[r][c] = 'O'
                score = minimax(board, False)
                board[r][c] = ''
                if score > best_score:
                    best_score = score
                    best_move = (r, c)
    if best_move:
        handle_click(best_move[0], best_move[1])


def computer_move():
    if game_over: return
    for r in range(3):
        for c in range(3):
            buttons[r][c].config(state=tk.DISABLED)
    
    window.update()
    time.sleep(0.25)

    if difficulty == 'Einfach':
        computer_move_random()
    elif difficulty == 'Mittel':
        computer_move_medium()
    elif difficulty == 'Schwer':
        computer_move_hard()

    if not game_over:
        for r in range(3):
            for c in range(3):
                if board[r][c] == '':
                    buttons[r][c].config(state=tk.NORMAL)




def check_winner():
    global game_over
    if check_for_win('X'): end_game('X'); return
    if check_for_win('O'): end_game('O'); return
    if all(board[row][col] != "" for row in range(3) for col in range(3)): end_game(None)

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

            if difficulty and current_player == 'O':
                computer_move()



def hide_all_frames():
    start_frame.pack_forget()
    difficulty_frame.pack_forget()
    board_frame.pack_forget()
    status_label.pack_forget()
    reset_button.pack_forget()

def show_difficulty_menu():
    hide_all_frames()
    difficulty_frame.pack(pady=50, padx=50)

def start_game(mode):
    global difficulty, current_player, game_over, board
    difficulty = mode 
    
    hide_all_frames()
    board_frame.pack(pady=10)
    status_label.pack(pady=10)
    reset_button.pack(pady=10)
    

    board = [["" for _ in range(3)] for _ in range(3)]
    current_player = "X"
    game_over = False
    status_label.config(text=f"Spieler {current_player} ist am Zug")
    for r in range(3):
        for c in range(3):
            buttons[r][c].config(text="", state=tk.NORMAL)

def show_main_menu():
    hide_all_frames()
    start_frame.pack(pady=50, padx=50)



tk.Label(start_frame, text="Wähle einen Spielmodus", font=("Helvetica", 18)).pack(pady=10)
tk.Button(start_frame, text="Mensch vs. Mensch", font=("Helvetica", 14), command=lambda: start_game(None)).pack(pady=10, fill='x')
tk.Button(start_frame, text="Mensch vs. Computer", font=("Helvetica", 14), command=show_difficulty_menu).pack(pady=10, fill='x')


tk.Label(difficulty_frame, text="Wähle die Schwierigkeit", font=("Helvetica", 18)).pack(pady=10)
tk.Button(difficulty_frame, text="Einfach (Zufall)", font=("Helvetica", 14), command=lambda: start_game('Einfach')).pack(pady=10, fill='x')
tk.Button(difficulty_frame, text="Mittel (Regeln)", font=("Helvetica", 14), command=lambda: start_game('Mittel')).pack(pady=10, fill='x')
tk.Button(difficulty_frame, text="Schwer (Unbesiegbar)", font=("Helvetica", 14), command=lambda: start_game('Schwer')).pack(pady=10, fill='x')
tk.Button(difficulty_frame, text="< Zurück", font=("Helvetica", 10), command=show_main_menu).pack(pady=20)


for r in range(3):
    for c in range(3):
        button = tk.Button(board_frame, text="", font=("Helvetica", 24, "bold"), width=5, height=2,
                           command=lambda row=r, col=c: handle_click(row, col))
        button.grid(row=r, column=c, padx=5, pady=5)
        buttons[r][c] = button


reset_button.config(command=show_main_menu)


show_main_menu() 
window.mainloop()