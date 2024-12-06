rm nohup.out || true
. ./init-dont-commit.sh
nohup python3 ./pet-watcher.py
echo Running in the background. To see output: tail -f nohup.out