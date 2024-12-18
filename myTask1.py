from typing import List


class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:

        # Define the four directions of the search
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        # Maintain a large visited array, such as board, that identifies whether each location has been visited
        visited = set()

        # depth-first search
        def dfs(i: int, j: int, idx: int) -> bool:
            # 1. Boundary condition where the current character in the
            #    two-dimensional array does not match the current character in the input string
            if board[i][j] != word[idx]:
                return False
            # 2. A matching string was found in the two-dimensional array
            if idx == len(word) - 1:
                return True
            # Used to identify whether each location has been visited
            visited.add((i, j))
            result = False
            # 3. Depth-first search from four directions
            for di, dj in directions:
                newi, newj = i + di, j + dj
                # Boundary conditions that prevent array corner markers from crossing boundaries
                if 0 <= newi < len(board) and 0 <= newj < len(board[0]):
                    # Determines whether the element at that position in the 2-bit array has been accessed
                    if (newi, newj) not in visited:
                        # Recursively invoke depth-first search
                        if dfs(newi, newj, idx + 1):
                            result = True
                            break
            # Back Tracking
            visited.remove((i, j))
            return result

        # Iterates through a 2-bit array to search for the specified string
        for i in range(len(board)):
            for j in range(len(board[0])):
                if dfs(i, j, 0):
                    return True

        return False
