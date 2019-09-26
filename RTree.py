import sys
from Core_functions import RTree, sequential_query
import time

data_file = ""
queries_file = ""


def time_it(func, *args):
    start = time.time()
    result = func(*args)
    end = time.time()
    return {'result': result, 'time': (end - start)}


def construct_r_tree(data_points):
    R_tree = RTree()
    print("get here")
    temp_counter = 0
    print("\033[H\033[J")
    print("build R-Tree:\n0.0%\n", end="\r")
    for i in range(len(data_points)):
        print(i)
        if temp_counter >= len(data_points) / 1000:
            print("\033[H\033[J")
            print("build R-Tree:\n{:.1f}%\n".format(100 * i / len(data_points)), end="\r")
            temp_counter = temp_counter % (len(data_points) / 1000)
        point = data_points[i]
        R_tree.insert(point, Rect(point["x"], point["y"], point["x"], point["y"]))
        temp_counter += 1

    return R_tree


def main(args):
    if len(args) != 3:
        print("Error: Invalid numbers of arguments. Require 2 arguments.")
    else:
        data_filename = args[1]
        queries_filename = args[2]

        # Read data file
        data_file = open(data_filename, "r")
        input = data_file.read().split('\n')
        data_file.close()
        data_size = int(input[0])
        data_points = []
        for i in range(data_size):
            id, x, y = input[i + 1].split(" ")
            data_points.append({"id": id, "x": int(x), "y": int(y)})
        # Create R tree
        R_tree = construct_r_tree(data_points)

        # Read queries file
        queries_file = open(queries_filename, "r")
        input = queries_file.read().split('\n')
        queries_file.close()
        # Load and run queries
        queries = []
        time_sum_sequential = 0
        time_sum_r_tree = 0
        number_of_queries = 0
        output_file = open("./result.txt", "w+")
        results = []
        for line in input:
            if len(line.split(" ")) == 4:
                x1, x2, y1, y2 = line.split(" ")
                queries.append({"x1": int(x1), "x2": int(x2), "y1": int(y1), "y2": int(y2)})
                number_of_queries += 1
                query = queries[-1]
                # Run and time  each sequential & R tree query
                # sequential
                time_sum_sequential += time_it(sequential_query, data_points, query)['time']
                # R tree
                r_tree_run = time_it(R_tree.query_rect, Rect(query["x1"], query["y1"], query["x2"], query["y2"]))
                time_sum_r_tree += r_tree_run['time']
                results.append("{}\n".format(r_tree_run['result']))
        print('\ntotal time for sequential queries: {}'.format(time_sum_sequential))
        output_file.write('\ntotal time for sequential queries: {}\n'.format(time_sum_sequential))
        print('average time for every sequential query: {}\n'.format(time_sum_sequential / number_of_queries))
        output_file.write(
            'average time for every sequential query: {}\n\n'.format(time_sum_sequential / number_of_queries))
        print('total time for R-Tree queries: {}'.format(time_sum_r_tree))
        output_file.write('total time for R-Tree queries: {}\n'.format(time_sum_r_tree))
        print('average time for every R-Tree query: {}\n'.format(time_sum_r_tree / number_of_queries))
        output_file.write('average time for every R-Tree query: {}\n\n'.format(time_sum_r_tree / number_of_queries))
        print('R-Tree is {} times faster then sequential query'.format(time_sum_sequential / time_sum_r_tree))
        output_file.write(
            'R-Tree is {} times faster then sequential query\n\n'.format(time_sum_sequential / time_sum_r_tree))
        output_file.writelines(results)

        output_file.close()


if __name__ == "__main__":
    main(sys.argv)
