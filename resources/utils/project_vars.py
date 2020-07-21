class ProjectVars:
    project_vars = {}

    @classmethod
    def set_project_vars(cls, project_vars):
        cls.project_vars = dict(project_vars)

    @classmethod
    def get_project_var(cls, var_name):
        return cls.project_vars.get(var_name)
