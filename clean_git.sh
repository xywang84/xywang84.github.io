rm -rf .git
git init
git add .
git commit -m "Initial Commit"
emacs ~/.bash_history
git remote add origin git@github.com:xywang84/xywang84.github.io
git remote -v
git push -u --force origin master
