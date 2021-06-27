#!/bin/bash

ps -aux | grep "buyer.py" | awk '{print $2}' | xargs kill 2>/dev/null
ps -aux | grep "firefox" | awk '{print $2}' | xargs kill 2>/dev/null
ps -aux | grep "geckodriver" | awk '{print $2}' | xargs kill 2>/dev/null
