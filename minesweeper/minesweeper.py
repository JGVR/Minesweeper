import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        #all cells are mines if the number of cells match the count
        if len(self.cells) == self.count:
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        #all cells are safe if the count for those cells is 0
        if self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        #if the cell is in the sentence, remove it and decrement the count
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        #if the cell is in the sentence, remove it
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        
        #mark cell as a made move
        self.moves_made.add(cell)

        #mark cell as safe and update any sentence contain the cell
        self.safes.add(cell)

        for sentence in self.knowledge:
            sentence.mark_safe(cell)

        #Create sentence that will contain the undetermined neighbors of cell with the appropriate count
        neighbors = []

        #check what cells are neighbors of cell based on cell's position
        for row in range(cell[0] - 1, cell[0] + 2):
            for col in range(cell[1] - 1, cell[-1] + 2):
                #check if current row and col point to cell, if so go to next iter
                if (row, col) == cell:
                    continue
                    
                # Check if current row and col are within bounds
                if 0 <= row < self.height and 0 <= col < self.width:
                    #ensure current neighbors are not marked as safe or mines
                    if (row, col) not in self.mines or (row, col) not in self.safes:
                        neighbors.append((row, col))
        
        #create sentence and add it to knowledge
        if len(neighbors) > 0:
            sentence = Sentence(neighbors, count)
            self.knowledge.append(sentence)

        #check if any new cells can be marked as safe or as mines based on each sentence in knowledge
        self.mark_safe_or_mine()

        #check if based on any of the sentences in self.knowledge, new cells can be marked as safe or as mines
        for i in range(len(self.knowledge)):
            current_sentence = self.knowledge[i]

            for j in range(len(self.knowledge)):
                next_sentence = self.knowledge[j]

                #check if current and next sentence are the same
                if next_sentence == current_sentence:
                    continue

                # > compare current sentence to other sentences to see if it leads to new knowledge
                # > new knowledge in this case is if we can remove a cell from current sentence cells based on if we know that the cell is safe or a mine
                # > first, lets check if next sentence's cells are safe or mines before adding or modifying the knowledge base
                if next_sentence.known_mines():
                    #check to see if any cells in current sentence is present in next sentence
                    for cell in set(current_sentence.cells):
                        #if cell is present in next_sentence's mark it as mine
                        if cell in next_sentence.cells:
                            current_sentence.mark_mine(cell)
                        
                        #also, add cell to self.mines
                        if cell not in self.mines:
                            self.mines.add(cell)
                
                if next_sentence.known_safes():
                    #check to see if any cells in current_sentence is present in next_sentence
                    for cell in set(current_sentence.cells):
                        #if cell is present in next_sentence's cells mark it as safe
                        if cell in next_sentence.cells:
                            current_sentence.mark_safe(cell)

                        #also, add cell to self.mines
                        if cell not in self.mines:
                            self.mines.add(cell)


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        #loop over knowledge to get all sentences
        for sentence in self.knowledge:
            #check if the cells in sentence are safe
            if sentence.known_safes():
                for cell in sentence.cells:
                    #check if the cell has already been explored by checking moves_made, if no return cell and exit
                    if cell not in self.moves_made:
                        return cell


    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        #loop over knowledge to get all sentences
        for sentence in self.knowledge:
            #check if are not mines
            if not sentence.known_mines():
                for cell in sentence.cells:
                    #check if the cell has already been explored by checking moves_made, if no return cell and exit
                    if cell not in self.moves_made:
                        return cell
        
        #if no moves made, make a random move
        if len(self.moves_made) == 0:
            while True:
                row = random.randint(0, self.height - 1)
                col = random.randint(0, self.width - 1)
                if (row, col) not in self.moves_made and (row, col) not in self.mines:
                    return (row, col)
    
    def mark_safe_or_mine(self):
        """
        Marks a cell as safe or as a mine if it can be concluded based on the AI's knowledge base.
        """
        #check if any new cells can be marked as safe or as mines based on each sentence in knowledge
        for sentence in self.knowledge:
            #check for cells known to be mines, add it to self.mines as long as it is not already in self.mines
            if sentence.known_mines():
                for cell in sentence.cells:
                    if cell not in self.mines:
                        self.mines.add(cell)
            
            #check for cells known to be safe, add it to self.sages as long as it is not already in self.safes
            if sentence.known_safes():
                for cell in sentence.cells:
                    if cell not in self.safes:
                        self.safes.add(cell)
