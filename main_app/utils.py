def teams_right_order(team_1, team_2):
    ordered_teams = [team_1, team_2]
    ordered_teams.reverse()

    is_reverse = False
    if team_1 != ordered_teams[0]:
        is_reverse = True

    return ordered_teams[0], ordered_teams[1], is_reverse
