set fish_greeting ""

fish_add_path --path /usr/local/sbin
fish_add_path --path /usr/local/bin

if type --query /opt/homebrew/bin/brew
    /opt/homebrew/bin/brew shellenv | source
end

fish_add_path $HOME/.local/bin
fish_add_path $HOME/.cargo/bin
fish_add_path $HOME/bin

if type --query pacman
    set --export EDITOR helix
    abbr --add hx helix
else
    set --export EDITOR hx
end

if status is-interactive
    starship init fish | source
    zoxide init fish | source
end

abbr --add blog "$EDITOR ~/blog"
abbr --add lab "$EDITOR ~/lab"
abbr --add miri "cargo +nightly miri"
abbr --add prune "git reflog expire --expire=now --all && git gc --prune=now"
