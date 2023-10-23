from tqdm import tqdm
from multiprocessing import Pool

def process_function(x):
    # Do something here
    return x

if __name__ == '__main__':
    with Pool(processes=4) as pool:
        result = list(tqdm(pool.imap(process_function, range(100)), total=100))
