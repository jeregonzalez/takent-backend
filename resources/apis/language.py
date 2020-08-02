from flask_restful import Resource

from database.models.common import Language, LanguageLevel


class LanguageApi(Resource):
    def get(self):
        languages = []
        for language in Language.objects:
            languages.append(language)
        return languages


class LanguageLevelApi(Resource):
    def get(self):
        language_levels = []
        for language_level in LanguageLevel.objects:
            language_levels.append(language_level)
        return language_levels
