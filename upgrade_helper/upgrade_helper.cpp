#include <chrono>
#include <thread>
#include <filesystem>
#include <windows.h>
#include <iostream>
#include <unistd.h>
int main() {
	std::this_thread::sleep_for(std::chrono::seconds(1)); // 等待1秒防止出问题

	try {
		std::filesystem::rename("../../app", "../../will_delete");
	} catch (std::filesystem::filesystem_error& e) {
		std::cout << "Error renaming 'app' to 'will_delete': " << e.what() << '\n';
	}

	try {
		std::filesystem::rename("../../will_use", "../../app");
	} catch (std::filesystem::filesystem_error& e) {
		std::cout << "Error renaming 'will_use' to 'app': " << e.what() << '\n';
	}

	if (chdir("../../app") != 0) {
		perror("Error changing directory to '../../app'");
	}

	ShellExecute(NULL, "open", "Simple Class Information Display.exe", NULL, NULL, SW_SHOW);
	return 0;
}

