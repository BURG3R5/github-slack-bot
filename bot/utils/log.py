class Logger:
    """
    Logs the latest commands to `.log` file.
    :param N: Number of latest commands to keep.
    """

    def __init__(self, N: int):
        self.N = N

    def log_command(self, log_text: str):
        """
        Logs the latest command to `.log` file.
        :param log_text: Information about the latest command to be saved.
        """
        # Read
        lines = []
        with open('.log', 'r') as file:
            lines = file.readlines()

        # Update
        lines.append(log_text + '\n')
        if len(lines) > self.N:
            lines.pop(0)

        # Write
        with open('.log', 'w') as file:
            file.writelines(lines)
