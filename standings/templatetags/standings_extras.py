from django import template
import standings.utils
from django.conf import settings
from django.utils.safestring import mark_safe
import textwrap

register = template.Library()


def position_display(result):
    if result is None:
        return '-'

    original_position = result.position
    shown_position = result.position
    if result.race_penalty_dsq:
        shown_position = -2
    elif result.dnf_reason == "DNS":
        shown_position = -3
    elif result.dnf_reason and result.race.season.classification_type != '':
        shown_position = -1

    special_positions = {
        None: '-',
        0: '-',
        -1: 'DNF',
        -2: 'DSQ',
        -3: 'DNS'
    }

    if shown_position == -1 and result.classified:
        return f"{original_position}*"

    return special_positions.get(shown_position, result.position)


def position_colour(result, season):
    if result.race.point_system:
        ps = result.race.point_system.to_dict()
    else:
        ps = season.point_system.to_dict()

    colours = get_colours(len(ps) + 1)

    return "pos-{}".format(str(colours.get(result.position, 'blue')))


@register.filter(name='show_bullet')
def show_bullet(result, season):
    content = ""
    if result is not None:
        if result.race.point_system:
            ps = result.race.point_system.to_dict()
        else:
            ps = season.point_system.to_dict()

        try:
            if result.team_points_allocated and result.position in ps:
                content = mark_safe('&bull;')
        except AttributeError:
            pass

    return content


@register.filter(name='pos_colour')
def pos_colour(position, season):
    colours = get_colours(len(season.point_system.to_dict()) + 1)

    return "pos-{}".format(str(colours.get(position, 'blue')))


def get_colours(place_count):
    colours = {
        '-': 'default',
        0: 'default',
        1: 'yellow',
        2: 'gray',
        3: 'orange',
        'Ret': 'retired',
        'DSQ': 'black',
        'DNS': 'default'
    }

    colours.update({x: 'green' for x in range(4, place_count)})

    return colours


@register.filter(name='find_result')
def find_result(results, race):
    try:
        result = [result for result in results if result.race_id == race.id][0]
    except IndexError:
        result = None
    return result


@register.filter(name='find_driver')
def find_driver(results, driver):
    try:
        result = [result for result in results if result.driver_id == driver.id][0]
    except IndexError:
        result = None
    return result


@register.filter(name='find_results')
def find_results(results, race):
    return [result for result in results if result.race_id == race.id]


@register.filter(name='get_position')
def get_position(result):
    return position_display(result)


@register.filter(name='get_points')
def get_points(results, season):
    if len(results) == 0:
        return 0

    points = 0
    ps = season.point_system.to_dict()
    for result in results:
        if result.race.point_system:
            ps = result.race.point_system.to_dict()
        points += ps.get(result.position, 0)

    return points


@register.filter(name='format_time')
def format_time(seconds):
    return standings.utils.format_time(seconds)


@register.filter(name='format_float')
def format_float(num):
    return standings.utils.format_float(num)


@register.filter(name='get_css_classes')
def get_css_classes(result, season):
    ret = []

    if result is not None:
        if result.race_penalty_dsq:
            ret.append('pos-black')
        elif result.dnf_reason and not result.classified:
            ret.append('pos-retired')
        else:
            ret.append(position_colour(result, season))

        if result.qualifying == 1:
            ret.append("pole-position")
        if result.fastest_lap:
            ret.append("fastest-lap")
    else:
        ret.append('pos-default')

    return " ".join(ret)


@register.filter(name='collate_notes')
def collate_notes(result):
    notes = []

    if result is not None:
        if result.note != '' and result.note is not None:
            notes.append(result.note)

        if result.race_penalty_description != '' and result.race_penalty_description is not None:
            notes.append("R: {}".format(result.race_penalty_description))

        if result.qualifying_penalty_description != '' and result.qualifying_penalty_description is not None:
            notes.append("Q: {}".format(result.qualifying_penalty_description))

        if result.subbed_by is not None:
            notes.append(
                '{} reserved for {}'.format(result.subbed_by.name, result.driver.name)
            )

        if result.allocate_points is not None:
            notes.append(
                'WCC points allocated to {}'.format(result.allocate_points.name)
            )

    note = textwrap.shorten('; '.join([n for n in notes if n is not None]), width=100)
    return note


@register.filter(name='admin_breadcrumb')
def admin_breadcrumb(breadcrumb):
    return 'admin:standings_{}_changelist'.format(breadcrumb['url'])


@register.filter(name='show_flag')
def show_flag(country):
    if country in settings.COUNTRIES_OVERRIDE:
        return mark_safe('<img src="{}" title="{}"/>'.format(country.flag, country.name))
    else:
        return mark_safe('<i class="{}" title="{}"></i>'.format(country.flag_css, country.name))


@register.filter(name='munge_points')
def munge_points(points):
    return '0' if points == '' else points


@register.filter(name='find_position')
def find_position(stats, pos):
    try:
        count = stats[pos]
    except KeyError:
        count = 0
    return count


@register.filter(name='compound')
def compound(name):
    return f'tyre_{name}.png'


@register.filter(name='compound_title')
def compound_title(name, length=0):
    if length > 0:
        return f"{name.replace('_', ' ').title()} ({length})"
    else:
        return f"{name.replace('_', ' ').title()}"


@register.filter(name='find_driver_compound')
def find_driver_compound(results, driver_id):
    if driver_id not in results:
        return ''

    img = '<div class="tyre-container">' \
          '<img src="{static}{src}" width="25" title="{title}">' \
          '<div class="tyre-text">{stint}</div></div>'

    images = []
    for entry in results[driver_id]:
        if 'compound' in entry and 'lap_count' in entry and entry['compound'] != '':
            images.append(img.format(
                static=settings.STATIC_URL,
                src=compound(entry['compound']),
                title=compound_title(entry['compound'], entry['lap_count']),
                stint=entry['lap_count'])
            )

    return mark_safe(''.join(images))


@register.filter(name='find_driver_qcompound')
def find_driver_qcompound(results, driver_id):
    if driver_id not in results:
        return ''

    img = '<img src="{static}{src}" width="25" title="{title}" />'

    image = img.format(
        static=settings.STATIC_URL,
        src=compound(results[driver_id]['compound']),
        title=compound_title(results[driver_id]['compound'])
    )

    return mark_safe(image)


@register.filter(name='find_diff')
def find_diff(laps, driver_id):
    return round(laps[driver_id]['diff'], 3) if driver_id in laps else 0


@register.filter(name='find_driver_pitstops')
def find_driver_pitstops(results, driver_id):
    if driver_id not in results:
        return ''

    tyre = '<div class="tyre-blob tyre-blob-{compound}">&nbsp;</div>'
    pit = '<div class="ui center aligned tyre-blob tyre-blob-{compound} tyre-blob-pitstop">{lap_number}</div>'

    laps = []
    for entry in results[driver_id]:
        compound = entry[0].replace("_", "-")
        if entry[1]:
            laps.append(pit.format(compound=compound, lap_number=entry[2]))
        else:
            laps.append(tyre.format(compound=compound))

    return mark_safe(''.join(laps))
