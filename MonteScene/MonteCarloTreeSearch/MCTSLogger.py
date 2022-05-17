import numpy as np
from graphviz import Digraph
from abc import ABC, abstractmethod
from typing import List

from MonteScene.ProposalGame import ProposalGame
from MonteScene.Tree.Tree import Tree
from MonteScene.Proposal.Prop import Proposal

class MCTSLogger(ABC):
    """
    Abstract class representing Logger. Serves as a base class for task specific loggers

    Attributes:
          game: ProposalGame instance

    """
    def __init__(self, game):
        """

        :param game: ProposalGame instance
        :type game: ProposalGame
        """

        self.game = game

    def print_to_log(self, print_str):
        print(print_str)

    @abstractmethod
    def reset_logger(self):
        """
        Reset logging variables

        :return:
        """

        # TODO Reset variables that should be tracked
        raise NotImplementedError()

    @abstractmethod
    def export_solution(self, best_props_list):
        """
        Export final solution.

        :param best_props_list: List of best proposals
        :type best_props_list:  List[Proposal]
        :return:
        """

        # TODO Export solution. Should be called from log_final
        raise NotImplementedError()

    @abstractmethod
    def log_final(self, mc_tree):
        """
        Final log performed after the search

        :param mc_tree: final tree
        :type mc_tree: Tree
        :return:
        """

        # TODO Implement logging for the last iteration on MCTS
        # TODO maybe visualize best solution
        # TODO maybe visualize plots
        # TODO maybe drawGraph
        # TODO maybe export_solution

        raise NotImplementedError()

    @abstractmethod
    def log_mcts(self, iter, last_score, last_tree_depth, mc_tree):
        """
        Log MCTS progress

        :param iter: iteration
        :type iter: int
        :param last_score: last score
        :type last_score: float
        :param last_tree_depth: last tree depth
        :type last_tree_depth: int
        :param mc_tree: current tree
        :type mc_tree: Tree
        :return:
        """

        # TODO Implement logging of a single MCTS iteration
        # TODO maybe visualize best solution so far
        # TODO maybe visualize solution at current iteration
        # TODO maybe visualize plots
        # TODO maybe drawGraph
        raise NotImplementedError()

    def drawGraph(self, mc_tree, out_file, K=2, D=-1):
        """
        Draw current tree into a .pdf file

        :param mc_tree: current tree
        :type mc_tree: Tree
        :param out_file: output file path
        :param K: number of children to draw. 0 draws all children
        :param D: max depth of the tree to draw. -1 defaults to whole tree
        :return:
        """
        def addNodes(node_curr, curr_d):
            if node_curr.children_nodes is None or len(node_curr.children_nodes) == 0:
                return
            else:
                child_scores = [mc_tree.get_node_score(c) for c in node_curr.children_nodes]

            child_scores = np.array(child_scores)
            top_k_child_inds = child_scores.argsort()[-K:]
            for i in top_k_child_inds:
                c = node_curr.children_nodes[i] # type: Node

                child_node_name = c.id
                parent_node_name = c.parent.id

                score = mc_tree.get_node_score(c)

                dot.node(child_node_name, 'score=%0.3f \n n=%d \n %s' % (score, c.vis_n, c.prop.id))

                if c.explored_lock:
                    dot.attr('edge', color='red')
                    dot.edges([(parent_node_name, child_node_name)])
                    dot.attr('edge', color='black')
                else:
                    dot.edges([(parent_node_name, child_node_name)])

                if curr_d != D:
                    # curr_d += 1
                    addNodes(c, curr_d=curr_d + 1)

        dot = Digraph(comment='MCTS')

        # K = 2
        # D = -1  # Change to -1 to draw the hole tree

        assert isinstance(mc_tree, Tree)
        mc_tree.reset_current_node()

        curr_d = 0

        curr_node = mc_tree.get_curr_node()
        dot.node(curr_node.id, 'score=%0.3f \n n=%d \n %s' %
                 (mc_tree.get_node_score(curr_node), curr_node.vis_n, curr_node.prop.id))

        addNodes(curr_node, curr_d=curr_d)

        dot.render(out_file)