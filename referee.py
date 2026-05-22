# referee.py
from settings import PIECES_DATA

def get_piece_info(piece_name):
    """Helper to extract English description and Rank from settings."""
    for item in PIECES_DATA:
        if item[0] == piece_name:
            return item[1], item[3] # Returns (Rank, English Name)
    return 0, "Unknown"

def adjudicate_combat(attacker, defender):
    """
    Evaluates Junqi combat rules and returns a tuple:
    (Outcome_String, Log_Message_String)
    
    Outcomes: "ATTACKER_WINS", "DEFENDER_WINS", "BOTH_DIE", "GAME_OVER"
    """
    att_rank, att_desc = get_piece_info(attacker.name)
    def_rank, def_desc = get_piece_info(defender.name)
    
    match_up_text = f"Combat! {attacker.player}'s {att_desc} attacked {defender.player}'s {def_desc}."

    # Priority 1: The Bomb (Mutually Assured Destruction)
    if attacker.name == "炸弹" or defender.name == "炸弹":
        return "BOTH_DIE", f"{match_up_text} BOOM! Both pieces were destroyed."

    # Priority 2: The Flag (Game Over)
    if defender.name == "军旗":
        return "GAME_OVER", f"{match_up_text} The Flag is captured! {attacker.player} wins the game!"

    # Priority 3 & 4: The Mine
    if defender.name == "地雷":
        if attacker.name == "工兵":
            # Engineer defuses the mine
            return "ATTACKER_WINS", f"{match_up_text} The Engineer successfully defused the Mine."
        else:
            # Per your requested rule: Both go down together
            return "BOTH_DIE", f"{match_up_text} The piece triggered the Mine! Both were destroyed."

    # Priority 5: Standard Rank Combat (9 down to 1)
    if att_rank > def_rank:
        return "ATTACKER_WINS", f"{match_up_text} Higher rank prevails! {attacker.player} wins."
    elif att_rank < def_rank:
        return "DEFENDER_WINS", f"{match_up_text} The attack failed. {defender.player} defended successfully."
    else:
        # Equal ranks destroy each other
        return "BOTH_DIE", f"{match_up_text} Ranks are equal. Both pieces fall in battle."