from typing import List


class Solution:
    def exist(self, board: List[List[str]], word: str) -> bool:

        # 定义查找的四个方向
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        # 维护一个与 board 等大的visited 数组，用于标识每个位置是否被访问过
        visited = set()

        # 深度优先搜索
        def dfs(i: int, j: int, idx: int) -> bool:
            # 1. 边界条件，二维数组中的当前字符与输入的字符串中的当前字符不匹配
            if board[i][j] != word[idx]:
                return False
            # 2. 在二维数组中找到了匹配的字符串
            if idx == len(word) - 1:
                return True
            # 用于标识每个位置是否被访问过
            visited.add((i, j))
            result = False
            # 3. 从四个方向进行深度优先搜索
            for di, dj in directions:
                newi, newj = i + di, j + dj
                # 边界条件，防止数组角标越界
                if 0 <= newi < len(board) and 0 <= newj < len(board[0]):
                    # 判断在二位数组中该位置的元素是否被访问过
                    if (newi, newj) not in visited:
                        # 递归调用深度优先搜索
                        if dfs(newi, newj, idx + 1):
                            result = True
                            break
            # 回溯
            visited.remove((i, j))
            return result

        # 在二位数组中遍历搜索指定字符串
        for i in range(len(board)):
            for j in range(len(board[0])):
                if dfs(i, j, 0):
                    return True

        return False
