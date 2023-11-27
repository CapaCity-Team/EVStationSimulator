import math, logging, os, json

# Default directory path
DEFAULT_DIRECTORY_PATH = None

# Function to set the directory path
def create_directory_path(path):
    global DEFAULT_DIRECTORY_PATH
    
    # se non esiste nessuna cartella per i risultati, crea la cartella result_0
    # altrimenti crea la cartella result_n+1
    i = 0
    while os.path.exists(os.path.join(path, "simulation_{}".format(i))):
        i += 1
    path = os.path.join(path, "simulation_{}".format(i))
    os.makedirs(path)
    
    DEFAULT_DIRECTORY_PATH = path
    return path

# Function to get the current directory path
def get_directory_path():
    return DEFAULT_DIRECTORY_PATH

def find_index_nearest_k_points(center: tuple, radius: float, points: list, k: int):
    # Find the index of the point in the list of points that is closest to the circle defined by the center and the radius
    distances = [abs(math.dist(center, point) - radius) for point in points]
    # Sort the distances and get the first k indexes
    return sorted(range(len(distances)), key=lambda k: distances[k])[:k]

# Logging
LOGGER = None

def log(message, level=logging.INFO):
    global LOGGER
    if LOGGER is not None:
        LOGGER.log(level, message)

def setup_logger(log_filename):
    global LOGGER

    # Set the log level for the root logger
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a FileHandler and set the log file name
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Get the root logger and add the file handler
    LOGGER = logging.getLogger()
    LOGGER.addHandler(file_handler)

    # Remove the console handler to disable console output
    for handler in LOGGER.handlers:
        if isinstance(handler, logging.StreamHandler):
            LOGGER.removeHandler(handler)

def load_config(config_path):
    try:
        with open(config_path, 'r') as file:
            config_data = json.load(file)
    except FileNotFoundError:
        raise Exception(f'File {config_path} not found')
    except json.decoder.JSONDecodeError:
        raise Exception(f'File {config_path} is not a valid JSON file')
    except Exception as e:
        raise e
    
    return config_data
