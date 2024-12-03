"""
Tool to print a pie chart in the terminal.
@author: Jai Wargacki
"""

import math

""" Color Constants """
RED = '\033[0;31m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
PURPLE = '\033[0;35m'
CYAN = '\033[0;36m'
END = '\033[0m'
COLORS = [RED, GREEN, YELLOW, BLUE, PURPLE, CYAN]


def create_splits(data: list) -> tuple:
    """
    Create the splits for the pie chart.
    :param data: The data to create the splits for
    :return: A tuple containing the total and the splits
    """
    total = sum([value for _, value in data])
    splits = []
    current = 0
    for _, value in data:
        current += value
        splits.append((current / total) * 360)
    return total, splits

def get_angle_of_point(x: int, y: int) -> float:
    """
    Get the angle of a point in a circle.
    :param x: The x coordinate
    :param y: The y coordinate
    :return: The angle in degrees
    """
    angle =  math.degrees(math.atan2(y, x))
    if angle < 0:
        angle += 360
    return angle

def get_char_at_point(x: int, y: int, splits: list) -> str:
    """
    Get the character at a point in a circle.
    :param x: The x coordinate
    :param y: The y coordinate
    :param splits: A list of splits in the circle
    :return: The character at the point
    """
    angle = get_angle_of_point(x, y)
    for i, split in enumerate(splits):
        if angle < split:
            return COLORS[i % len(COLORS)] + '*' + END
    return str(len(splits)) 



def get_ascii_pie(data: list, radius: int = 10, include_total: bool = True, include_key: bool = True) -> str:
    """
    Creates an ascii pie chart from the given data.
    :param data: The data to create the pie chart from list of (Author, Number of lines)
    :param radius: The radius (doubled on x axis) of the pie chart (default: 10)
    :param include_total: Whether to include the total number of lines (default: True)
    :param include_key: Whether to include the key (default: True)
    :return: The ascii pie chart as a string
    """
    total, splits = create_splits(data)
    output = '\n'
    for y in range(-radius+1, radius): # Scaled in 1 to avoid hanging single characters
        for x in range(-radius * 2, radius * 2 + 1):
            if (x / 2) ** 2 + y ** 2 <= radius ** 2:
                output += get_char_at_point(x/2, y, splits)
            else:
                output += ' '
        output += '\n'
    output += '\n'
    if include_total:
        output += 'Total Number of Lines: {}\n'.format(total)
    if include_key:
        for i in range(len(data)):
            percentage = round(data[i][1] / total * 100, 2)
            output += '\t{}{}{}: {} lines({}%)\n'.format(COLORS[i % len(COLORS)], data[i][0], END, data[i][1], percentage)
    return output
