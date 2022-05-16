class NodesTypes:
    """
    Enumerates different node types

    """

    ROOTNODE = 0
    ESCNODE = 1
    ENDNODE = 2
    OTHERNODE = 3

    NODE_STR_DICT = {
        ROOTNODE: 'ROOT',
        ESCNODE: 'ESC',
        ENDNODE: 'END',
        OTHERNODE: 'OTHER'
    }

    SPECIAL_NODES_LIST = [ROOTNODE, ESCNODE, ENDNODE]

class ScoreModes:
    """
    Enumerates different score modes

    """

    MAX_NODE_SCORE_MODE = "MAX"
    AVG_NODE_SCORE_MODE = "AVG"
    VALID_SCORE_MODES = [MAX_NODE_SCORE_MODE, AVG_NODE_SCORE_MODE]