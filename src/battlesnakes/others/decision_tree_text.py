
algorithm = """

BEGIN = env_1_vs_1?
    env_1_vs_1+ = env_mine_bigger?
        env_mine_bigger+ = no_danger?
            no_danger+ = food
                food = env_food_near?
                    env_food_near+ = get_food
                        get_food = routine_move!
                    env_food_near- = chase_tail
                        chase_tail = see_my_tail?
                            see_my_tail+ = chase_my_tail
                                chase_my_tail = routine_move!
                            see_my_tail- = see_enemy_tail?
                                see_enemy_tail+ = chase_enemy_tail
                                    chase_enemy_tail = routine_move!
                                see_enemy_tail- = no_tail
                                    no_tail = routine_move!
            no_danger- = routine_move!
        env_mine_bigger- = env_less_than_8?
            env_less_than_8+ = env_lt8_smaller?
                env_lt8_smaller+ = env_lt8_enemy_far?
                    env_lt8_enemy_far+ = env_lt8_food_1?
                        env_lt8_food_1+ = eat!
                        env_lt8_food_1- = env_food_near?
                            env_food_near+ = goto_food!
                            env_food_near- = routine_move!

                    ##################
                    env_lt8_enemy_far- = env_lt8_food_1?
                env_lt8_smaller- = env_food_near?
            env_less_than_8- = env_lt8_smaller?
    env_1_vs_1- = env_1_vs_n
        env_1_vs_n = routine_move!

"""

