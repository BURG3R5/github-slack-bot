import os


def log_subscription(sub_command):

    lines = []
    with open('.log', 'r') as file:
        lines = file.readlines()
    if len(lines) >= 3:
        lines.pop(0)
        lines.append(sub_command + '\n')
        with open('.log', 'w') as file:
            file.writelines(lines)
    else:
        with open('.log', 'a') as file:
            file.write(sub_command + '\n')
