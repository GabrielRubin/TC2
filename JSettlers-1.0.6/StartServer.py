import subprocess

serverProcess = subprocess.Popen("java -jar JSettlersServer.jar 8880 10 dbUser dbPass",
                                 shell=True, stdout=subprocess.PIPE)
robot1Process = subprocess.Popen("java -cp JSettlersServer.jar soc.robot.SOCRobotClient localhost 8880 robot1 passwd",
                                 shell=False, stdout=subprocess.PIPE)
robot2Process = subprocess.Popen("java -cp JSettlersServer.jar soc.robot.SOCRobotClient localhost 8880 robot2 passwd",
                                 shell=False, stdout=subprocess.PIPE)
robot3Process = subprocess.Popen("java -cp JSettlersServer.jar soc.robot.SOCRobotClient localhost 8880 robot3 passwd",
                                 shell=False, stdout=subprocess.PIPE)
clientProcess = subprocess.Popen("java -jar JSettlers.jar localhost 8880")

serverProcess.wait()
robot1Process.wait()
robot2Process.wait()
robot3Process.wait()
clientProcess.wait()

print serverProcess.returncode