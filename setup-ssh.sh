# bash
echo This does not work in script, since env vars not set? SSH_AUTH_SOCK IIRC
eval `ssh-agent -s`
ssh-add ~/.ssh/seekatar