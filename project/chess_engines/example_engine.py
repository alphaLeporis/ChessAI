#!/usr/bin/python3
from project.chess_engines.uci_engine import UciEngine
import chess
from project.chess_agents.AlphaBetaPruningNullMoveQueiscence import AlphaBetaPruningNullMoveQueiscence
from project.chess_utilities.NewUtility import NewUtility

if __name__ == "__main__":
    # Create your utility
    utility = NewUtility()
    # Create your agent
    agent = AlphaBetaPruningNullMoveQueiscence(utility, 15.0)
    # Create the engine
    engine = UciEngine("AlphaBetaPruningNullQuiscence engine", "Alexander", agent)
    # Run the engine (will loop until the game is done or exited)
    engine.engine_operation()
