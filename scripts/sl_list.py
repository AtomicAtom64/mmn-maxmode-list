from get_docs import get_sl_list
from get_modes import get_modes

if __name__ == "__main__":
    texts = get_sl_list()
    get_modes(texts, "sl_list")