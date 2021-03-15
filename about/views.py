from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Здесь можно произвести какие-то действия для создания контекста.
        # Для примера в словарь просто передаются две строки
        context['author'] = 'Автор проекта - Алексей Лобарев.'
        context['github'] = (
            '<a href="https://github.com/loskuta42/">'
            'Ссылка на github</a>'
        )
        return context


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Здесь можно произвести какие-то действия для создания контекста.
        # Для примера в словарь просто передаются две строки
        context['pycharm'] = 'Сайт написан при использовании Pycharm.'
        context['tech'] = 'А так же модели, формы, декораторы и многое другое'
        return context
