import math, logging, os, json

# Default directory path
DEFAULT_DIRECTORY_PATH = None

# Function to set the directory path
def create_directory_path():
    global DEFAULT_DIRECTORY_PATH
    
    # se non esiste nessuna cartella per i risultati, crea la cartella result_0
    # altrimenti crea la cartella result_n+1
    i = 0
    while os.path.exists(os.path.join(os.path.dirname(__file__), "../data/simulation_result/simulation_{}".format(i))):
        i += 1
    path = os.path.join(os.path.dirname(__file__), "../data/simulation_result/simulation_{}".format(i))
    os.makedirs(path)
    
    DEFAULT_DIRECTORY_PATH = path
    return path

# Function to get the current directory path
def get_directory_path():
    return DEFAULT_DIRECTORY_PATH

def find_index_nearest_point(center: tuple, radius: float, points: list):
    # Find the index of the point in the list of points that is closest to the circle defined by the center and the radius
    distances = [abs(math.dist(center, point) - radius) for point in points]
    return distances.index(min(distances))

def setup_logger(log_filename):
    # Set the log level for the root logger
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create a FileHandler and set the log file name
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    # Get the root logger and add the file handler
    root_logger = logging.getLogger()
    root_logger.addHandler(file_handler)

    # Remove the console handler to disable console output
    for handler in root_logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            root_logger.removeHandler(handler)

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

