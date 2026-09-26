##########################
## JOBSTATS CONFIG FILE ##
##########################

# prometheus server address, port, and retention period
PROM_SERVER = "http://muscadine-node-1.hpc.msstate.edu:8428"
PROM_RETENTION_DAYS = 365

# number of seconds between measurements
SAMPLING_PERIOD = 30

# Set to True if GPU stats have "job_id" label as opposed to "jobid"
AMD_EXPORTER_JOBID = True

# If using Slurm database then include the lines below with "enabled": False
# If using MariaDB/MySQL then set "enabled": True
# Set "mirror_to_admin_comment": True to additionally write the JS1 payload
# to the Slurm AdminComment field (sacctmgr). This preserves compatibility
# with sacct-based tools such as reportseff which read GPU/multi-node
# efficiency from AdminComment.
EXTERNAL_DB_CONFIG = {
    "enabled": False,  # set to True to use the external db for storing stats
    "host": "127.0.0.1",
    "port": 3307,
    "database": "jobstats",
    "user": "jobstats",
    "password": "password",
#     "config_file": "/path/to/jobstats-db.cnf",
#     "mirror_to_admin_comment": False,  # also write JS1 payload to AdminComment via sacctmgr
}

# translate cluster names in Slurm DB to informal names
CLUSTER_TRANS = {}  # if no translations then use an empty dictionary
CLUSTER_TRANS_INV = dict(zip(CLUSTER_TRANS.values(), CLUSTER_TRANS.keys()))

# maximum number of characters to display in jobname
MAX_JOBNAME_LEN = 64


################################################################################
##                    T E X T    C O L O R I Z A T I O N                      ##
################################################################################
GPU_UTIL_RED   = 15  # percentage
GPU_UTIL_BLACK = 25  # percentage
CPU_UTIL_RED   = 65  # percentage
CPU_UTIL_BLACK = 80  # percentage
TIME_EFFICIENCY_RED   = 10  # percentage
TIME_EFFICIENCY_BLACK = 60  # percentage
MIN_MEMORY_USAGE      = 70  # percentage
MIN_RUNTIME_SECONDS   = 10 * SAMPLING_PERIOD  # seconds


################################################################################
##                 D E T A I L E D    G P U    M E T R I C S                  ##
################################################################################
GPU_METRICS_EXPORTER = "AMD"  # choices are "None" and "AMD"
GPU_METRICS = {
    "GFX": {
        "metric": "gpu_gfx_activity",
        "operation": "avg_over_time",
        "show_overall": True,
        "show_per_gpu": True,
        "write_to_db": True,
        "long_name": "Graphics Engine Activity",
    },
    "UMC": {
        "metric": "gpu_umc_activity",
        "operation": "avg_over_time",
        "show_overall": True,
        "show_per_gpu": True,
        "write_to_db": True,
        "long_name": "Memory Controller Activity",
    },
    "PCIe RX": {
        "metric": "pcie_rx_per_sec",
        "operation": "avg_over_time",
        "show_overall": False,
        "show_per_gpu": True,
        "write_to_db": True,
        "long_name": "PCIe Bytes Received",
    },
    "PCIe TX": {
        "metric": "pcie_tx_per_sec",
        "operation": "avg_over_time",
        "show_overall": False,
        "show_per_gpu": True,
        "write_to_db": True,
        "long_name": "PCIe Bytes Transmitted",
    },
    "XGMI RX": {
        "metric": "xgmi_total_rx_per_sec",
        "operation": "avg_over_time",
        "show_overall": False,
        "show_per_gpu": True,
        "write_to_db": True,
        "long_name": "Infinity Fabric RX Throughput",
    },
    "XGMI TX": {
        "metric": "xgmi_total_tx_per_sec",
        "operation": "avg_over_time",
        "show_overall": False,
        "show_per_gpu": True,
        "write_to_db": True,
        "long_name": "Infinity Fabric TX Throughput",
    },
    "Power": {
        "metric": "power_usage_milliwatts",
        "operation": "avg_over_time",
        "show_overall": False,
        "show_per_gpu": True,
        "write_to_db": True,
        "long_name": "Socket Power",
    },
    "Temp": {
        "metric": "temperature_celsius",
        "operation": "avg_over_time",
        "show_overall": False,
        "show_per_gpu": True,
        "write_to_db": True,
        "long_name": "Junction Temperature",
    },
}

################################################################################
##                          C U S T O M    N O T E S                          ##
################################################################################

NOTES = []

# Node and architecture specs for Muscadine 
CORES_PER_NODE = {
    "muscadine": 64,
}
DEFAULT_MEM_PER_CORE = {
    "muscadine": 2_000_000_000,
}

###############################
# B O L D   R E D   N O T E S #
###############################

