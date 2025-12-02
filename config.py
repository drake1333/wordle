import os

CURRENT_USER = None
WINSTREAK_4 = 0
WINSTREAK_5 = 0
WINSTREAK_6 = 0

OPTIONS_FILE = "options.json"
DEFAULT_OPTIONS = {"theme": "Light", "font": "Default"}
DB_FILE = "appdata.db"
DAILY_WORD_FILE = "dailyword.txt"

dictionary6 = {
    1: ["lineEdit_a","lineEdit_b","lineEdit_c","lineEdit_d","lineEdit_e","lineEdit_za"],
    2: ["lineEdit_f","lineEdit_g","lineEdit_h","lineEdit_m","lineEdit_i","lineEdit_zb"],
    3: ["lineEdit_j","lineEdit_k","lineEdit_l","lineEdit_n","lineEdit_o","lineEdit_zc"],
    4: ["lineEdit_p","lineEdit_q","lineEdit_r","lineEdit_s","lineEdit_t","lineEdit_zd"],
    5: ["lineEdit_u","lineEdit_v","lineEdit_w","lineEdit_x","lineEdit_y","lineEdit_z"]
}

dictionary5 = {
    1: ["lineEdit_a","lineEdit_b","lineEdit_c","lineEdit_d","lineEdit_e"],
    2: ["lineEdit_f","lineEdit_g","lineEdit_h","lineEdit_m","lineEdit_i"],
    3: ["lineEdit_j","lineEdit_k","lineEdit_l","lineEdit_n","lineEdit_o"],
    4: ["lineEdit_p","lineEdit_q","lineEdit_r","lineEdit_s","lineEdit_t"],
    5: ["lineEdit_u","lineEdit_v","lineEdit_w","lineEdit_x","lineEdit_y"]
}

dictionary4 = {
    1: ["lineEdit_a","lineEdit_b","lineEdit_c","lineEdit_d"],
    2: ["lineEdit_f","lineEdit_g","lineEdit_h","lineEdit_m"],
    3: ["lineEdit_j","lineEdit_k","lineEdit_l","lineEdit_n"],
    4: ["lineEdit_p","lineEdit_q","lineEdit_r","lineEdit_s"],
    5: ["lineEdit_u","lineEdit_v","lineEdit_w","lineEdit_x"]
}

WORDLE_DICTIONARIES = {
    4: dictionary4,
    5: dictionary5,
    6: dictionary6,
}