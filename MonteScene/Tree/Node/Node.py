from ordered_set import OrderedSet

from MonteScene.constants.constants import *
from MonteScene.Proposal.PropsOptimizer import PropsOptimizer
from MonteScene.ProposalGame import ProposalGame
from .NodeScore import NodeScore
from MonteScene.Proposal import Proposal

class Node(object):
    """
    Class representing node.

    Attributes:
        id: unique string identifier for the node
        prop: proposal which is contained within the node
        parent: parent node
        update_mode: rule for updating node score
        score: score assigned to the node based on update_mode
        vis_n: number of times the node has been visited during search
        is_new: identifies whether selected node has just been created (Typically True as long as vis_n = 0)
        depth: depth of the tree at which the node is located
        children_nodes: list of children nodes (None before initialization)
        explored_lock: True if all of its descendants have been visited at least once (Enables node locking)
        all_children_created: True if all children nodes have been initialized
        optimizer: Optimizer associated with the node

    """
    def __init__(self, prop, parent):
        """

        :param prop: proposal to be contained within the node
        :type prop: Proposal
        :param parent: Parent node
        :type parent: Node | None
        :param update_mode: rule for updating node score
        :type update_mode: int
        """

        if parent is None:
            self.id = prop.id
        else:
            self.id = prop.id + "_" + parent.id

        self.prop = prop
        self.parent = parent

        self.node_score = NodeScore()

        self.vis_n = 0

        self.is_new = True

        if parent is None:
            self.depth = 0
        else:
            self.depth = self.parent.depth + 1

        # Will be set to True if all children have been explored
        if prop.type == NodesTypes.ENDNODE:
            self.children_nodes = OrderedSet()
            self.explored_lock = True
            self.all_children_created = True
        else:
            self.children_nodes = None
            self.explored_lock = False
            self.all_children_created = False

        self.optimizer = None

    def set_prop(self, prop: Proposal):
        self.prop = prop

    def change_node_id_and_children_id(self, new_id: int):
        self.id = new_id
        if self.children_nodes is None:
            return

        for cn in self.children_nodes:
            cn.change_node_id_and_children_id(cn.prop.id + "_" + new_id)


    def get_existing_children_nodes(self):
        if self.prop.type == NodesTypes.ENDNODE:
            return []

        return self.children_nodes

    def append_child(self, child):
        if self.children_nodes is None:
            self.children_nodes = []

        child.parent = self
        self.children_nodes.append(child)

    def update_node(self, score):

        # Increment the number of visits
        self.vis_n += 1

        self.node_score.update_score(score)

        # Check the lock
        # if self.all_children_created:
        #     self.check_and_lock()

    def get_score(self, update_mode):

        ret_score = self.node_score.get_score(update_mode)
        if update_mode == ScoreModes.AVG_NODE_SCORE_MODE:
            ret_score = ret_score / self.vis_n if self.vis_n > 0 else ret_score

        return  ret_score

    def add_PropOptimizer(self, game, settings):
        """
        Add an optimizer

        :param game: ProposalGame instance
        :type game: ProposalGame
        :param settings: settings containing rules for defining the optimizer
        :return:
        """
        self.optimizer = PropsOptimizer(game, settings)


