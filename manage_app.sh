#!/bin/bash

# Navigate to your project directory
cd /home/indiasfernandes/Automations/OnCoins

# Initialize pyenv and pyenv-virtualenv
export PATH="/home/indiasfernandes/.pyenv/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv virtualenv-init -)"

echo "Starting virtual environment..."
pyenv activate env

eval "$(ssh-agent -s)"
ssh-add ~/.ssh/ssh_key



# Function to renew IP lease
renew_ip_lease() {
    echo "Releasing and renewing IP lease..."
    sudo dhclient -r wlan0 && sudo dhclient wlan0
    echo "IP lease renewed."
}

# Function to collect static files
collect_static_files() {
    echo "Collecting and managing static files..."
    python manage.py collectstatic --noinput
    echo "Static files collected."
}

# Function to handle Git operations
handle_git_operations() {
    echo "Stashing local changes and pulling latest updates..."
    git stash
    git pull origin raspberry-version
}

handle_migration() {
    echo "Handling Django migrations..."
    python manage.py makemigrations
    python manage.py migrate
}

start_django_server() {
    echo "Starting Django development server on main screen..."
    screen -dmS django_main_screen python manage.py runserver 0.0.0.0:8000

  }


# Function to restart the development system
start_server() {
    echo "Closing previous screens..."
    killall screen

    echo "Killing all Celery´s..."
    pkill -f 'celery'

    echo "Restarting the development environment..."
    handle_git_operations
    handle_migration

    echo "Managing Celery processes..."
    redis-server --daemonize yes

    echo "Starting Celery workers and beats..."
    screen -dmS celery_worker celery -A CoinHub worker -l info
    screen -dmS celery_beat celery -A CoinHub beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

    start_django_server

    screen -wipe

    sleep 10
}

# Main menu loop
while true; do
    clear
    echo "Developer Operations Menu:"
    echo "1. Start/Restart Server"
    echo "2. Renew IP"
    echo "3. Collect Static Files"
    echo "4. Exit"
    read -p "Enter choice [1-4]: " choice

    case $choice in
        1) start_server ;;
        2) renew_ip_lease ;;
        3) collect_static_files ;;
        4) echo "Shutting down..."; exit 0 ;;
        *) echo "Invalid selection, try again."; sleep 2 ;;
    esac
done

