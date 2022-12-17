"""
Contains the `SecretStorage` class, to save and fetch secrets using the peewee library.
"""

from typing import Optional

from peewee import CharField, IntegrityError, Model, SqliteDatabase

db = SqliteDatabase(None)


class SecretStorage:
    """
    Uses the `peewee` library to save and fetch secrets from an SQL database.
    """

    def __init__(self):
        global db
        db.init("data/secrets.db")
        db.connect()
        db.create_tables([GitHubSecret])

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

    def __str__(self):
        return f"({self.repository}) — {self.secret}"
