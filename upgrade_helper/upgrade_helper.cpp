#include <chrono>
#include <thread>
#include <filesystem>
#include <unistd.h>
#include <cstdlib>

int main() {
    std::this_thread::sleep_for(std::chrono::seconds(1)); // 等待1秒防止出问题
    std::filesystem::rename("../../app", "will_delete");
    std::filesystem::rename("../../will_use", "app");
    chdir("../../app");
    system("./Simple Class Information Display.exe");
    return 0;
}