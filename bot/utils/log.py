import os


def log_command(log_text: str):
    """
    Logs the latest command to `.log` file.
    :param log_text: Information about the latest command to be saved.
    """
    lines = []
    with open('.log', 'r') as file:
        lines = file.readlines()
    lines.append(log_text + '\n')

    if len(lines) > 5:
        lines.pop(0)

    with open('.log', 'w') as file:
        print(lines)
        print('here')
        file.writelines(lines)
