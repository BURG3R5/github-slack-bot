class Logger:
    """
    Logs the latest commands to `./data/logs`.
    :param N: Number of latest commands to keep.
    """

    def __init__(self, N: int):
        self.N = N

    def log_command(self, log_text: str):
        """
        Logs the latest command to `./data/logs`.
        :param log_text: Information about the latest command to be saved.
        """
        # Read
        lines = []
        with open('data/logs', 'a+') as file:
            file.seek(0)
            lines = file.readlines()

        # Update
        lines.append(log_text + '\n')
        if len(lines) > self.N:
            lines.pop(0)

        # Write
        with open('data/logs', 'w') as file:
            file.writelines(lines)
