unbind-key -n C-a
unbind-key -n C-z
set -g prefix ^Z
set -g prefix2 F12
bind z send-prefix

###############################################################
# Emacs 風キーバインド
###############################################################

unbind 1
unbind ^C
unbind &

# prefix 0 現在のペインを削除
bind 0 kill-pane
# prefix 1 ウインドウ内の現在のペインを残し、他のペインをウインドウにする
bind 1 break-pane
# prefix 2 ウインドウを横に分割
bind 2 split-window -v
# prefix 3 ウインドウを縦に分割
bind 3 split-window -h
# prefix o ペインをローテート
bind o select-pane -t :.+
# prefix k ウインドウを削除
bind k kill-window
# prefix C-k ペインを削除
bind C-k kill-pane
# prefix i
bind i display-panes
# prefix C-t
bind C-t next-window
