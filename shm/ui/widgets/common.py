# from collections import deque
# import asciichartpy
# from textual.widgets import Static


# def ascii_line(data, height=8):
#     if not data:
#         return ""
#     return asciichartpy.plot(list(data), {"height": height})


# class DataBox(Static):
#     def update_data(self, title: str, data):
#         lines = [f"[b]{title}[/b]\n"]

#         if isinstance(data, list):
#             lines.extend(data)
#         elif isinstance(data, dict):
#             for k, v in data.items():
#                 lines.append(f"{k:<28} {v}")

#         self.update("\n".join(lines))


# class GraphBox(Static):
#     def update_graph(self, title: str, data: deque):
#         self.update(f"[b]{title}[/b]\n\n{ascii_line(data)}")

from collections import deque
import asciichartpy
from textual.widgets import Static


def ascii_line(data, height: int = 8):
    """
    Draw ascii chart with configurable height.
    """
    if not data:
        return ""

    return asciichartpy.plot(
        list(data),
        {
            "height": height,
            "min": 0,
        },
    )


class DataBox(Static):
    """
    Generic data renderer.
    - list[str]  → preformatted lines
    - dict       → key : value table
    """

    def update_data(self, title: str, data):
        lines = [f"[b]{title}[/b]\n"]

        if isinstance(data, list):
            lines.extend(data)

        elif isinstance(data, dict):
            for k, v in data.items():
                lines.append(f"{k:<28} {v}")

        self.update("\n".join(lines))


class GraphBox(Static):
    """
    Graph renderer with dynamic height support.
    """

    def update_graph(self, title: str, data: deque, height: int = 8):
        if not data:
            self.update(f"[b]{title}[/b]\n\n(no data)")
            return

        graph = ascii_line(data, height=height)
        self.update(f"[b]{title}[/b]\n\n{graph}")
