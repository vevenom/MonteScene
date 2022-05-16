from MonteScene.Game import Game
from MonteScene.MonteCarloTreeSearch.MCTSLogger import MCTSLogger
from MonteScene.MonteCarloTreeSearch.MonteCarloTreeSearch import MonteCarloSceneSearch


if __name__ == '__main__':
        # Create Game
        # TODO Abstract Class. Define your own Game inherited from this and implement the abstract methods
        game = Game()

        # Create Logger
        mcts_logger = MCTSLogger(game) # TODO Abstract Class. Define your own Logger inherited from this and implement the abstract methods

        # Create MCTS
        # run MCTS
        mcts = MonteCarloSceneSearch(game, mcts_logger=mcts_logger, settings=None)
        mcts.run()
        # mcts_logger.create_gif()
