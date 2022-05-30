import numpy as np
from ordered_set import OrderedSet

from MonteScene.Tree.constants import NodesTypes, ScoreModes
from MonteScene.Tree.Node.Node import Node
from MonteScene.Proposal import Proposal
from MonteScene.ProposalGame import ProposalGame

class Tree(object):
    """
    Class representing Scene Tree.

    Attributes:
        sib_nodes_limit: limit of sibling nodes on a single tree level
        add_esc_nodes: add escape nodes
        root_node: the root node of the tree
        node_curr: currently selected node in the tree
    """

    # Static variables for keeping track
    esc_nodes_n = 0
    end_nodes_n = 0
    @staticmethod
    def __reset_static_vars__():
        Tree.esc_nodes_n = 0
        Tree.end_nodes_n = 0

    @staticmethod
    def generate_new_esc_prop():
        Tree.esc_nodes_n += 1
        esc_prop = Proposal(NodesTypes.NODE_STR_DICT[NodesTypes.ESCNODE] + str(Tree.esc_nodes_n), NodesTypes.ESCNODE)

        return esc_prop

    @staticmethod
    def generate_new_end_prop():
        Tree.end_nodes_n += 1
        end_prop = Proposal(NodesTypes.NODE_STR_DICT[NodesTypes.ENDNODE] + str(Tree.end_nodes_n),
                            NodesTypes.ENDNODE)

        return end_prop

    def __init__(self, settings):
        """
        :param settings: settings containing rules for building the tree
        """

        root_prop = Proposal(NodesTypes.NODE_STR_DICT[NodesTypes.ROOTNODE], NodesTypes.ROOTNODE)
        
        self.sib_nodes_limit = settings.tree.sib_nodes_limit
        self.add_esc_nodes = settings.tree.add_esc_nodes

        update_mode = settings.mcts.ucb_score_type
        assert update_mode in ScoreModes.VALID_SCORE_MODES

        self.update_mode = update_mode

        self.root_node = Node(root_prop, parent=None)
        self.set_curr_node(self.root_node)

        Tree.__reset_static_vars__()

    def check_and_lock(self):
        """
        Check and lock current node and the ancestors if all of their children are locked

        :return:
        """

        tmp_curr_node = self.get_curr_node()

        while True:
            all_children_locked = True
            for child_node in self.get_curr_node().children_nodes:
                if not child_node.explored_lock:
                    all_children_locked = False
                    break

            if self.get_curr_node().prop.type == NodesTypes.ROOTNODE or not all_children_locked:
                break

            self.get_curr_node().explored_lock = True
            self.visit_parent()

        self.set_curr_node(tmp_curr_node)

    def visit_parent(self):
        """
        Change current node to parent node.

        :return:
        """
        assert not self.get_curr_node() is self.root_node
        self.set_curr_node(self.get_curr_node().parent)

    def reset_current_node(self):
        """
        Reset current node to root node

        :return:
        """
        self.set_curr_node(self.root_node)

    def get_curr_node(self):
        """

        :return: current Node
        :rtype: Node
        """

        return self.node_curr

    def get_node_score(self, node, update_mode=None):
        """

        :param node:
        :type node: Node
        :return:
        """

        if update_mode is None:
            update_mode = self.update_mode

        return node.get_score(update_mode)

    def set_curr_node(self, node):
        """

        :param node: node to set as the current node
        :type node: Node
        :return:
        """

        self.node_curr = node

    def get_best_path(self):
        """
        Return path with best score in the tree

        :return:
        """

        node_curr_save = self.get_curr_node()

        self.reset_current_node()
        is_end = False
        final_prop_list = []

        best_score = -np.inf
        while (not is_end):
            best_score = -np.inf
            next_node = None

            if self.get_curr_node().prop.type not in NodesTypes.SPECIAL_NODES_LIST:
                final_prop_list.append(self.get_curr_node().prop)

            for child in self.get_curr_node().children_nodes:
                child_score = self.get_node_score(child)

                if child_score > best_score:
                    next_node = child
                    best_score = child_score

            self.set_curr_node(next_node)
            if self.get_curr_node().prop.type == NodesTypes.ENDNODE or self.get_curr_node().children_nodes is None:
                is_end = True

        leaf_node = self.get_curr_node()
        print("Best score in the tree was %.3f at depth %d" %(best_score, self.get_curr_node().depth))

        self.set_curr_node(node_curr_save)

        return final_prop_list, leaf_node
    
    def get_node_children(self, node, game):
        """
        Get children nodes and initializes them if necessary.

        :param node: node to get the children from
        :type node: Node
        :param game: ProposalGame instance
        :type game: ProposalGame

        :return: list of children nodes
        :rtype: List[Node]
        """
        # Endnode has no children
        if  node.prop.type == NodesTypes.ENDNODE:
            return []

        # Initialize list of children nodes if necessary
        if node.children_nodes is None:
            candidate_pool = game.pool_curr

            assert candidate_pool is not None

            if node.prop.type == NodesTypes.ROOTNODE:
                # For a root node select the first prop in the pool and proposals that are incompatible to this prop

                incomp_pool = candidate_pool[0].incompatible_proposals_set # Start the tree level with Prop at index 0
                child_props = \
                    (candidate_pool & incomp_pool)
            elif node.prop.type == NodesTypes.ESCNODE:
                # For an escnode discard its siblings from the pool
                # TODO in the new version we can merge this with standard node type handling (We know incompatible_pool
                #  already)

                if len(candidate_pool):
                    incompatible_pool = \
                        OrderedSet([n.prop for n in node.parent.get_existing_children_nodes() if
                                    n.prop.type != NodesTypes.ESCNODE])

                    neighbours_pool = node.prop.neighbouring_proposals_set
                    neighbours_pool = neighbours_pool & candidate_pool
                    if not len(neighbours_pool):
                        neighbours_pool = candidate_pool

                    nxt_level_pool = (neighbours_pool - incompatible_pool)
                    nxt_level_pool = nxt_level_pool & nxt_level_pool[0].incompatible_proposals_set
                    child_props = nxt_level_pool

                    if len(child_props) == 1:
                        child_props = OrderedSet()
                else:
                    child_props = OrderedSet()

            elif node.prop.type == NodesTypes.ENDNODE:
                assert False, "Calling get_children_nodes on ENDNODE"
            else:
                # For a standard node discard incompatible proposals and start with neighbors if provided
                if len(candidate_pool):
                    neighbours_pool = node.prop.neighbouring_proposals_set
                    neighbours_pool = neighbours_pool & candidate_pool
                    if not len(neighbours_pool):
                        neighbours_pool = candidate_pool

                    incomp_pool = neighbours_pool[0].incompatible_proposals_set
                    nxt_level_pool = \
                        (candidate_pool & incomp_pool)

                    child_props = nxt_level_pool

                else:
                    child_props = OrderedSet()

            # Limit the number of children nodes
            if self.sib_nodes_limit:
                child_props = child_props[:self.sib_nodes_limit]

            # Add escape node
            if self.add_esc_nodes and len(child_props):
                esc_prop = Tree.generate_new_esc_prop()
                esc_prop.incompatible_proposals_set = child_props

                for prop in node.prop.neighbouring_proposals_set:
                    esc_prop.append_neighbour_prop(prop)
                child_props = child_props | OrderedSet([esc_prop])

            # Initialize children if there are any, otherwise create an endnode
            if len(child_props):
                node.children_nodes = [Node(cp, node) for cp in child_props]
                node.all_children_created = True
            else:
                end_prop = Tree.generate_new_end_prop()

                node.children_nodes = [Node(end_prop, node)]
                node.all_children_created = True

        return node.children_nodes