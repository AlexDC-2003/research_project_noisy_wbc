import time

from application import SenderProgram, Receiver0Program, Receiver1Program
from squidasm.run.stack.config import StackNetworkConfig
from squidasm.run.stack.run import run

# Import network configuration
cfg = StackNetworkConfig.from_file("config.yaml")

# Create program instances
sender_program = SenderProgram()
receiver0_program = Receiver0Program()
receiver1_program = Receiver1Program()

start_time = time.time()
# Run simulation
run(config=cfg, programs={
    "Sender": sender_program,
    "Receiver0": receiver0_program,
    "Receiver1": receiver1_program
}, num_times=1)

end_time = time.time()
print(f"Execution time: {end_time - start_time:.2f} seconds")