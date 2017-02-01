from collections import defaultdict, Counter

assignments = []


def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values


def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """

    # Find all instances of naked twins
    solved_boxes = []
    for index, box_set in enumerate(unitlist):
        if index==2:
            2+2
        # use dict for box_set
        # use a standard unitlist dict, removing solves, and generate from that link with dicts and delete to delete across rows, columns, and squares
        box_set_dict = {}
        dd = defaultdict(list)

        for box in box_set.copy():
            if len(values[box]) == 2:
                dd[values[box]].append(box)
            elif len(values[box]) == 1:
                solved_boxes.append(box)
                # box_set.remove(box)
            else:
                box_set_dict[box] = values[box]

        nakeds = [item for item in dd.items() if len(item[1]) == 2]

        if nakeds:
            for valuez, boxs in nakeds:

                for box in box_set_dict:
                    for value in valuez:
                        values[box] = values[box].replace(value, '')
                    if len(values[box]) == 1:
                        solved_boxes.append(box)
    return values


def cross(A, B):
    """Cross product of elements in A and elements in B."""
    return [a+b for b in B for a in A]


def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    assert len(grid) == 81
    return dict([(box, value.replace('.', '123456789')) for box, value in zip(boxes, grid)])

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1 + max(len(values[s]) for s in boxes)
    line = '+'.join(['-' * (width * 3)] * 3)
    for r in rows:
        print(''.join(values[r + c].center(width) + ('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print()

def eliminate(values):
    """
    Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    for box in boxes:
        if len(values[box]) == 1:
            for peer in peers[box]:
                values[peer] = values[peer].replace(values[box], '')

    return values

def only_choice(values):
    """
    Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    new_values = values.copy()  # note: do not modify original values
    # TODO: Implement only choice strategy here

    for box_set in unitlist:
        for number in '123456789':
            boxes_with_num = [box for box in box_set if number in values[box]]
            if len(boxes_with_num) == 1:
                new_values[boxes_with_num[0]] = number

    return new_values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """

    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Your code here: Use the Eliminate Strategy
        eliminate(values)

        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)

        naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):

    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function

    result = reduce_puzzle(values)
    if not result:
        return False
    elif all([len(val) == 1 for val in result.values()]):
        return result

    # Choose one of the unfilled squares with the fewest possibilities
    box, nums = min([x for x in values.items() if len(x[1]) > 1], key=lambda x: len(x[1]))

    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for num in nums:
        new_values = values.copy()
        new_values[box] = num
        next_result = search(new_values)
        if next_result:
            return next_result

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

def validate(solved_values):
    for index, unit in enumerate(unitlist):
        values = [solved_values[box] for box in unit]
        for value in values:
            assert len(value) == 1
            assert value in '123456789'
        c = Counter(values)
        assert c.most_common()[0][1]==1, "ERROR at unit {}, {}".format(index, c.most_common()[0])


rows = 'ABCDEFGHI'
cols = '123456789'
rev_cols = '987654321'


boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
diag1 = [[x for x in map(''.join, zip(rows, cols))]]
diag2 = [[x for x in map(''.join, zip(rows, rev_cols))]]
square_units = [cross(rs, cs) for rs in ('ABC', 'DEF', 'GHI') for cs in ('123', '456', '789')]
unitlist = row_units + column_units + square_units + diag1 + diag2
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s], []))-set([s])) for s in boxes)

if __name__ == '__main__':
    # diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    # display(solve(diag_sudoku_grid))

    from solution_test import TestNakedTwins

    display(TestNakedTwins.before_naked_twins_2)
    print()
    display(naked_twins(TestNakedTwins.before_naked_twins_2))
    # print()
    # display(naked_twins(TestNakedTwins.before_naked_twins_1))
    # print()
    display(TestNakedTwins.possible_solutions_2[0])
    # print()
    # display(TestNakedTwins.possible_solutions_1[1])

    # try:
    #     from visualize import visualize_assignments
    #     visualize_assignments(assignments)
    #
    # except SystemExit:
    #     pass
    # except Exception as e:
    #     print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
