from netqasm.sdk.qubit import Qubit
from netqasm.sdk.classical_communication.message import StructuredMessage
from squidasm.sim.stack.program import Program, ProgramContext, ProgramMeta
from squidasm.util.routines import teleport_send, teleport_recv
import random
import math

# Number of States used for 1 bit of data sent
NUM_STATES = 280

class SenderProgram(Program):
    # Other parties involved in the communication
    PEER_R0 = "Receiver0"
    PEER_R1 = "Receiver1"

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="sender_faulty_program",
            csockets=[self.PEER_R0, self.PEER_R1],
            epr_sockets=[self.PEER_R0, self.PEER_R1],
            max_qubits=5 * NUM_STATES,
        )

    def run(self, context: ProgramContext):
        connection = context.connection

        # Set conflicting messages for each receiver
        # This is the case utilised in Guba et al. appendices
        x_r0 = 0
        x_r1 = 1
        sigma_r0 = []
        sigma_r1 = []

        # Local bit pair counts
        indices_0011 = []
        indices_mixed = []
        indices_1100 = []

        for i in range(NUM_STATES):
            # Create and entangle 4 qubits
            # Linear Circuit Implementation
            q0 = Qubit(connection)
            q1 = Qubit(connection)
            q2 = Qubit(connection)
            q3 = Qubit(connection)
            q0.rot_Z(1, 1)
            q1.rot_Z(1, 1)
            q2.rot_Z(1, 1)
            q0.rot_X(1, 1)
            q1.rot_X(1, 1)
            q2.rot_X(1, 1)
            q0.rot_Z(17, 6)
            q1.rot_Z(1, 1)
            q2.rot_Z(237, 7)
            q2.cnot(q0)
            q0.rot_X(1, 1)
            q2.rot_X(1, 1)
            q0.rot_Z(19, 7)
            q2.rot_Z(1, 1)
            q0.rot_X(1, 1)
            q0.rot_Z(1, 0)
            q1.cnot(q0)
            q2.cnot(q0)
            q3.cnot(q1)
            q0.cnot(q2)
            q1.cnot(q3)
            q2.cnot(q0)
            q0.cnot(q1)
            q2.cnot(q0)

            # Teleport third qubit q2 to R0, fourth qubit q3 to R1
            yield from connection.flush()
            yield from teleport_send(q2, context, peer_name=self.PEER_R0)
            yield from teleport_send(q3, context, peer_name=self.PEER_R1)

            # Measure q0 and q1
            m0 = q0.measure()
            m1 = q1.measure()
            yield from connection.flush()

            # Build local count lists
            bits = (int(m0), int(m1))
            if bits == (0, 0):
                indices_0011.append(i)
            elif bits == (1, 1):
                indices_1100.append(i)
            else:
                indices_mixed.append(i)

        # Adversarial strategy from Appendix B.1
        T = math.ceil(0.272 * NUM_STATES)
        Q = T - math.ceil(0.94 * T) + 1
        if len(indices_0011) >= T - Q and len(indices_mixed) >= Q and len(indices_1100) >= T:
            sigma_r0 = indices_0011[:T - Q] + indices_mixed[:Q]
            sigma_r1 = indices_1100[:T]
        else:
            # Cannot apply strategy safely, send empty sets to force abort
            sigma_r0 = []
            sigma_r1 = []
            return {
                "failed_to_apply_strategy": True,
                "l1": len(indices_0011),
                "l2": len(indices_mixed),
                "l3": len(indices_1100)
            }

        # Send data to receivers and return "output"
        context.csockets[self.PEER_R0].send(StructuredMessage("invocation", [x_r0, sigma_r0]))
        context.csockets[self.PEER_R1].send(StructuredMessage("invocation", [x_r1, sigma_r1]))
        return {
            "x_r0": x_r0,
            "x_r1": x_r1,
            "sigma_r0_len": len(sigma_r0),
            "sigma_r1_len": len(sigma_r1),
            "l1": len(indices_0011),
            "l2": len(indices_mixed),
            "l3": len(indices_1100)
        }


