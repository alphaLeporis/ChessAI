#!/usr/bin/python3
from project.chess_agents.negamax_queiscence_agent import NegaMaxQueiscence
from project.chess_engines.uci_engine import UciEngine
from project.chess_utilities.complete_utility import CompleteUtility

if __name__ == "__main__":
    # Create your utility
    utility = CompleteUtility()
    # Create your agent
    agent = NegaMaxQueiscence(utility, 5.0)
    # Create the engine
    engine = UciEngine("NegaMax - Queiscence - MTDf - Opening - Closing", "Alexander, Louis, Niels", agent)
    # Run the engine (will loop until the game is done or exited)
    engine.engine_operation()
