import math
import sys
from copy import deepcopy


# B = 4
class Rect:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def perimeter(self):
        return 2 * (abs(self.x2 - self.x1) + abs(self.y2 - self.y1))

    def is_overlap(self, rect):
        return self.x1 < rect.x2 and self.x2 > rect.x1 and self.y1 > rect.y2 and self.y2 < rect.y1

    def has_point(self, point):
        return self.x1 <= point.x <= self.x2 and self.y1 <= point.y <= self.y2

    def __str__(self):
        return "({}, {}) - ({}, {})".format(self.x1, self.y1, self.x2, self.y2)


class Point:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

    def __str__(self):
        return "Point #{}: - ({}, {})".format(self.id, self.x, self.y)


class Node(object):
    def __init__(self, B=4):
        self.B = B
        self.id = 0
        # for internal nodes
        self.child_nodes = []
        # for leaf nodespyth
        self.data_points = []
        self.parent_node = None
        self.MBR = Rect(-1, -1, -1, -1)

    def add_point(self, point):
        if self.is_leaf():
            self.data_points.append(point)
            # update MBR
            if len(self.data_points) == 1:
                self.MBR = Rect(point.x, point.y, point.x, point.y)
            else:
                print(self.MBR)
                print(point)
                self.MBR.x1 = point.x if point.x < self.MBR.x1 else self.MBR.x1
                self.MBR.y1 = point.y if point.y < self.MBR.y1 else self.MBR.y1
                self.MBR.x2 = point.x if point.x > self.MBR.x2 else self.MBR.x2
                self.MBR.y2 = point.y if point.y > self.MBR.y2 else self.MBR.y2
        pass

    def perimeter_with_point(self, point):
        x1 = point.x if point.x < self.MBR.x1 else self.MBR.x1
        y1 = point.y if point.y < self.MBR.y1 else self.MBR.y1
        x2 = point.x if point.x > self.MBR.x2 else self.MBR.x2
        y2 = point.y if point.y > self.MBR.y2 else self.MBR.y2
        return Rect(x1, y1, x2, y2).perimeter()

    def perimeter(self):
        # only calculate the half perimeter here
        return self.MBR.perimeter()

    def is_underflow(self):
        return (self.is_leaf and len(self.data_points) < math.ceil(self.B / 2)) or \
               (not self.is_leaf and len(self.child_nodes) < math.ceil(self.B / 2))

    def is_overflow(self):
        return (self.is_leaf and len(self.data_points) > self.B) or \
               (not self.is_leaf and len(self.child_nodes) > self.B)

    def is_root(self):
        return self.parent is None

    def is_leaf(self):
        return len(self.child_nodes) == 0


class RegionTree:
    def __init__(self, B):
        self.B = B
        self.root = Node()

    def insert_point(self, point, cur_node=None):
        # init U as node
        if cur_node is None:
            cur_node = self.root
        # Insertion logic start
        if cur_node.is_leaf():
            cur_node.add_point(point)
            # handle overflow
        else:
            chosen_child = self.choose_best_child(cur_node, point)
            self.insert_point(point, chosen_child)
        pass

    # Find a suitable one to expand:
    def choose_best_child(self, node, point):
        fit_child = None
        best_child = None
        best_perimeter = 0
        # Scan the child nodes
        for item in node.child_nodes:
            if item.has_point(point):
                fit_child = node
                break
            if node.child_nodes.index(item) == 0 or best_perimeter > item.perimeter_with_point(point):
                best_child = item
                best_perimeter = node.perimeter_with_point(point)
        return fit_child if fit_child is not None else best_child

    def query_region(self, rect):
        return None
