import os
from itertools import product

os.environ['MKL_THREADING_LAYER'] = 'GNU'
import yaml
import subprocess
import comet_ml

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


def parse_config_file(cfg_path: str = ".\config.yaml", keys=None, values=None):
    with open(cfg_path, 'r') as cfg_file:
        config_dict = yaml.safe_load(cfg_file)

    cmd = "yolo "
    for key, value in config_dict.items():
        if key == "cfg" or key == "v5loader":
            continue
        elif key in keys:
            idx = keys.index(key)
            value = values[idx]

        cmd += f"{key}={value} "
    return cmd


def main():
    hparams = {
        # "copy_paste": [0., 0.25],
        # "fliplr": [0., 0.25],
        # "flipud": [0., 0.25],
        # "hsv_v": [0., 0.1, 0.25],
        # "hsv_s": [0., 0.1, 0.25],
        # "translate": [0., 0.25, 0.50],
        "lrf": [0.1, 0.05, 0.01, 0.005],
        # "bgr": [0., 0.5]
               }
    
    hparams_values = [v for k, v in hparams.items()]
    hparams_product = list(product(*hparams_values))

    print(hparams_product)
    print(len(hparams_product))

    for values in hparams_product:
        # Define your command
        cmd = parse_config_file(f"./model_files/config.yaml", list(hparams.keys()), values)

        # Execute command
        process = subprocess.Popen(cmd, shell=True)
        output, error = process.communicate()


if __name__ == "__main__":
    main()
