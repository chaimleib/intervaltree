from intervaltree.node import Node
from intervaltree import Interval

def test_str():
    left = Node(x_center=-1, s_center=set([Interval(-1, 0)]))
    assert "Node<-1, depth=1, balance=0>" == str(left)

    root = Node(
        x_center=0,
        s_center=set([Interval(0, 1)]),
        left_node=left,
        right_node=None,
    )
    assert "Node<0, depth=2, balance=-1>" == str(root)


def test_str_type():
    class MyNode(Node):
        pass

    left = MyNode(x_center=-1, s_center=set([Interval(-1, 0)]))
    assert MyNode == type(left)
    assert "MyNode<-1, depth=1, balance=0>" == str(left)

    root = MyNode(
        x_center=0,
        s_center=set([Interval(0, 1)]),
        left_node=left,
        right_node=None,
    )
    assert "MyNode<0, depth=2, balance=-1>" == str(root)


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, '-v'])
