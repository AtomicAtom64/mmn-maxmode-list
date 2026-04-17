from get_docs import get_main_list
from get_modes import get_modes

if __name__ == "__main__":
    texts = get_main_list()
    get_modes(texts, "main_list")