if test -f /opt/homebrew/bin/brew
    eval (/opt/homebrew/bin/brew shellenv)
end

fish_add_path --path /usr/local/sbin
fish_add_path --path /usr/local/bin

fish_add_path $HOME/.local/bin
fish_add_path $HOME/.cargo/bin
fish_add_path $HOME/bin

set fish_greeting ""

abbr --add blog "code ~/blog"
abbr --add lab "code ~/lab"
abbr --add prune "git reflog expire --expire=now --all && git gc --prune=now"

if status is-interactive
    starship init fish | source
end
