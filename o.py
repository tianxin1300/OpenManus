import subprocess, pathlib
def run(c):
    print("$", c)
    subprocess.run(c, shell=True)
run("git status --porcelain")
run("git add -f docs/ workspace/summary.md cloudflare/")
run('git commit -m "final: bypass 0-tools + 0-cost gateway dual routing"')
run("git push")
print("push done")
