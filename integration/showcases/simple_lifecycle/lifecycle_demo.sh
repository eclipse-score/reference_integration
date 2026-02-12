#! /bin/sh

running_on_qnx() {
    [ -x "$(command -v slay)" ]
}

echo "\nStep 1: Starting Launch Manager\n"
cd /showcases/data/simple_lifecycle
/showcases/bin/launch_manager&

sleep 2

echo "\nStep 2: Make application stop reporting alive notifications\n"

if running_on_qnx
then
    slay -s SIGUSR1 -f cpp_supervised_app
else
    pkill -SIGUSR1 -f cpp_supervised_app
fi

sleep 6

echo "\nStep 3: Shutdown Launch Manager\n"

if running_on_qnx
then
    slay -f launch_manager
else
    pkill -f launch_manager
fi
