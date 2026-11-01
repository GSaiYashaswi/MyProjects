import random
import threading
import pyttsx3
import tkinter as tk
from tkinter import ttk

# --- Voice Speech Engine ---
def speak(text):
    def run_speech():
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 160)
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass
    threading.Thread(target=run_speech, daemon=True).start()

# --- Main Hand Cricket Desktop App (Two Innings / Fixed Crazy Mode) ---
class HandCricketApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hand Cricket Pro - Two Innings Match")
        self.root.geometry("680x750")
        self.root.configure(bg="#1E1E2E")
        self.root.resizable(False, False)

        # Game State Variables
        self.mode = tk.StringVar(value="Normal")
        self.innings = 1  # 1 = You Bat, 2 = Computer Bats (You Bowl)
        self.total_score = 0
        self.comp_score = 0
        self.target = 0
        self.high_score = 0
        self.balls_faced = 0
        self.is_match_over = False

        # Build UI Layout
        self.setup_ui()

    def setup_ui(self):
        # Header / Control Bar
        top_frame = tk.Frame(self.root, bg="#181825", padx=20, pady=12)
        top_frame.pack(fill=tk.X)

        self.match_status_lbl = tk.Label(top_frame, text="🏏 INNINGS 1: YOU BATTING", font=("Helvetica", 14, "bold"), fg="#89B4FA", bg="#181825")
        self.match_status_lbl.pack(side=tk.LEFT)

        tk.Label(top_frame, text="Mode:", font=("Helvetica", 11), fg="#CDD6F4", bg="#181825").pack(side=tk.LEFT, padx=(15, 5))
        mode_menu = ttk.OptionMenu(top_frame, self.mode, "Normal", "Normal", "Crazy", command=self.on_mode_change)
        mode_menu.pack(side=tk.LEFT)

        # Main Body Panel
        body = tk.Frame(self.root, bg="#1E1E2E", padx=20, pady=12)
        body.pack(fill=tk.BOTH, expand=True)

        # Scoreboard Section
        score_panel = tk.Frame(body, bg="#181825", padx=15, pady=10, relief=tk.RAISED, bd=2)
        score_panel.pack(fill=tk.X, pady=(0, 10))

        score_inner = tk.Frame(score_panel, bg="#181825")
        score_inner.pack(fill=tk.X, pady=2)
        
        self.score_label = tk.Label(score_inner, text="Score: 0", font=("Helvetica", 24, "bold"), fg="#A6E3A1", bg="#181825")
        self.score_label.pack(side=tk.LEFT)
        
        self.target_lbl = tk.Label(score_inner, text="Target: -", font=("Helvetica", 14, "bold"), fg="#FAB387", bg="#181825")
        self.target_lbl.pack(side=tk.RIGHT, padx=10)

        self.highscore_lbl = tk.Label(score_panel, text="High Score: 0", font=("Helvetica", 10, "bold"), fg="#F9E2AF", bg="#181825")
        self.highscore_lbl.pack(anchor="w", pady=(2, 0))

        # Stats Row
        stats_frame = tk.Frame(score_panel, bg="#313244", padx=10, pady=5)
        stats_frame.pack(fill=tk.X, pady=(6, 0))
        
        self.balls_lbl = tk.Label(stats_frame, text="Balls: 0", font=("Helvetica", 10), fg="#CDD6F4", bg="#313244")
        self.balls_lbl.pack(side=tk.LEFT)
        
        self.sr_lbl = tk.Label(stats_frame, text="Strike Rate: 0.0", font=("Helvetica", 10), fg="#CDD6F4", bg="#313244")
        self.sr_lbl.pack(side=tk.RIGHT)

        # Two Dedicated Choice Cards
        choices_container = tk.Frame(body, bg="#1E1E2E")
        choices_container.pack(fill=tk.X, pady=(0, 10))

        # Card 1: My Choice
        my_card = tk.Frame(choices_container, bg="#313244", padx=15, pady=8)
        my_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
        
        self.my_title_lbl = tk.Label(my_card, text="👤 Your Batting Choice", font=("Helvetica", 10, "bold"), fg="#89B4FA", bg="#313244")
        self.my_title_lbl.pack(anchor="w")
        self.my_choice_val = tk.Label(my_card, text="-", font=("Helvetica", 22, "bold"), fg="#A6E3A1", bg="#313244")
        self.my_choice_val.pack(pady=4)

        # Card 2: Computer Choice
        comp_card = tk.Frame(choices_container, bg="#313244", padx=15, pady=8)
        comp_card.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(8, 0))
        
        self.comp_title_lbl = tk.Label(comp_card, text="🤖 Computer Bowler", font=("Helvetica", 10, "bold"), fg="#F38BA8", bg="#313244")
        self.comp_title_lbl.pack(anchor="w")
        self.comp_choice_val = tk.Label(comp_card, text="-", font=("Helvetica", 22, "bold"), fg="#F9E2AF", bg="#313244")
        self.comp_choice_val.pack(pady=4)

        # Result Message Banner
        self.result_lbl = tk.Label(body, text="Click any number below to start playing!", font=("Helvetica", 11, "italic"), fg="#F9E2AF", bg="#1E1E2E")
        self.result_lbl.pack(pady=(0, 10))

        # Keypad Grid Section (1 to 10 Buttons)
        keypad_frame = tk.Frame(body, bg="#181825", padx=15, pady=12, relief=tk.RAISED, bd=2)
        keypad_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(keypad_frame, text="Select Number (1 to 10):", font=("Helvetica", 10, "bold"), fg="#89B4FA", bg="#181825").pack(anchor="w", pady=(0, 8))

        btn_grid = tk.Frame(keypad_frame, bg="#181825")
        btn_grid.pack()

        for i in range(1, 11):
            row = (i - 1) // 5
            col = (i - 1) % 5
            b = tk.Button(btn_grid, text=str(i), font=("Helvetica", 11, "bold"), width=6, height=1, bg="#45475A", fg="#CDD6F4", 
                          activebackground="#89B4FA", activeforeground="#11111B", relief=tk.FLAT,
                          command=lambda val=i: self.play_ball(val))
            b.grid(row=row, column=col, padx=4, pady=4)

        # Rules Description Box
        rules_frame = tk.Frame(body, bg="#11111B", padx=10, pady=8)
        rules_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(rules_frame, text="Mode Rules:", font=("Helvetica", 9, "bold"), fg="#89B4FA", bg="#11111B").pack(anchor="w")
        self.rules_text = tk.Label(rules_frame, text="", font=("Helvetica", 8), fg="#CDD6F4", bg="#11111B", justify=tk.LEFT)
        self.rules_text.pack(anchor="w", pady=2)
        
        self.update_rules_display()

    def update_rules_display(self):
        if self.mode.get() == "Normal":
            text = "• Normal: Matching numbers = OUT!\n• Innings 2: Bowl and match the computer's number to get it out."
        else:
            text = "• Crazy Mode: Matching numbers = (Number)² runs! Computer within ±1 = OUT!\n• Innings 2: Same rules apply."
        self.rules_text.config(text=text)

    def on_mode_change(self, value):
        self.update_rules_display()
        self.reset_match()

    def reset_match(self):
        self.innings = 1
        self.total_score = 0
        self.comp_score = 0
        self.target = 0
        self.balls_faced = 0
        self.is_match_over = False
        self.match_status_lbl.config(text="🏏 INNINGS 1: YOU BATTING", fg="#89B4FA")
        self.my_title_lbl.config(text="👤 Your Batting Choice")
        self.comp_title_lbl.config(text="🤖 Computer Bowler")
        self.score_label.config(text="Score: 0")
        self.target_lbl.config(text="Target: -")
        self.balls_lbl.config(text="Balls: 0")
        self.sr_lbl.config(text="Strike Rate: 0.0")
        self.my_choice_val.config(text="-")
        self.comp_choice_val.config(text="-")
        self.result_lbl.config(text="New match started! Click a number to bat.", fg="#F9E2AF")

    def play_ball(self, user_val):
        if self.is_match_over:
            self.reset_match()

        comp_val = random.randint(1, 10)
        mode = self.mode.get()

        # --- INNINGS 1: YOU BAT ---
        if self.innings == 1:
            self.balls_faced += 1
            self.my_choice_val.config(text=str(user_val))
            self.comp_choice_val.config(text=str(comp_val))

            status = "RUNS"
            scored = 0
            msg = ""

            if mode == "Normal":
                if user_val == comp_val:
                    status = "OUT"
                else:
                    scored = user_val
                    msg = f"+{user_val} Runs!"
            elif mode == "Crazy":
                if user_val == comp_val:
                    # Matching numbers gives square of number and is NOT out
                    scored = user_val ** 2
                    status = "CRITICAL"
                    msg = f"CRITICAL HIT! {user_val} squared = +{scored} Runs!"
                elif abs(user_val - comp_val) == 1:
                    # Bowler is within plus or minus 1 of batter -> OUT!
                    status = "OUT"
                    msg = f"OUT! Bowler played {comp_val} (±1 Trap)!"
                else:
                    scored = user_val
                    msg = f"+{user_val} Runs!"

            if status == "OUT":
                self.target = self.total_score + 1
                self.is_match_over = True
                self.match_status_lbl.config(text="🎯 INNINGS 2: YOU BOWLING", fg="#FAB387")
                self.my_title_lbl.config(text="👤 Your Bowling Choice")
                self.comp_title_lbl.config(text="🤖 Computer Batter")
                self.target_lbl.config(text=f"Target: {self.target}")
                self.result_lbl.config(text=f"{msg} You scored {self.total_score}. Target is {self.target}. Click to start Innings 2!", fg="#F38BA8")
                speak(f"You are out with {self.total_score} runs. Computer needs {self.target} to win. Start bowling!")
                
                # Switch to Innings 2 for next click
                self.innings = 2
                self.is_match_over = False
                self.comp_score = 0
                self.balls_faced = 0
            else:
                self.total_score += scored
                if self.total_score > self.high_score:
                    self.high_score = self.total_score
                    self.highscore_lbl.config(text=f"High Score: {self.high_score}")

                self.score_label.config(text=f"Score: {self.total_score}")
                self.result_lbl.config(text=msg, fg="#A6E3A1")
                speak(msg)

            strike_rate = (self.total_score / self.balls_faced) * 100 if self.balls_faced > 0 else 0.0
            self.balls_lbl.config(text=f"Balls: {self.balls_faced}")
            self.sr_lbl.config(text=f"Strike Rate: {strike_rate:.1f}")

        # --- INNINGS 2: YOU BOWL / COMPUTER BATS ---
        elif self.innings == 2:
            self.balls_faced += 1
            self.my_choice_val.config(text=str(user_val))
            self.comp_choice_val.config(text=str(comp_val))

            is_comp_out = False
            if mode == "Normal":
                if user_val == comp_val:
                    is_comp_out = True
            elif mode == "Crazy":
                if user_val == comp_val:
                    # In Crazy mode bowling, matching gives computer bonus runs (or you can keep it simple as exact match or ±1 trap)
                    # Let's apply the same logic symmetrically or exact match for computer wicket
                    is_comp_out = (user_val == comp_val) or (abs(user_val - comp_val) == 1)

            if is_comp_out:
                self.is_match_over = True
                self.result_lbl.config(text=f"WICKET! You got the computer out for {self.comp_score}! YOU WIN!", fg="#A6E3A1")
                speak(f"Wicket! You got the computer out! You win the match!")
            else:
                # If computer survives, it scores runs (in crazy mode if they match, they get squared runs)
                comp_runs_added = (comp_val ** 2) if (mode == "Crazy" and user_val == comp_val) else comp_val
                self.comp_score += comp_runs_added
                self.score_label.config(text=f"Comp: {self.comp_score} / {self.target}")
                
                if self.comp_score >= self.target:
                    self.is_match_over = True
                    self.result_lbl.config(text=f"Computer chased the target! Computer scored {self.comp_score}. YOU LOSE!", fg="#F38BA8")
                    speak(f"Computer chased the target. You lose!")
                else:
                    self.result_lbl.config(text=f"Computer scored {comp_runs_added} runs. Target: {self.target}", fg="#F9E2AF")
                    speak(f"Computer scored {comp_runs_added} runs.")

            self.balls_lbl.config(text=f"Balls: {self.balls_faced}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HandCricketApp(root)
    root.mainloop()