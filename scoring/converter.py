from sr.comp.scorer import Converter as BaseConverter


class Converter(BaseConverter):
    def form_team_to_score(self, form, zone_id):
        left_scoring_zone = form.get('left_scoring_zone_{}'.format(zone_id))
        return {
            **super().form_team_to_score(form, zone_id),
            'left_scoring_zone': left_scoring_zone is not None,
        }

    def score_to_form(self, score):
        form = super().score_to_form(score)

        for info in score['teams'].values():
            zone_id = info['zone']
            form['left_scoring_zone_{}'.format(zone_id)] = info.get(
                'left_scoring_zone',
                False,
            )

        return form

    def match_to_form(self, match):
        form = super().match_to_form(match)

        for zone_id, tla in enumerate(match.teams):
            if tla:
                form['left_scoring_zone_{}'.format(zone_id)] = False

        return form
