import os

def log_subscription(sub_command):
    
    lines = []
    with open('.log', 'r') as fp:
        lines = fp.readlines()
    if len(lines) >= os.environ['X']:
        with open(".log", 'w') as fp:
            for number, line in enumerate(lines):
                if number !=0:
                    fp.write(line)

        with open('.log', 'a') as fp:
            fp.write(sub_command)
    else : 
        with open('.log', 'a') as fp:
            fp.write(sub_command)