class Receiver0Program(Program):
    # Other parties involved in the communication
    PEER = "Sender"
    PEER_R1 = "Receiver1"
    # MU parameter of the WBC
    MU = 0.3

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="receiver0_program",
            csockets=[self.PEER, self.PEER_R1],
            epr_sockets=[self.PEER],
            max_qubits=NUM_STATES,
        )

    def run(self, context: ProgramContext):
        connection = context.connection

        # Receive teleported qubits
        qubits = []
        for _ in range(NUM_STATES):
            q = yield from teleport_recv(context, peer_name=self.PEER)
            qubits.append(q)

        csocket = context.csockets[self.PEER]
        csocket_r1 = context.csockets[self.PEER_R1]

        # Receive data bit and check set
        msg = yield from csocket.recv()
        x_s, sigma_s = msg.payload

        # Minimum check set length for the length condition
        T = math.ceil(self.MU * NUM_STATES)
        y0 = "abort"

        # Perform check phase
        if len(sigma_s) >= T:
            outcomes = []
            for i in sigma_s:
                outcome = qubits[i].measure()
                outcomes.append(outcome)
            yield from connection.flush()
            # Check if each pair of received qubits-data bit are different
            # If they are, consistency check passes
            # Otherwise, abort is kept
            if all(int(o) != x_s for o in outcomes):
                y0 = x_s

        # Send your received data bit and check set forward to the second receiver
        csocket_r1.send(StructuredMessage("forward", [x_s, sigma_s]))
        # Return output
        return {"y0": y0}


class Receiver1Program(Program):
    # Other parties involved in the communication
    PEER = "Sender"
    PEER_R0 = "Receiver0"
    
    # Parameters of the WBC
    MU = 0.3
    LAMBDA = 0.94

    @property
    def meta(self) -> ProgramMeta:
        return ProgramMeta(
            name="receiver1_program",
            csockets=[self.PEER, self.PEER_R0],
            epr_sockets=[self.PEER],
            max_qubits=NUM_STATES,
        )

    def run(self, context: ProgramContext):
        connection = context.connection

        # Receive teleported qubits
        qubits = []
        for _ in range(NUM_STATES):
            q = yield from teleport_recv(context, peer_name=self.PEER)
            qubits.append(q)

        csocket = context.csockets[self.PEER]
        csocket_r0 = context.csockets[self.PEER_R0]

        # Receive data bit and check set
        msg = yield from csocket.recv()
        x_s, sigma_s = msg.payload

        # Minimum check set length for the length condition
        T = math.ceil(self.MU * NUM_STATES)
        y1_tilde = "abort"

        # Perform check phase
        if len(sigma_s) >= T:
            outcomes = []
            for i in sigma_s:
                outcome = qubits[i].measure()
                outcomes.append(outcome)
            yield from connection.flush()
            # Check if each pair of received qubits-data bit are different
            # If they are, consistency check passes
            # Otherwise, abort is kept
            if all(int(o) != x_s for o in outcomes):
                y1_tilde = x_s
        
        # Receive forwarded bit and check set from First Receiver
        msg2 = yield from csocket_r0.recv()
        x0_fwd, sigma0_fwd = msg2.payload

        # Confusion property check
        confusion_ok = x0_fwd != y1_tilde and x0_fwd != "abort" and y1_tilde != "abort"
        # Length check
        length_ok = len(sigma0_fwd) >= T
        # Consistency check
        consistency_ok = False
        if length_ok:
            required = math.ceil(self.LAMBDA * T + len(sigma0_fwd) - T)
            mismatch = 0
            for _ in sigma0_fwd:
                dummy_q = Qubit(connection)
                m = dummy_q.measure()
                yield from connection.flush()
                if int(m) != x0_fwd:
                    mismatch += 1
            consistency_ok = mismatch >= required

        # Return output
        y1 = x0_fwd if (confusion_ok and length_ok and consistency_ok) else y1_tilde
        return {"y1": y1}