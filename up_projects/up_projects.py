import os
from os import path
import git


class ProjectsDir(object):
    def __init__(self, projects_dir):
        path_expanded = path.expanduser(projects_dir)
        self.projects_dir = path.abspath(path_expanded)

    def get_projects(self) -> list:
        projects = []

        for entry in os.listdir(self.projects_dir):
            entry_path = path.join(self.projects_dir, entry)

            if path.isdir(entry_path):
                project = Project(entry_path)
                projects.append(project)

        return projects


class Project(object):
    def __init__(self, project_dir):
        self.project_dir = project_dir
        self.failed_reason = None
        self.failed = False

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    @property
    def name(self) -> str:
        return path.basename(self.project_dir)

    @property
    def is_empty(self) -> bool:
        return len(os.listdir(self.project_dir)) == 0

    @property
    def is_repo(self) -> bool:
        return bool(self.get_repo())

    @property
    def repo(self) -> git.Repo:
        return self.get_repo()

    @property
    def is_dirty(self) -> bool:
        return self.repo.is_dirty(untracked_files=True)

    def you_failed(self, reason):
        self.failed = True
        self.failed_reason = reason

    def get_repo(self) -> git.Repo:
        try:
            return git.Repo(self.project_dir)
        except git.exc.InvalidGitRepositoryError:
            return None

    def init_repo(self) -> git.Repo:
        return git.Repo.init(self.project_dir)

    def has_remote(self, remote_name) -> bool:
        return bool(self.get_remote(remote_name))

    def get_remote(self, remote_name) -> git.remote.Remote:
        try:
            return self.repo.remote(remote_name)
        except ValueError:
            return None

    def create_remote(self, remote_name, remote_url):
        self.repo.create_remote(remote_name, remote_url)

    def remove_remote(self, remote_name):
        self.repo.delete_remote(remote_name)

    def do_fetch(self, remote_name) -> bool:
        remote = self.get_remote(remote_name)
        try:
            remote.fetch()
            return True
        except git.exc.GitCommandError:
            return False

    def do_push_branches(self, remote_name) -> bool:
        remote = self.get_remote(remote_name)
        remote.push(all=True, no_verify=True)
        return True

    def do_push_tags(self, remote_name) -> bool:
        remote = self.get_remote(remote_name)
        remote.push(tags=True, no_verify=True)
        return True
