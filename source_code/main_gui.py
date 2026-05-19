from caro_ai.logic import Game_Caro
from caro_ai.ai.minimax_lv2 import agent
from gui import CaroGUI

def main():
    ai = agent(depth=3)
    CaroGUI(
        game_factory=lambda: Game_Caro(9),
        ai_agent=ai,
        board_size=9
    )

if __name__ == "__main__":
    main()