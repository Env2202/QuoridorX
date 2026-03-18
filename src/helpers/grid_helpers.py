from PyQt6.QtCore import QPointF

def grid_to_scene(row, col, cell_size):
    x = col * cell_size
    y = row * cell_size
    return QPointF(x, y)

def scene_to_grid(scene_pos, cell_size):
    row = round(scene_pos.y() / cell_size)
    col = round(scene_pos.x() / cell_size)
    return row, col
