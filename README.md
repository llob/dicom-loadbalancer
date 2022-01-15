# dicom-loadbalancer
Load balancing DICOM router (WORK IN PROGRESS)

The DICOM loadbalancer provides functionality for acting as any number of
DICOM SCPs and forwarding any data received (via C-STORE) to sets of configured
"worker" SCPs. As such, the DICOM loadbalancer concurrently takes on the role 
of both SCP and SCU.

The DICOM loadbalancer supports selecting workers from sets of workers, based on:
- Which SCP the data was originally sent to
- Pattern matching on DICOM headers

The DICOM loadbalancer will eventually support a pluggable system for performing
in-flight DICOM header rewrites before relaying to destination worker SCPs
