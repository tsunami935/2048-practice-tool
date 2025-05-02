from gamestate import GameState, GameStatus, Action

run = True

game_state = GameState()

while run:
    print("Welcome to 2048! Move by typing [UP, DOWN, LEFT, RIGHT] or [W, A, S, D].")
    while game_state.status == GameStatus.RUN:
        print("")
        game_state.print()
        move = input("Move: ")
        match move.strip().upper():
            case "UP" | "W":
                game_state.step(Action.UP)
            case "LEFT" | "A":
                game_state.step(Action.LEFT)
            case "DOWN" | "S":
                game_state.step(Action.DOWN)
            case "RIGHT" | "D":
                game_state.step(Action.RIGHT)
            case "HELP" | "H":
                print("Move by typing [UP, DOWN, LEFT, RIGHT] or [W, A, S, D].")
            case _:
                print("Invalid move.")
    replay = input("\nWould you like to play again? (Y/N): ")
    if replay.strip().upper() == "N":
        run = False