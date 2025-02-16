#!/bin/bash
fswatch -o ./game_ctrl | while read f; do
    rsync -avz --delete ./game_ctrl/ do-deploy:/opt/game_ctrl/
done 