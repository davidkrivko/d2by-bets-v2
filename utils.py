from config import WORD_BLACK_LIST


def update_team_name(team: str):
    team = team.strip().lower()

    for word in WORD_BLACK_LIST:
        team = team.replace(word, "")

    return team.strip()


def teams_right_order(team_1, team_2):
    if team_1 < team_2:
        return team_1, team_2, False
    else:
        return team_2, team_1, True
