class Node:
    """
    Class for a node in a tree
    :param value: the value of the node
    :param sons: the sons of the node
    """
    
    def __init__(self, value, sons = None):
        if sons is None:
            sons = list()
        self.value = value
        self.sons = sons
