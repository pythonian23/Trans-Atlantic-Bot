import os, subprocess, signal

print("Content-Type: text/html\n\n")

counter = 0
p = subprocess.Popen(['ps', '-u', 'pythonia'], stdout=subprocess.PIPE)
# must match your username --------^^^^^^^^

out, err = p.communicate()
for line in out.splitlines():
  if 'main.py'.encode('utf-8') in line:
#     ^^^^^^^--- this has to match the filename of your loop

    counter += 1
    pid = int(line.split(None, 1)[0])
    print("Stopping bot.")
    os.kill(pid, signal.SIGTERM)

if counter == 0:
  print("Already stopped.")