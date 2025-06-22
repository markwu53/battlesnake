
algorithm = """

BEGIN = root

root = env_1_vs_1?
    env_1_vs_1+ = 1_vs_1
    env_1_vs_1- = 1_vs_n
        1_vs_n = routine_move!

1_vs_1 = env_mine_bigger?
    env_mine_bigger+ = no_danger?
        no_danger+ = food
        no_danger- = routine_move!
    env_mine_bigger- = env_less_than_8?
        env_less_than_8+ = env_lt8_smaller?
            env_lt8_smaller+ = env_lt8_enemy_far?
                env_lt8_enemy_far+ = food

                ##################
                env_lt8_enemy_far- = env_danger_1?
                    env_danger_1+ = routine_move!
                    env_danger_1- = routine_move!
            env_lt8_smaller- = env_lt8_len_eq?
                env_lt8_len_eq+ = routine_move!
                env_lt8_len_eq- = routine_move!
        env_less_than_8- = env_lt8_smaller?

food = env_food_1?
    env_food_1+ = 
    env_food_danger_1?
        env_food_danger_1+ = env_can_avoid?
            env_can_avoid+ = avoid!
            env_can_avoid- = eat!
        env_food_danger_1- = eat!
    env_food_1- = env_food_near?
        env_food_near+ = env_food_closer?
            env_food_closer+ = goto_food!
            env_food_closer- = goto_food2!
        env_food_near- = routine_move!

"""

