"""
Reading Order Optimizer - Determines optimal reading order for chunks
Uses graph-based algorithm (completely free, no external dependencies)
"""
from typing import Dict, Any, List, Tuple
from collections import defaultdict, deque


class ReadingOrderOptimizer:
    """Optimizes reading order of text chunks using graph algorithms"""

    def __init__(self):
        self.y_threshold = 20  # Vertical threshold for "same line"
        self.column_gap_threshold = 50  # Minimum gap between columns

    def optimize_reading_order(
        self,
        chunks: List[Dict[str, Any]],
        layout_type: str
    ) -> List[Dict[str, Any]]:
        """
        Determine optimal reading order for chunks

        Args:
            chunks: List of text chunks with bbox info
            layout_type: 'one_column', 'two_column', 'three_column', 'complex'

        Returns:
            Chunks sorted in optimal reading order
        """
        if not chunks:
            return []

        if layout_type == 'one_column':
            # Simple top-to-bottom
            return self._simple_vertical_order(chunks)
        elif layout_type in ['two_column', 'three_column']:
            # Column-aware ordering
            return self._multi_column_order(chunks, layout_type)
        else:
            # Complex layout - use graph algorithm
            return self._graph_based_order(chunks)

    def _simple_vertical_order(self, chunks: List[Dict]) -> List[Dict]:
        """Simple top-to-bottom ordering"""
        return sorted(chunks, key=lambda c: (
            c.get('bbox', [0, 0, 0, 0])[1],  # Y coordinate
            c.get('bbox', [0, 0, 0, 0])[0]   # X coordinate (tiebreaker)
        ))

    def _multi_column_order(self, chunks: List[Dict], layout_type: str) -> List[Dict]:
        """
        Multi-column ordering: read each column top-to-bottom, then next column

        Strategy:
        1. Group chunks by column (X-coordinate clustering)
        2. Sort columns left-to-right
        3. Within each column, sort top-to-bottom
        """
        # Detect column boundaries
        columns = self._detect_columns(chunks)

        # Assign chunks to columns
        chunks_by_column = defaultdict(list)
        for chunk in chunks:
            bbox = chunk.get('bbox', [0, 0, 0, 0])
            x_center = (bbox[0] + bbox[2]) / 2

            # Find which column this belongs to
            col_idx = self._find_column(x_center, columns)
            chunks_by_column[col_idx].append(chunk)

        # Sort each column vertically
        ordered_chunks = []
        for col_idx in sorted(chunks_by_column.keys()):
            col_chunks = sorted(
                chunks_by_column[col_idx],
                key=lambda c: c.get('bbox', [0, 0, 0, 0])[1]
            )
            ordered_chunks.extend(col_chunks)

        return ordered_chunks

    def _graph_based_order(self, chunks: List[Dict]) -> List[Dict]:
        """
        Graph-based reading order for complex layouts

        Creates directed graph where edge (A→B) means "A should be read before B"
        Uses topological sort to find reading order
        """
        # Build directed graph
        graph = defaultdict(list)
        in_degree = defaultdict(int)

        # Initialize all chunks in graph
        for chunk in chunks:
            chunk_id = id(chunk)
            in_degree[chunk_id] = 0

        # Add edges based on spatial relationships
        for i, chunk_a in enumerate(chunks):
            for j, chunk_b in enumerate(chunks):
                if i == j:
                    continue

                if self._should_read_before(chunk_a, chunk_b):
                    id_a, id_b = id(chunk_a), id(chunk_b)
                    graph[id_a].append(id_b)
                    in_degree[id_b] += 1

        # Topological sort (Kahn's algorithm)
        queue = deque([id(c) for c in chunks if in_degree[id(c)] == 0])
        ordered = []

        # Create ID to chunk mapping
        id_to_chunk = {id(c): c for c in chunks}

        while queue:
            current_id = queue.popleft()
            ordered.append(id_to_chunk[current_id])

            for neighbor_id in graph[current_id]:
                in_degree[neighbor_id] -= 1
                if in_degree[neighbor_id] == 0:
                    queue.append(neighbor_id)

        # Handle cycles (shouldn't happen, but fallback to Y-sort)
        if len(ordered) < len(chunks):
            remaining = [c for c in chunks if c not in ordered]
            ordered.extend(sorted(remaining, key=lambda c: c.get('bbox', [0, 0, 0, 0])[1]))

        return ordered

    def _should_read_before(self, chunk_a: Dict, chunk_b: Dict) -> bool:
        """
        Determine if chunk A should be read before chunk B

        Rules:
        1. If A is significantly above B → A before B
        2. If A and B are on same line (Y-wise), and A is left of B → A before B
        3. If A is header/title type → A before B
        """
        bbox_a = chunk_a.get('bbox', [0, 0, 0, 0])
        bbox_b = chunk_b.get('bbox', [0, 0, 0, 0])

        y_a = (bbox_a[1] + bbox_a[3]) / 2
        y_b = (bbox_b[1] + bbox_b[3]) / 2
        x_a = (bbox_a[0] + bbox_a[2]) / 2
        x_b = (bbox_b[0] + bbox_b[2]) / 2

        # Rule 1: A is above B
        if y_a < y_b - self.y_threshold:
            return True

        # Rule 2: Same line, A is left of B
        if abs(y_a - y_b) <= self.y_threshold and x_a < x_b:
            return True

        # Rule 3: Type-based priority (header before body)
        type_priority = {'header': 0, 'title': 0, 'body': 1, 'footer': 2}
        priority_a = type_priority.get(chunk_a.get('type', 'body'), 1)
        priority_b = type_priority.get(chunk_b.get('type', 'body'), 1)

        if priority_a < priority_b and abs(y_a - y_b) < 100:
            return True

        return False

    def _detect_columns(self, chunks: List[Dict]) -> List[Tuple[float, float]]:
        """
        Detect column boundaries from chunks

        Returns:
            List of (x_start, x_end) for each column
        """
        if not chunks:
            return []

        # Get all X-center coordinates
        x_centers = [(c.get('bbox', [0, 0, 0, 0])[0] + c.get('bbox', [0, 0, 0, 0])[2]) / 2
                     for c in chunks]

        # Simple clustering by sorting and finding gaps
        x_sorted = sorted(x_centers)

        columns = []
        col_start = x_sorted[0]

        for i in range(1, len(x_sorted)):
            gap = x_sorted[i] - x_sorted[i-1]

            if gap > self.column_gap_threshold:
                # End current column, start new one
                columns.append((col_start, x_sorted[i-1]))
                col_start = x_sorted[i]

        # Add last column
        columns.append((col_start, x_sorted[-1]))

        return columns

    def _find_column(self, x: float, columns: List[Tuple[float, float]]) -> int:
        """Find which column index an X-coordinate belongs to"""
        for i, (x_start, x_end) in enumerate(columns):
            if x_start <= x <= x_end:
                return i

        # Fallback: find closest column
        distances = [min(abs(x - x_start), abs(x - x_end)) for x_start, x_end in columns]
        return distances.index(min(distances))
