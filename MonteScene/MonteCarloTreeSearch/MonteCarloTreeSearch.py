import time
import numpy as np
import random
import torch
import copy
import yaml
import os

from MonteScene.MonteCarloTreeSearch.MCTSLogger import MCTSLogger
from MonteScene.Tree.Tree import Tree
from MonteScene.Tree.Node.Node import Node
from MonteScene.Tree.constants import *
from MonteScene.ProposalGame import ProposalGame
from ..utils import *


class MonteCarloSceneSearch:
    """
    Class implementing MCTS

    Attributes:
        mcts_logger: MCTSLogger instance
        settings: settings containing rules for MCTS
        use_cuda: used for tracking computation time. True if torch.cuda.is_available()
        mc_tree: Scene Tree
        iter_cntr: iteration counter

    """
    def __init__(self, game, mcts_logger=None, tree=None, settings=None):
        """

        :param game: ProposalGame instance
        :type game: ProposalGame
        :param mcts_logger: MCTSLogger instance
        :type mcts_logger: MCTSLogger
        :param tree: Tree instance
        :type tree: Tree
        :param settings: settings containing rules for MCTS
        """
        self.game = game

        if mcts_logger is None:
            mcts_logger = MCTSLogger(game=self.game)

        self.mcts_logger = mcts_logger

        if settings is None:
            settings_path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'default_settings.yaml'))
            with open(settings_path, 'r') as f:
                settings = yaml.safe_load(f)
            settings = convert_dict2namespace(settings)
        self.settings = settings

        self.use_cuda = torch.cuda.is_available()

        assert self.settings.mcts.ucb_score_type in ScoreModes.VALID_SCORE_MODES, "UCB_SCORE_TYPE value %s is not supported" % self.settings.mcts.ucb_score_type

        if tree is None:
            self.mc_tree = Tree(self.settings)
        else:
            self.mc_tree = tree

        self.iter_cntr = -1

    def calc_node_ucb(self, node, return_term_scores=True):
        """
        Calculate node confidence using standard UCB

        :param node: input node
        :type node: Node
        :param return_term_scores: True if UCB terms should be returned (for logging)

        :return: node confidence, (optionally exploitation, exploration)
        :rtype: np.float | (np.float (np.float, np.float))
        """
        assert node.vis_n > 0

        exploit_term = node.get_score()
        exploit_term = self.settings.mcts.exploit_coeff * exploit_term

        # Update current UCB weight based on linear decay
        current_explore_weight = (1 - self.iter_cntr / float(self.num_iters)) * self.settings.mcts.start_explore_coeff + \
                                 self.iter_cntr / float(self.num_iters) * self.settings.mcts.end_explore_coeff

        # Calculate exploitation
        UCB_term = exploit_term

        # Calculate exploration
        explore_term = np.sqrt(
            2 * np.log(node.parent.vis_n) / node.vis_n)
        explore_term = current_explore_weight * explore_term

        UCB_term += explore_term

        if return_term_scores:
            return UCB_term, (exploit_term, explore_term)
        else:
            return UCB_term

    def descend_tree(self):
        """
        Perform the SELECTION phase. Traverse the tree to the next level

        :return:
        """

        # Initialize variables
        best_UCB = -np.inf
        best_cand = None
        next_node = None
        b_exploit_term = 0
        b_explore_term = 0

        curr_node = self.mc_tree.get_curr_node()
        children_nodes = list(self.mc_tree.get_node_children(curr_node, self.game))

        is_existing_node = True
        all_children_explored = True
        halt_descent = False

        # Iterate children nodes
        for cn in children_nodes:
            assert isinstance(cn, Node)
            if cn.prop.type == NodesTypes.ENDNODE:
                end_reached = True
                next_node = cn

            # If node has been visited calculate the confidence. Otherwise select this node
            if not cn.is_new:
                if cn.explored_lock and not self.settings.tree.vis_locked:
                    continue
                all_children_explored = False

                UCB_term, (exploit_term, explore_term) = \
                    self.calc_node_ucb(cn, return_term_scores=True)

                if UCB_term > best_UCB:
                    best_UCB = UCB_term
                    best_cand = cn.prop
                    next_node = cn
                    b_exploit_term = exploit_term
                    b_explore_term = explore_term
                    is_existing_node = True
            else:
                all_children_explored = False
                self.mcts_logger.print_to_log('New node %s at depth %d' % (cn.prop.id, cn.depth))

                best_UCB = np.inf
                best_cand = cn.prop
                next_node = cn
                is_existing_node = False
                break

        if all_children_explored:
            halt_descent = True
            self.mcts_logger.print_to_log(("All children explored. Locking node %s" % (curr_node.prop.id)))

            assert False, "Check if everything is implemented correctly. This should never happen."

            # Fix the situation
            # self.mc_tree.check_and_lock()
            #
            # if end_reached:
            #     self.mc_tree.set_curr_node(next_node)
            #     best_cand = next_node
            #
            # return best_cand, halt_descent

        assert next_node is not None
        if is_existing_node:
            curr_node.all_children_created = True

            self.mcts_logger.print_to_log('ModelID: %s, Depth: %d, numSim: %d, UCB %0.3f, Exploit: %0.3f, Explore: %0.3f'
                                          % (next_node.prop.id,
                                             next_node.depth,
                                             next_node.vis_n,
                                             best_UCB,
                                             b_exploit_term,
                                             b_explore_term
                                             ))

        self.mc_tree.set_curr_node(next_node)

        # TODO remove this line
        # assert not self.mc_tree.get_curr_node().prop.type == NodesTypes.ENDNODE

        return best_cand, halt_descent

    def calc_score(self):
        """
        Calculate score (and optionally optimize)

        :return:
        """

        curr_node = self.mc_tree.get_curr_node()

        if curr_node.optimizer is not None and curr_node.optimizer.optimize_steps > 0:
            loss = curr_node.optimizer.optimize(self.game.calc_loss_from_proposals)
            score = self.game.convert_loss_to_score(loss)
        else:
            score = self.game.calc_score_from_proposals()

        return score

    def simulate_and_update(self):
        """
        Perform the SIMULATION phase

        :return:
        """
        self.mcts_logger.print_to_log('Starting simulation at node %s, depth %d' % (self.mc_tree.get_curr_node().prop.id,
                                                                                    self.mc_tree.get_curr_node().depth))
        self.mc_tree.get_curr_node().is_new = False

        pool_curr, prop_seq = self.game.get_state()
        pool_curr = copy.copy(pool_curr)
        node_curr = self.mc_tree.get_curr_node()

        pre_sim_prop_seq_len = len(prop_seq)

        start_time = time.time()

        sim_scores = []
        sim_prop_seqs = []
        sim_optimizers = []

        # Perform several simulations
        for iter_cntr in range(self.settings.mcts.num_sim_iter):
            # TODO Does MultiSim work?

            # Start with curr node
            sim_node_curr = node_curr

            prop_seq = prop_seq[:pre_sim_prop_seq_len]
            self.game.set_state(pool_curr, prop_seq)
            self.mc_tree.set_curr_node(node_curr)
            sim_is_end = False

            # randomly select nodes until reaching the leaf node
            while not sim_is_end:
                sim_child_nodes = self.mc_tree.get_node_children(sim_node_curr, self.game)

                sim_node_curr = random.choice(sim_child_nodes)  # type: Node

                self.mc_tree.set_curr_node(sim_node_curr)
                self.game.step(sim_node_curr.prop)

                endnode_reached = sim_node_curr.prop.type == NodesTypes.ENDNODE
                if endnode_reached:
                    if self.settings.mcts.refinement.optimize_steps:
                        sim_node_curr.add_PropOptimizer(self.game, self.settings)

                    self.mcts_logger.print_to_log("Unfold time: %.3f" % (time.time() - start_time))

                    if self.use_cuda:
                        start = torch.cuda.Event(enable_timing=True)
                        end = torch.cuda.Event(enable_timing=True)

                        start.record()

                    # Calculate score for selected proposals and optionally do refinement
                    simulation_score = self.game.calc_score_from_proposals(props_optimizer=sim_node_curr.optimizer)

                    if self.use_cuda:
                        end.record()
                        torch.cuda.synchronize()
                        self.mcts_logger.print_to_log("Score time: %.3f ms" % (start.elapsed_time(end)))

                    # Update scores
                    sim_is_end = True
                    self.update_tree(simulation_score)

                    sim_scores.append(endnode_reached * simulation_score.cpu().numpy())

                    sim_prop_seqs.append(prop_seq)
                    sim_optimizers.append(sim_node_curr.optimizer)

        # Reset the state after simulation
        # self.game.set_state(pool_curr, prop_seq)
        # self.mc_tree.set_curr_node(node_curr)

        best_prop_seq_ind = np.argmax(sim_scores)
        best_prop_seq = sim_prop_seqs[best_prop_seq_ind]
        best_opt = sim_optimizers[best_prop_seq_ind]
        self.game.set_state(self.game.pool_curr, best_prop_seq)

        self.mcts_logger.print_to_log('%d Simulations took %.4f secs' % (self.settings.mcts.num_sim_iter, time.time()-start_time))

        ret_score = max(sim_scores)
        return ret_score

    def update_tree(self, score):
        """
        Perform UPDATE phase

        :param score:
        :return:
        """

        self.mcts_logger.print_to_log('Updating tree with score %0.2f...' % score)


        curr_node = self.mc_tree.get_curr_node()

        while True:
            self.mc_tree.get_curr_node().update_node(score)

            if self.mc_tree.get_curr_node().prop.type == NodesTypes.ROOTNODE:
                break

            self.mc_tree.visit_parent()

        self.mc_tree.set_curr_node(curr_node)

    def run(self):
        """
        Runs MCSS

        :return:
        """

        self.mcts_logger.reset_logger()

        # Start the search
        self.iter_cntr = -1
        score_curr = -1
        total_time = 0.

        self.num_iters = self.settings.mcts.num_iters

        # Iterate MCTS
        while self.iter_cntr < self.num_iters - 1:
            self.iter_cntr += 1

            st_iter_time = time.time()
            self.mcts_logger.print_to_log('Starting iteration %d of %d' % (self.iter_cntr, self.num_iters))
            is_end = False

            # Start from the tree root and full pool of proposals
            self.mc_tree.reset_current_node()
            self.game.restart_game()

            # If root is locked, then all nodes in the tree have been visited.
            if self.mc_tree.get_curr_node().explored_lock and not self.settings.mcts.vis_locked:
                self.mcts_logger.print_to_log('Root locked stopping...')
                break

            # Iterate tree nodes until the ENDNODE is reached
            halt_descent = False
            invalid_iter = False

            while (not is_end):
                # SELECT
                cand_curr, halt_descent = self.descend_tree()

                if self.mc_tree.get_curr_node().prop.type == NodesTypes.ENDNODE:
                    if self.mc_tree.get_curr_node().is_new and self.settings.mcts.refinement.optimize_steps:
                        self.mc_tree.get_curr_node().add_PropOptimizer(self.game, self.settings)

                    score_curr = self.calc_score()
                    self.update_tree(score_curr)

                    is_end = True
                elif halt_descent:
                    invalid_iter = True
                    is_end = True
                    assert False, "Why was descent halted?"
                else:
                    self.game.step(self.mc_tree.get_curr_node().prop)
                    if self.mc_tree.get_curr_node().is_new:
                        # SIMULATE AND UPDATE
                        score_curr = self.simulate_and_update()
                        is_end = True

            if invalid_iter:
                self.mcts_logger.print_to_log('Iteration halted!')
                self.iter_cntr -= 1
                assert False
                # Possible Handle
                # continue

            iter_time = time.time() - st_iter_time
            total_time += iter_time
            self.mcts_logger.print_to_log("Iter time: %.3f ms" % iter_time)

            self.mcts_logger.log_mcts(iter=self.iter_cntr,
                            last_score=score_curr,
                            last_tree_depth=self.mc_tree.get_curr_node().depth,
                            mc_tree=self.mc_tree)


        # Finalize MCTS
        self.mcts_logger.log_mcts(iter=self.iter_cntr,
                        last_score=score_curr,
                        last_tree_depth=self.mc_tree.get_curr_node().depth,
                        mc_tree=self.mc_tree,
                        )

        self.mcts_logger.print_to_log("Total search time: %.3f" % total_time)

        self.mc_tree.reset_current_node()
        self.game.restart_game()

        if self.settings.mcts.refinement.final_optimization_steps > 0:
            # Descend best path and optimize once more
            best_props_list, leaf_node = self.mc_tree.get_best_path()
            last_opt_st_time = time.time()
            optimizer = leaf_node.optimizer  # type: PropsOptimizer
            optimizer.set_optimize_steps(self.settings.mcts.refinement.final_optimization_steps)
            score = self.game.calc_score_from_proposals(best_props_list,
                                                       props_optimizer=optimizer)
            last_opt_time = time.time() - last_opt_st_time
            total_time += last_opt_time

            self.mcts_logger.print_to_log("Total time after optimization: %.3f" % total_time)

        # Final log
        self.mcts_logger.log_final(mc_tree=self.mc_tree)
