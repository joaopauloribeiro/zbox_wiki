#!/usr/bin/env bash
cd $HOME/Documents/code

RSYNC_OPTS="--recursive --links --perms --times --force --delete --stats
rsync "$RSYNC_OPTS" zbox_wiki /Volumes/PODORA/coding"