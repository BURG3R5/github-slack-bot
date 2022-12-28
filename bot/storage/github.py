"""
Contains the `GitHubStorage` class, to save and fetch secrets using the peewee library.
"""

from typing import Optional

from peewee import CharField, IntegrityError, Model, SqliteDatabase

db = SqliteDatabase(None)


class GitHubStorage:
    """
    Uses the `peewee` library to save and fetch secrets from an SQL database.
    """

    def __init__(self):
        global db
        db.init("data/github.db")
        db.connect()
        db.create_tables([GitHubSecret, User])

    def add_secret(
        self,
        repository: str,
        secret: str,
        force_replace: bool = False,
    ) -> bool:
        """
        Creates or updates a secret object in the database.

        :param repository: Unique identifier of the GitHub repository, of the form "<owner-name>/<repo-name>"
        :param secret: Secret used by the webhook in the given repo
        :param force_replace: Whether in case of duplication the old secret should be overwritten

        :return: `False` in case an old secret was found for the same repository, `True` otherwise.
        """

        try:
            GitHubSecret\
                .insert(repository=repository, secret=secret)\
                .execute()
            return True
        except IntegrityError:
            if force_replace:
                GitHubSecret\
                    .insert(repository=repository, secret=secret)\
                    .on_conflict_replace()\
                    .execute()
            return False

    def get_secret(self, repository: str) -> Optional[str]:
        """
        Queries the `secrets` database.

        :param repository: Unique identifier for the GitHub repository, of the form "<owner-name>/<repo-name>"

        :return: Result of query, either a string secret or `None`.
        """

        results = GitHubSecret\
            .select()\
            .where(GitHubSecret.repository == repository)

        if len(results) == 1:
            return results[0].secret

        return None

    def add_user(
        self,
        slack_user_id: str,
        github_user_name: str,
        force_replace: bool = False,
    ):
        """
        Creates or updates a user object in the database.

        :param slack_user_id: Unique identifier of the Slack User-id.
        :param github_user_name: Unique identifier of GitHub User-name.
        :param force_replace: Whether in case of duplication the old user should be overwritten.
        """

        try:
            User\
                .insert(slack_user_id=slack_user_id, github_user_name=github_user_name)\
                .execute()
        except IntegrityError:
            if force_replace:
                User\
                    .insert(slack_user_id=slack_user_id, github_user_name=github_user_name)\
                    .on_conflict_replace()\
                    .execute()

    def get_slack_id(self, github_user_name) -> Optional[str]:
        """
        Queries the `user` database for `slack_user_id` corresponding to given GitHub user-name.

        :param github_user_name: Unique identifier for the GitHub User-name.

        :return: Result of query, Slack user-id corresponding to given GitHub user-name.
        """

        user = User\
                    .get_or_none(User.github_user_name == github_user_name)
        if user is not None:
            return user.slack_user_id
        return None

    def remove_user(self, slack_user_id: str = "", github_user_name: str = ""):
        """
        Deletes the `user` entry having the given `slack_user_id` or `github_user_name` (only one is required).

        :param slack_user_id: Slack user-id of the entry which is to be deleted.
        :param github_user_name: GitHub user-name of the entry which is to be deleted.
        """

        if slack_user_id != "":
            User\
                .delete()\
                .where(User.slack_user_id == slack_user_id)\
                .execute()
        elif github_user_name != "":
            User\
                .delete()\
                .where(User.github_user_name == github_user_name)\
                .execute()


class GitHubSecret(Model):
    """
    A peewee-friendly model that represents a repository-secret pair to be used when receiving webhooks from GitHub.

    :keyword repository: Unique identifier for the GitHub repository, of the form "<owner-name>/<repo-name>"
    :keyword secret: Secret used by the webhook in the given repo
    """

    repository = CharField(unique=True)
    secret = CharField()

    class Meta:
        database = db
        table_name = "GitHubSecret"

    def __str__(self):
        return f"({self.repository}) — {self.secret}"


class User(Model):
    """
    A peewee-friendly model that represents a mapping between Slack user-id and GitHub user-name.

    :keyword slack_user_id: Unique identifier for Slack user-id.
    :keyword github_user_name: Unique identifier for GitHub user-name.
    """

    slack_user_id = CharField(unique=True)
    github_user_name = CharField(unique=True)

    class Meta:
        database = db
        table_name = "User"

    def __str__(self):
        return f"{self.github_user_name} - {self.slack_user_id}"
