#!python3
#
# TODO:
# - SCP/SCU configuration handling  ✅
# - SCU implementations
# - Buffer implementation
# - Liveness checker
# - Structured logging              ✅
# - Configuration loading           ✅

import dicom_loadbalancer
import configuration
import logging

logging.basicConfig(level=logging.DEBUG)
logging.info('Starting DICOM loadbalancer')

config = configuration.Configuration('test/data/config/sample-config.json')

load_balancer = dicom_loadbalancer.DicomLoadBalancer(config)
# Blocking call
load_balancer.start()