import sys
import arcade
from views.game_view import GameView, SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from views.game_over_view import Game_Over_View


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

    game_view = GameView(level=1)
    window.show_view(game_view)

    arcade.run()


def run_game_over(result=True, score="0", timer="00:00", statistic="Игра завершена"):
    # Создание окна Game Over
    window = Game_Over_View()
    window.result = result
    window.score = score
    window.timer = timer
    window.statistic = statistic

    arcade.run()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ["game_over", "--game-over"]:
        # Game Over
        result = sys.argv[2] == "True" if len(sys.argv) > 2 else True
        score = sys.argv[3] if len(sys.argv) > 3 else "0"
        timer = sys.argv[4] if len(sys.argv) > 4 else "00:00"
        statistic = sys.argv[5] if len(sys.argv) > 5 else "Игра завершена"

        run_game_over(result, score, timer, statistic)
    else:
        # Обычный режим
        main()



