from wordle_solver import WordleSolver

if __name__ == '__main__':
    w = WordleSolver()
    try:
        w.solve_wordle()
    finally:
        w.exit_handler()
