import itertools


class InvalidScoresheetException(Exception):
    pass


CAN_STATE_SCORES = {
    "B": 3,  # 3 points for can with tape on the Bottom
    "T": 1,  # 1 point for can with tape on the Top
    "S": 0,  # 0 points for can on its Side
}

MAX_CANS = 28


class Scorer(object):
    def __init__(self, teams_data, arena_data):
        self._teams_data = teams_data
        self._arena_data = arena_data

    def calculate_scores(self):
        scores = {}
        for tla, info in self._teams_data.items():
            zone = info['zone']
            cans = self._arena_data[zone]['tokens']
            points = sum(CAN_STATE_SCORES[c] for c in cans if c != " ")

            if info.get('left_scoring_zone', False):
                points += 1

            scores[tla] = points

        return scores

    def validate(self, extra_data):
        cans = "".join(itertools.chain.from_iterable(
            info['tokens']
            for info in self._arena_data.values()
        ))
        cans = cans.replace(" ", "")

        extra = set(cans) - set(CAN_STATE_SCORES.keys())
        if extra:
            raise InvalidScoresheetException(
                f"Invalid can state: {extra!r}. "
                f"Must be one of: {', '.join(CAN_STATE_SCORES.keys())}",
            )

        if len(cans) > MAX_CANS:
            raise InvalidScoresheetException(
                "Too many cans seen. "
                f"Must be no more than {MAX_CANS} got {len(cans)}",
            )

        # TODO: Check that teams are present if they are marked as leaving
        # their zone


if __name__ == '__main__':
    import libproton
    libproton.main(Scorer)
