#!/usr/bin/env bash
export FINGERPRINT="VOLKSWAGEN_PASSAT_MK8"
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export NUMEXPR_NUM_THREADS=1
export OPENBLAS_NUM_THREADS=1
export VECLIB_MAXIMUM_THREADS=1

if [ -z "$AGNOS_VERSION" ]; then
  export AGNOS_VERSION="11.4"
fi

export STAGING_ROOT="/data/safe_staging"