# Zero GPU utilization (single GPU jobs)
condition = 'self.js.gpus and (self.js.diff > c.MIN_RUNTIME_SECONDS) and num_unused_gpus > 0 and self.js.gpus == 1'
note = ("This job did not use the allocated AMD Instinct GPU. Please verify that your application "
        "is built with ROCm/HIP support and actively executing GPU kernels before resubmitting.")
style = "bold-red"
NOTES.append((condition, note, style))

# Zero GPU utilization (multi-GPU jobs)
condition = 'self.js.gpus and (self.js.diff > c.MIN_RUNTIME_SECONDS) and num_unused_gpus > 0 and self.js.gpus > 1'
note = ('f"This job did not use {num_unused_gpus} of the {self.js.gpus} allocated GPUs. "'
        'f"Please verify multi-GPU configuration (RCCL, HIP_VISIBLE_DEVICES, or MPI rank bindings). {multi}"')
style = "bold-red"
NOTES.append((condition, note, style))

# Zero CPU utilization (single node)
condition = '(self.js.diff > c.MIN_RUNTIME_SECONDS) and (num_unused_nodes > 0) and (self.js.nnodes == "1")'
note = ('"This job did not use the CPU. This suggests that the process stalled or failed "'
        '"at the beginning of the execution. Inspect your job script and the "'
        'f"slurm-{self.js.jobid}.out file for startup errors."')
style = "bold-red"
NOTES.append((condition, note, style))

# Out of memory
condition = 'self.js.state == "OUT_OF_MEMORY" and (not zero_cpu)'
note = ("This job failed because it exceeded allocated system memory. Resubmit while requesting "
        "additional memory via the --mem or --mem-per-cpu Slurm parameter.")
style = "bold-red"
NOTES.append((condition, note, style))

# Timeout
condition = '(self.js.state == "TIMEOUT") and (not zero_gpu) and (not zero_cpu)'
note = ("This job was cancelled because it reached its walltime limit. Increase the "
        "--time parameter in your batch script to allow the workload to finish.")
style = "bold-red"
NOTES.append((condition, note, style))

# Excessive walltime limit requested
condition = 'self.js.time_eff_violation and self.js.time_efficiency <= c.TIME_EFFICIENCY_RED and (not zero_gpu) and (not zero_cpu)'
note = ('f"This job only used {self.js.time_efficiency}% of its requested time limit "'
        'f"({self.human_seconds(SECONDS_PER_MINUTE * self.js.timelimitraw)}). Requesting more accurate walltimes "'
        '"improves job scheduling priority and cluster queue throughput."')
style = "bold-red"
NOTES.append((condition, note, style))


#########################
# P L A I N   N O T E S #
#########################

# Low GPU utilization
condition = '(not zero_gpu) and self.js.gpus and (self.js.gpu_utilization <= c.GPU_UTIL_RED) and (self.js.diff > c.MIN_RUNTIME_SECONDS)'
note = ('f"The overall GPU utilization was only {round(self.js.gpu_utilization)}%. "'
        '"Low utilization often indicates I/O bottlenecks, single-threaded CPU pre-processing, "'
        '"or small batch sizes unable to saturate the compute units on the MI210."')
style = "normal"
NOTES.append((condition, note, style))

# Low CPU utilization (parallel jobs)
condition = '(not zero_cpu) and (not self.js.gpus) and (self.js.cpu_efficiency < c.CPU_UTIL_RED) and (int(self.js.ncpus) > 1)'
note = ('f"The overall CPU utilization was {ceff}%. Ensure your application is multithreaded "'
        'f"(OpenMP/MPI) and properly utilizing all {self.js.ncpus} requested cores."')
style = "normal"
NOTES.append((condition, note, style))

# Low CPU utilization (serial code running with multiple requested cores)
condition = '(self.js.nnodes == "1") and (int(self.js.ncpus) > 1) and (not self.js.gpus) and (serial_ratio > 0.85 and serial_ratio < 1.01)'
note = ('f"The CPU utilization ({self.js.cpu_efficiency}%) indicates the program only used 1 of the "'
        'f"{self.js.ncpus} allocated CPU cores. Allocating additional cores for a single-threaded program "'
        '"wastes queue priority. Set --cpus-per-task=1 or --ntasks=1."')
style = "normal"
NOTES.append((condition, note, style))

# Overallocating CPU memory
condition = ('(not zero_gpu) and (not zero_cpu) and (self.js.cpu_memory_efficiency < c.MIN_MEMORY_USAGE) '
             'and gpu_show and (self.js.state != "OUT_OF_MEMORY") and (self.js.diff > c.MIN_RUNTIME_SECONDS)')
note = ('f"This job {opening} of its allocated CPU memory ({self.cpu_memory_formatted(with_label=False)}). "'
        'f"For future jobs, consider reducing memory allocation to --mem={self.rounded_memory_with_safety(gb_per_node_used)}G."')
style = "normal"
NOTES.append((condition, note, style))
