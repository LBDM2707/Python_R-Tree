# This file contains some core functions of implementing an R-Tree. You can refer to this example to build up R-Trees and run queries.
import math
import sys

B = 4

# We set B=4, and I suggest you to set B=3 or B=4;


def sequential_query(points, query):
    result = 0
    for point in points:
        if query['x1'] <= point['x'] <= query['x2'] and query['y1'] <= point['y'] <= query['y2']:
            result = result + 1
    return result


class Node(object):
    def __init__(self):
        self.id = 0
        # for internal nodes
        self.child_nodes = []
        # for leaf nodes
        self.data_points = []
        self.parent = None
        self.MBR = {
            'x1': -1,
            'y1': -1,
            'x2': -1,
            'y2': -1,
        }

    def perimeter(self):
        # only calculate the half perimeter here
        return (self.MBR['x2'] - self.MBR['x1']) + (self.MBR['y2'] - self.MBR['y1'])

    def is_underflow(self):
        if self.is_leaf():
            if self.data_points.__len__() < math.ceil(B / 2):
                return True
            else:
                return False
        else:
            if self.child_nodes.__len__() < math.ceil(B / 2):
                return True
            else:
                return False

    def is_overflow(self):
        if self.is_leaf():
            if self.data_points.__len__() > B:
                return True
            else:
                return False
        else:
            if self.child_nodes.__len__() > B:
                return True
            else:
                return False

    def is_root(self):
        if self.parent is None:
            return True
        else:
            return False

    def is_leaf(self):
        if self.child_nodes.__len__() == 0:
            return True
        else:
            return False


