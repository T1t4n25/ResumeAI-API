import os
import warnings

# Suppress specific warnings
os.environ['GRPC_VERBOSITY'] = 'ERROR'
warnings.filterwarnings("ignore", category=DeprecationWarning)