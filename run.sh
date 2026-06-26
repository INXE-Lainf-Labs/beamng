#!/bin/bash
#SBATCH --job-name=beamng_simulation_run
#SBATCH --output=./data/slurm/sim_job_%j.txt
#SBATCH --error=./data/slurm/sim_job_%j.err
#SBATCH --partition=normal
#SBATCH --gres=gpu:1

echo "Job ID: $SLURM_JOB_ID"
echo "PID do bash script: $$"
echo "Starting job..."

source .venv/bin/activate 
python simulate.py --circuit c1 --speed 12 --report

echo "Finishing job..."