class RTree(object):
    def __init__(self):
        self.root = Node()

    def query(self, node, query):
        num = 0
        if node.is_leaf():
            for point in node.data_points:
                if self.is_covered(point, query):
                    num = num + 1
            return num
        else:
            for child in node.child_nodes:
                if self.is_intersect(child, query):
                    num = num + self.query(child, query)
            return num

    def is_intersect(self, node, query):
        # if two mbrs are intersected, then:
        # |center1_x - center2_x| <= length1 / 2 + length2 / 2 and:
        # |center1_y - center2_y| <= width1 / 2 + width2 / 2
        center1_x = (node.MBR['x2'] + node.MBR['x1']) / 2
        center1_y = (node.MBR['y2'] + node.MBR['y1']) / 2
        length1 = node.MBR['x2'] - node.MBR['x1']
        width1 = node.MBR['y2'] - node.MBR['y1']
        center2_x = (query['x2'] + query['x1']) / 2
        center2_y = (query['y2'] + query['y1']) / 2
        length2 = query['x2'] - query['x1']
        width2 = query['y2'] - query['y1']
        if abs(center1_x - center2_x) <= length1 / 2 + length2 / 2 and\
                abs(center1_y - center2_y) <= width1 / 2 + width2 / 2:
            return True
        else:
            return False

    def is_covered(self, point, query):
        x1, x2, y1, y2 = query['x1'], query['x2'], query['y1'], query['y2']
        if x1 <= point['x'] <= x2 and y1 <= point['y'] <= y2:
            return True
        else:
            return False

    def insert(self, u, p):
        if u.is_leaf():
            self.add_data_point(u, p)
            if u.is_overflow():
                self.handle_overflow(u)
        else:
            v = self.choose_subtree(u, p)
            self.insert(v, p)
            self.update_mbr(v)


    # return the child whose MBR requires the minimum increase in perimeter to cover p
    def choose_subtree(self, u, p):
        if u.is_leaf():
            return u
        else:
            min_increase = sys.maxsize
            best_child = None
            for child in u.child_nodes:
                if min_increase > self.peri_increase(child, p):
                    min_increase = self.peri_increase(child, p)
                    best_child = child
            # return self.choose_subtree(best_child, p)
            return best_child

    def peri_increase(self, node, p):
        # new perimeter - original perimeter = increase of perimeter
        origin_mbr = node.MBR
        x1, x2, y1, y2 = origin_mbr['x1'], origin_mbr['x2'], origin_mbr['y1'], origin_mbr['y2']
        increase = (max([x1, x2, p['x']]) - min([x1, x2, p['x']]) +
                    max([y1, y2, p['y']]) - min([y1, y2, p['y']])) - node.perimeter()
        return increase

    def handle_overflow(self, u):
        u1, u2 = self.split(u)
        # if u is root, create a new root with s1 and s2 as its' children
        if u.is_root():
            new_root = Node()
            self.add_child(new_root, u1)
            self.add_child(new_root, u2)
            self.root = new_root
            self.update_mbr(new_root)
        # if u is not root, delete u, and set s1 and s2 as u's parent's new children
        else:
            w = u.parent
            # copy the information of s1 into u
            w.child_nodes.remove(u)
            self.add_child(w, u1)
            self.add_child(w, u2)
            if w.is_overflow():
                self.handle_overflow(w)
            self.update_mbr(w)

    def split(self, u):
        # split u into s1 and s2
        best_s1 = Node()
        best_s2 = Node()
        best_perimeter = sys.maxsize
        # u is a leaf node
        if u.is_leaf():
            m = u.data_points.__len__()
            # create two different kinds of divides
            divides = [sorted(u.data_points, key=lambda data_point: data_point['x']),
                       sorted(u.data_points, key=lambda data_point: data_point['y'])]
            for divide in divides:
                for i in range(math.ceil(0.4 * B), m - math.ceil(0.4 * B) + 1):
                    s1 = Node()
                    s1.data_points = divide[0: i]
                    self.update_mbr(s1)
                    s2 = Node()
                    s2.data_points = divide[i: divide.__len__()]
                    self.update_mbr(s2)
                    if best_perimeter > s1.perimeter() + s2.perimeter():
                        best_perimeter = s1.perimeter() + s2.perimeter()
                        best_s1 = s1
                        best_s2 = s2

        # u is a internal node
        else:
            # create four different kinds of divides
            m = u.child_nodes.__len__()
            divides = [sorted(u.child_nodes, key=lambda child_node: child_node.MBR['x1']),
                       sorted(u.child_nodes, key=lambda child_node: child_node.MBR['x2']),
                       sorted(u.child_nodes, key=lambda child_node: child_node.MBR['y1']),
                       sorted(u.child_nodes, key=lambda child_node: child_node.MBR['y2'])]
            for divide in divides:
                for i in range(math.ceil(0.4 * B), m - math.ceil(0.4 * B) + 1):
                    s1 = Node()
                    s1.child_nodes = divide[0: i]
                    self.update_mbr(s1)
                    s2 = Node()
                    s2.child_nodes = divide[i: divide.__len__()]
                    self.update_mbr(s2)
                    if best_perimeter > s1.perimeter() + s2.perimeter():
                        best_perimeter = s1.perimeter() + s2.perimeter()
                        best_s1 = s1
                        best_s2 = s2

        for child in best_s1.child_nodes:
            child.parent = best_s1
        for child in best_s2.child_nodes:
            child.parent = best_s2

        return best_s1, best_s2

    def add_child(self, node, child):
        node.child_nodes.append(child)
        child.parent = node
        # self.update_mbr(node)
        if child.MBR['x1'] < node.MBR['x1']:
            node.MBR['x1'] = child.MBR['x1']
        if child.MBR['x2'] > node.MBR['x2']:
            node.MBR['x2'] = child.MBR['x2']
        if child.MBR['y1'] < node.MBR['y1']:
            node.MBR['y1'] = child.MBR['y1']
        if child.MBR['y2'] > node.MBR['y2']:
            node.MBR['y2'] = child.MBR['y2']

    def add_data_point(self, node, data_point):
        node.data_points.append(data_point)
        # self.update_mbr(node)
        if data_point['x'] < node.MBR['x1']:
            node.MBR['x1'] = data_point['x']
        if data_point['x'] > node.MBR['x2']:
            node.MBR['x2'] = data_point['x']
        if data_point['y'] < node.MBR['y1']:
            node.MBR['y1'] = data_point['y']
        if data_point['y'] > node.MBR['y2']:
            node.MBR['y2'] = data_point['y']

    def update_mbr(self, node):
        # print("update_mbr")
        x_list = []
        y_list = []
        if node.is_leaf():
            x_list = [point['x'] for point in node.data_points]
            y_list = [point['y'] for point in node.data_points]
        else:
            x_list = [child.MBR['x1'] for child in node.child_nodes] + [child.MBR['x2'] for child in node.child_nodes]
            y_list = [child.MBR['y1'] for child in node.child_nodes] + [child.MBR['y2'] for child in node.child_nodes]
        new_mbr = {
            'x1': min(x_list),
            'x2': max(x_list),
            'y1': min(y_list),
            'y2': max(y_list)
        }
        node.MBR = new_mbr




