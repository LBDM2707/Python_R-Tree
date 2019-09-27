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

    def contain_rect(self, rect):
        return self.x1 < rect.x1 and self.y1 < rect.y1 and self.x2 > rect.x2 and self.y2 > rect.y2

    def has_point(self, point):
        return self.x1 <= point.x <= self.x2 and self.y1 <= point.y <= self.y2

    def __str__(self):
        return "Rect: ({}, {}), ({}, {})".format(self.x1, self.y1, self.x2, self.y2)


class Point:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y

    def __str__(self):
        return "Point #{}: ({}, {})".format(self.id, self.x, self.y)


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
        # update in the right position to keep the list ordered
        self.add_points([point])
        pass

    def add_points(self, points):
        self.data_points += points
        # update MBR
        self.update_MBR()
        pass

    def perimeter_increase_with_point(self, point):
        x1 = point.x if point.x < self.MBR.x1 else self.MBR.x1
        y1 = point.y if point.y < self.MBR.y1 else self.MBR.y1
        x2 = point.x if point.x > self.MBR.x2 else self.MBR.x2
        y2 = point.y if point.y > self.MBR.y2 else self.MBR.y2
        return Rect(x1, y1, x2, y2).perimeter() - self.perimeter()

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

    def add_child_node(self, node):
        self.add_child_nodes([node])
        pass

    def add_child_nodes(self, nodes):
        for node in nodes:
            node.parent_node = self
            self.child_nodes.append(node)
        self.update_MBR()
        pass

    def update_MBR(self):
        if self.is_leaf():
            self.MBR.x1 = min([point.x for point in self.data_points])
            self.MBR.x2 = max([point.x for point in self.data_points])
            self.MBR.y1 = min([point.y for point in self.data_points])
            self.MBR.y2 = max([point.y for point in self.data_points])
        else:
            self.MBR.x1 = min([child.MBR.x1 for child in self.child_nodes])
            self.MBR.x2 = max([child.MBR.x2 for child in self.child_nodes])
            self.MBR.y1 = min([child.MBR.y1 for child in self.child_nodes])
            self.MBR.y2 = max([child.MBR.y2 for child in self.child_nodes])
        if self.parent_node and not self.parent_node.MBR.contain_rect(self.MBR):
            self.parent_node.update_MBR()
        pass


class RegionTree:
    def __init__(self, B):
        self.B = B
        self.root = Node(self.B)

    def insert_point(self, point, cur_node=None):
        # init U as node
        if cur_node is None:
            cur_node = self.root
        # Insertion logic start
        if cur_node.is_leaf():
            cur_node.add_point(point)
            # handle overflow
            if cur_node.is_overflow():
                self.handle_overflow(cur_node)
        else:
            chosen_child = self.choose_best_child(cur_node, point)
            self.insert_point(point, chosen_child)
        pass

    # Find a suitable one to expand:
    @staticmethod
    def choose_best_child(node, point):
        best_child = None
        best_perimeter = 0
        # Scan the child nodes
        for item in node.child_nodes:
            if node.child_nodes.index(item) == 0 or best_perimeter > item.perimeter_increase_with_point(point):
                best_child = item
                best_perimeter = item.perimeter_with_point(point)
        return best_child

    # WIP
    def handle_overflow(self, node):
        node, new_node = self.split_leaf_node(node) if node.is_leaf() else self.split_internal_node(node)
        if node.is_root():
            self.root = Node(self.B)
            self.root.add_child_nodes([node, new_node])
        else:
            node.parent_node.add_child_node(new_node)
            if node.parent_node.is_overflow():
                self.handle_overflow(node.parent_node)
        pass

    # WIP
    def split_leaf_node(self, node):
        new_node = Node(self.B)
        all_points = sorted(node.data_points, key=lambda point: point.x)
        node.data_points = all_points[:len(all_points) // 2]
        node.update_MBR()
        new_node.add_points(all_points[len(all_points) // 2:])
        return node, new_node

    # WIP
    def split_internal_node(self, node):
        new_node = Node(self.B)
        return node, new_node

    # Take in a Rect and return number of data point that is covered by the R tree.
    def region_query(self, rect, node=None):
        # initiate with root
        node = self.root if node is None else node
        if node.is_leaf():
            print("some point")
            count = 0
            for point in node.child_nodes:
                if rect.has_point(point):
                    count += 1
            return count
        else:
            return sum([self.region_query(rect, child) for child in node.child_nodes if rect.is_overlap(child.MBR)])
