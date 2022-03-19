class InvalidScoresheetException(Exception):
    pass


class Scorer(object):
    def __init__(self, teams_data, arena_data):
        self._teams_data = teams_data

    def calculate_scores(self):
        raise NotImplementedError

    def validate(self, extra_data):
        raise NotImplementedError


if __name__ == '__main__':
    import libproton
    libproton.main(Scorer)
