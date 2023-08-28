from django import template

register = template.Library()


@register.filter
def wrap_text(value):
    new_text = ''
    for i in range(len(value)):
        new_text += value[i]
        if i % 20 == 0 and i != 0:
            new_text += '-\n'

    # print(new_text)

    return new_text
