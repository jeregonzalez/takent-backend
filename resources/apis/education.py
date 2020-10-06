from flask_restful import Resource

from database.models.parametric_docs import EducationLevel


class EducationLevelApi(Resource):
    def get(self):
        education_levels = []
        for education_level in EducationLevel.objects:
            education_levels.append(education_level)
        return education_levels
