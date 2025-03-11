import daemon

from main import main

if __name__ == "__main__":
	with daemon.DaemonContext():
		main()