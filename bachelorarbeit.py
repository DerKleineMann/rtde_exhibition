from rtde_control import RTDEControlInterface as RTDEControl
from rtde_receive import RTDEReceiveInterface as RTDEReceive
import datetime
import math
import os
import psutil
import sys
import time


# Function to gather data from robot
def robotData(rtde_r):
    # Get the actual joint positions
    actualQ = rtde_r.getActualQ()
    # Get the actual TCP force
    actualTCPForce = rtde_r.getActualTCPForce()
    # Get the actual TCP speed
    actualTCPSpeed = rtde_r.getActualTCPSpeed()
    # get the actual current
    actualCurrent = rtde_r.getActualCurrent()
    print("Actual joint positions:", actualQ, "\n Actual TCP Force:", actualTCPForce, "\n Actual TCP Speed:", actualTCPSpeed, "\n Actual current inside the robot:", actualCurrent)


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

# Check connection with robot
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

# Attribution of positions
homeJoints = [0.11096344143152237, -1.1199520269977015, -2.5396979490863245, -0.09851295152773076, 1.4749480485916138, 0.31134793162345886]
homePose = [572.20,-127.03,-91.83,2.286,-2.904,1.187]
homeJointsDeg = [6.34,-64.17,-145.51,-5.64,84.51,17.84]
firstGoalJoints = [0.7451574206352234, -1.3359397093402308, -2.2915383020984095, -0.523752514516012, 0.9417466521263123, 0.31137189269065857]
secondGoalJoints = [-0.0847085157977503, -1.51786977449526, -2.3583067099200647, -0.5191591421710413, 1.4815809726715088, 0.31137189269065857]
thirdGoalJoints = [-0.07562238374818975, -1.3190715948687952, -2.1666491667376917, -1.1410210768329065, 1.474852204322815, 0.311335951089859]

print(rtde_r.getActualQ())

# Go to home position in moveJ
rtde_c.moveJ(homeJoints, vel, acc)

# Go to position in ServoJ
""" counter = 0
while counter<=1250:
    t_start = rtde_c.initPeriod()
    rtde_c.servoJ(firstGoalJoints, vel, acc, dt, lookahead_time, gain)
    robotData(rtde_r)
    rtde_c.waitPeriod(t_start)
    time_counter += dt
    counter += 1
rtde_c.servoStop() """

# Go to position in moveL
#rtde_c.moveL(homePose, vel, acc)

""" # Go to position in ServoL
counter = 0
while counter<=5000:
    t_start = rtde_c.initPeriod()
    rtde_c.servoL(secondGoalPosition, vel, acc, dt, lookahead_time, gain)
    robotData(rtde_r)
    rtde_c.waitPeriod(t_start)
    time_counter += dt
    counter += 1
rtde_c.servoStop()

# Go back to home position
rtde_c.moveJ(homePosition, vel, acc) """



# End connection with robot
print("Control Interrupted!")
rtde_c.servoStop()
rtde_c.stopScript()