from django.core.paginator import Paginator
from django.shortcuts import render
from django.http import HttpResponse
from django.http.request import QueryDict, MultiValueDict
from django.forms.models import model_to_dict
from django.templatetags.static import static

import json
from .models import Card
from .forms import CardSearchForm

def index(request):
    if request.method == 'POST' and 'page' in request.POST:
        # stack overflow solution: https://stackoverflow.com/a/31166557/14739100
        session_data = request.session.get('post_data', {})
        session_data = MultiValueDict(session_data)
        post_data = QueryDict('', mutable=True)
        post_data.update(session_data)
    else:
        post_data = request.POST
    form = CardSearchForm(post_data or None)

    try:
        cards = form.filter_cards() if form.is_valid() else Card.objects.all()
    except Card.DoesNotExist:
        cards = None

    tab = request.POST.get('tab', 'detail')
    
    # filter `CARD_COLLECT == false`
    cards = cards.filter(collect=True)
    
    paginator = Paginator(cards, 12)
    page_total = paginator.num_pages
    page_number = request.POST.get('page', 1)
    cards = paginator.get_page(page_number)

    # update url value to static url
    for card in cards:
        card.url = static(f'card/Texture2D/CARD_{card.id}.png')
        card.frame = static(f'card/Texture2D/{card.frame}.png')
        Card.parse_to_string(card)

    context = {'card_list': cards,
               'page': page_number,
               'page_total': page_total,
               'selected_card': None,
               'form': form,
               'tab': tab}
    
    if request.method == 'POST' and 'page' in request.POST:
        for card in cards:
            card = model_to_dict(card)
            card['url'] = static(f'card/Texture2D/CARD_{card["id"]}.png')
            for key in ['skill_turn', 'skill_instance', 'skill_attack', 'skill_defend']:
                card[key] = card[key].replace('◈\n ', '◈<br/>&nbsp;')
                card[key] = card[key].replace('\n◈', '<br/>◈')
                card[key] = card[key].replace('\n ', '<br/>&nbsp;')

        return HttpResponse(render(request, 'card/index.html', context))

    # QueryDict is immutable, so save it as native dictionary
    request.session['post_data'] = dict(request.POST)
    return render(request, 'card/index.html', context)

def select(request, card_id):
    card = Card.objects.get(id=card_id)
    card = model_to_dict(card)
    card['url'] = static(f'card/Texture2D/CARD_{card_id}.png')
    card['frame'] = static(f'card/Texture2D/{card["frame"]}.png')
    Card.parse_to_string(card)
    # make space between tag
    card['tag'] = card['tag'].replace(',', ', ')

    # change text to adjust indent + newline
    for key in ['skill_turn', 'skill_instance', 'skill_attack', 'skill_defend']:
        card[key] = card[key].replace('◈\n ', '◈<br/>&nbsp;')
        card[key] = card[key].replace('\n◈', '<br/>◈')
        card[key] = card[key].replace('\n ', '<br/>&nbsp;')

    return HttpResponse(json.dumps({'selected_card': card}, ensure_ascii=False))