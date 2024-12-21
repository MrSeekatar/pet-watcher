#!/bin/bash

run()
{
    rm log.txt || true
    python3 pet_watcher.py > log.txt 2>&1 &
    echo Running in the background. To see output: tail -f log.txt
}

lint()
{
    pylint pet_watcher.py send_email.py detect_motion.py
}

Help()
{
    echo "Run one or more bash snippets. Enter one or more of the following commands:"
    echo
    echo "  run    # runs the watcher"
    echo "  lint   # does lint"
    echo
}

# Check if no arguments are passed
if [ $# -eq 0 ]; then
    Help
    exit 0
fi

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
