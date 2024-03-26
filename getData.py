# Imported Python libraries from ur_rtde
from rtde_control import RTDEControlInterface as RTDEControl
from rtde_receive import RTDEReceiveInterface as RTDEReceive
import datetime
import math
import os
import psutil
import sys

def getCircleTarget(pose, timestep, radius=0.075, freq=1.0):
    circ_target = pose[:]
    circ_target[0] = pose[0] + radius * math.cos((2 * math.pi * freq * timestep))
    circ_target[1] = pose[1] + radius * math.sin((2 * math.pi * freq * timestep))
    return circ_target

# Parameters
vel = 0.5
acc = 0.5
rtde_frequency = 500.0
dt = 1.0/rtde_frequency  # 2ms
flags = RTDEControl.FLAG_VERBOSE | RTDEControl.FLAG_UPLOAD_SCRIPT
ur_cap_port = 50002
robot_ip = "10.211.56.10"

lookahead_time = 0.1
gain = 600

# ur_rtde realtime priorities
rt_receive_priority = 90
rt_control_priority = 85

rtde_r = RTDEReceive(robot_ip, rtde_frequency, [], True, False, rt_receive_priority)
rtde_c = RTDEControl(robot_ip, rtde_frequency, flags, ur_cap_port, rt_control_priority)

# Set application real-time priority
os_used = sys.platform
process = psutil.Process(os.getpid())
if os_used == "win32":  # Windows (either 32-bit or 64-bit)
    process.nice(psutil.REALTIME_PRIORITY_CLASS)
elif os_used == "linux":  # linux
    rt_app_priority = 80
    param = os.sched_param(rt_app_priority)
    try:
        os.sched_setscheduler(0, os.SCHED_FIFO, param)
    except OSError:
        print("Failed to set real-time process scheduler to %u, priority %u" % (os.SCHED_FIFO, rt_app_priority))
    else:
        print("Process real-time priority set to: %u" % rt_app_priority)

time_counter = 0.0

# Home position
home_tcp_pose = [0.29847139545707124, -0.1478598501112546, 0.3479066344993614, -1.8899557664340416, 2.416018432569994, 0.009677137005207807]
rtde_c.moveL(home_tcp_pose, vel, acc)

# Move to init position using moveL
actual_tcp_pose = rtde_r.getActualTCPPose()
init_pose = getCircleTarget(actual_tcp_pose, time_counter)
rtde_c.moveL(init_pose, vel, acc)


counter = 0

while counter<=5000:
    t_start = rtde_c.initPeriod()
    servo_target = getCircleTarget(actual_tcp_pose, time_counter)
    rtde_c.servoL(servo_target, vel, acc, dt, lookahead_time, gain)
    print("Actual Q: ", rtde_r.getActualQ())
    print("Actual TCP Force: ", rtde_r.getActualTCPForce())
    print("Actual TCP Speed: ", rtde_r.getActualTCPSpeed())
    print("Actual Joint Current: ", rtde_r.getActualCurrent())
    rtde_c.waitPeriod(t_start)
    time_counter += dt
    counter += 1


print("Control Interrupted!")
rtde_c.servoStop()
rtde_c.stopScript()
