import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for v in self.crossword.variables:
            for x in self.domains[v].copy():
                if v.length != len(x):
                    self.domains[v].remove(x)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        letter = set()
        overlap_pair = ()
        for var_1, var_2 in self.crossword.overlaps:
            if var_1 == x and var_2 == y:
                overlap_pair = self.crossword.overlaps[var_1, var_2]

        if overlap_pair is not None:
            for word in self.domains[y]:
                letter.add(word[overlap_pair[1]])

            for val_1 in self.domains[x].copy():
                if val_1[overlap_pair[0]] not in letter:
                    self.domains[x].remove(val_1)
                    revised = True

        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        queue = []

        if arcs is None:
            for var_1, var_2 in self.crossword.overlaps:
                queue.append((var_1, var_2))
        else:
            queue = arcs

        while len(queue) != 0:
            arc = queue.pop()
            if self.revise(arc[0], arc[1]):
                if len(self.domains[arc[0]]) == 0:
                    return False
            for val_3 in self.crossword.neighbors(arc[0]) - {arc[1]}:
                queue.append((val_3, arc[0]))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in assignment or len(assignment[var]) == 0:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        overlap_pair_1 = ()
        for var_1 in assignment:
            new_ass_1 = assignment.copy()
            new_ass_1.pop(var_1)
            for var_2 in new_ass_1:
                if assignment[var_1] == assignment[var_2]:
                    return False

            if len(list(assignment[var_1])) != var_1.length:
                return False

        for var_2 in assignment:
            new_ass_3 = assignment.copy()
            neighbors = self.crossword.neighbors(var_2)
            for neighbor in neighbors:
                if neighbor in assignment:
                    for vari_1, vari_2 in self.crossword.overlaps:
                        if vari_1 == var_2 and vari_2 == neighbor:
                            overlap_pair_1 = self.crossword.overlaps[vari_1, vari_2]

                    letter_1 = list(new_ass_3[var_2])[overlap_pair_1[0]]
                    letter_2 = list(new_ass_3[neighbor])[overlap_pair_1[1]]

                    if letter_1 != letter_2:
                        return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        choices = 0
        list_value = []
        order_list = []
        domain_values = list(self.domains[var])
        neighbours = self.crossword.neighbors(var)

        for value_1 in domain_values:
            for neighbour in neighbours:
                if neighbour not in assignment:
                    if value_1 in list(self.domains[neighbour]):
                        choices += 1
            list_value.append((value_1, choices))
            choices = 0

        list_value.sort(key=self.my_func)

        for value_2 in list_value:
           order_list.append(value_2[0])

        return order_list


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        unassigned_var_list = []
        domain_len_list = []
        min_val_list = []
        degree_list = []

        for var_1 in self.crossword.variables:
            if var_1 not in assignment:
                unassigned_var_list.append(var_1)

        for var_2 in unassigned_var_list:
            domain_len_list.append((var_2, len(self.domains[var_2])))

        domain_len_list.sort(key=self.my_func)

        for tuple in domain_len_list:
            min = domain_len_list[0][1]
            if min == tuple[1]:
                min_val_list.append(tuple[0])

        if len(min_val_list) == 1:
            value = min_val_list[0]
            return value

        for var_3 in min_val_list:
            degree_list.append((var_3, len(self.crossword.neighbors(var_3))))

        degree_list.sort(key=self.my_func, reverse=True)

        value = degree_list[0][0]

        return value

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)
        for value in self.order_domain_values(var, assignment):
            new_assignment = assignment.copy()
            new_assignment[var] = value
            if self.consistent(new_assignment):
                result = self.backtrack(new_assignment)
                if result is not None:
                  return result

        return None


    def my_func(self, tuple):
        return tuple[1]

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
