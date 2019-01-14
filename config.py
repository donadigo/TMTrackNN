import os
import json

def load_config(config_path):
    d = os.path.dirname(config_path)
    config = json.loads(open(config_path, 'r').read())
    config['train_data'] = os.path.join(d, config['train_data'])
    config['pattern_data'] = os.path.join(d, config['pattern_data'])
    config['position_scaler'] = os.path.join(d, config['position_scaler'])
    return config