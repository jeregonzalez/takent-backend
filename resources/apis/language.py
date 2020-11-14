from flask_restful import Resource

from database.models.parametric_docs import Language, LanguageLevel


class LanguageApi(Resource):
    def get(self):
        return Language.objects.order_by('+name')


class LanguageLevelApi(Resource):
    def get(self):
        language_levels = []
        for language_level in LanguageLevel.objects:
            language_levels.append(language_level)
        return language_levels
