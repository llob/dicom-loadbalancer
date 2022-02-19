#!python3
#
# TODO:
# - Buffer implementation
# - Stoppable thread implementation
# - Pylint cleaning
# - Mypy in github workflow
# - Docker containerization
# - JSON Schema validation of configuration

# Done:
# - SCP/SCU configuration handling  ✅
# - SCU implementations             ✅
# - Liveness checker                ✅
# - Structured logging              ✅
# - Configuration loading           ✅

import logging
import argparse
import pathlib
import os.path
import sys

import dicom_loadbalancer
import configuration

def default_config_file_path() -> str:
    return pathlib.Path(__file__).parent.absolute().joinpath('config.json').resolve()

def process_config_file_path(args: argparse.Namespace) -> str:
    config_file_path = default_config_file_path()
    if 'config_file_path' not in args:
        logging.info('No config-file-path specified, using {}'.format(config_file_path))
    config_file_path = args.config_file_path
    if not os.path.isfile(config_file_path):
        logging.error('Config file {} does not exist'.format(config_file_path))
        sys.exit(1)
    return config_file_path

def configure_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG, 
        format='%(asctime)s %(name)-20s %(levelname)-8s %(message)s')
    logging.info('Starting DICOM loadbalancer')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument(
        '--config-file-path', 
        required=False, 
        type=str,
        help='Path to configuration file')
    args = parser.parse_args()

    configure_logging()

    config_file_path = process_config_file_path(args)

    config = configuration.Configuration(config_file_path)

    load_balancer = dicom_loadbalancer.DicomLoadBalancer(config)
    # Blocking call
    load_balancer.start()