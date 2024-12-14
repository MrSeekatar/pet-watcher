#!/bin/bash

run()
{
    rm nohup.out || true
    nohup python3 pet_watcher.py &
    echo Running in the background. To see output: tail -f nohup.out
}

lint()
{
    pylint pet_watcher.py send_email.py detect_motion.py
}

Help()
{
    echo "Run one or more bash snippets"
    echo
    echo "run # runs the watcher"
    echo "lint # does lint"
    echo
}

while (( "$#")); do
    case $1 in
        lint)
            lint;;
        run)
            run;;
        *)
            Help;;
    esac
    shift
done
