import os
import json

class DependencyLinker:
    def __init__(self, dependency_file='./job_dependencies.json'):
        self.dependency_file = dependency_file
        self.load_dependencies()

    def load_dependencies(self):
        if os.path.exists(self.dependency_file):
            with open(self.dependency_file, 'r') as f:
                self.dependencies = json.load(f)
                for job in self.dependencies:
                    if isinstance(self.dependencies[job], str):
                        self.dependencies[job] = [self.dependencies[job]]
        else:
            self.dependencies = {}
            self.save_dependencies()

    def save_dependencies(self):
        with open(self.dependency_file, 'w') as f:
            json.dump(self.dependencies, f, indent=4)

    def add_job_id(self, job_name, job_id):
        self.dependencies[job_name] = [job_id]  # Ensure the latest job ID overwrites any previous ID
        self.save_dependencies()

    def append_job_id(self, job_name, job_id):
        if job_name not in self.dependencies:
            self.dependencies[job_name] = []
        if isinstance(self.dependencies[job_name], str):
            self.dependencies[job_name] = [self.dependencies[job_name]]
        self.dependencies[job_name].append(job_id)
        self.save_dependencies()

    def get_dependencies(self, job_name):
        return self.dependencies.get(job_name, [])

    def clear_dependencies(self, job_name):
        if job_name in self.dependencies:
            self.dependencies[job_name] = []
            self.save_dependencies()
