#include <windows.h>
#include <iostream>
#include <string>
#include <vector>
#include <limits>
#include <dxgi.h>
#include <iphlpapi.h>
#include <sstream>
#pragma comment(lib, "dxgi.lib")
#pragma comment(lib, "iphlpapi.lib")

// Get CPU name using __cpuid intrinsic
#include <intrin.h>
std::string GetCPUName() {
    int cpuInfo[4] = { -1 };
    char cpuBrandString[0x40] = { 0 };
    __cpuid(cpuInfo, 0x80000000);
    unsigned int nExIds = cpuInfo[0];
    for (unsigned int i = 0x80000000; i <= nExIds; ++i) {
        __cpuid(cpuInfo, i);
        if (i == 0x80000002)
            memcpy(cpuBrandString, cpuInfo, sizeof(cpuInfo));
        else if (i == 0x80000003)
            memcpy(cpuBrandString + 16, cpuInfo, sizeof(cpuInfo));
        else if (i == 0x80000004)
            memcpy(cpuBrandString + 32, cpuInfo, sizeof(cpuInfo));
    }
    return std::string(cpuBrandString);
}

// Get number of logical processors
unsigned int GetLogicalProcessorCount() {
    SYSTEM_INFO sysinfo;
    GetSystemInfo(&sysinfo);
    return sysinfo.dwNumberOfProcessors;
}

// Get total and available RAM in GB
void GetRAMInfo(double &totalGB, double &availGB) {
    MEMORYSTATUSEX memInfo;
    memInfo.dwLength = sizeof(MEMORYSTATUSEX);
    GlobalMemoryStatusEx(&memInfo);
    totalGB = memInfo.ullTotalPhys / (1024.0 * 1024 * 1024);
    availGB = memInfo.ullAvailPhys / (1024.0 * 1024 * 1024);
}

// Get disk total and free size in GB
void GetDiskInfo(const wchar_t* drive, double &totalGB, double &freeGB) {
    ULARGE_INTEGER freeBytesAvailable, totalNumberOfBytes, totalNumberOfFreeBytes;
    BOOL res = GetDiskFreeSpaceExW(drive, &freeBytesAvailable, &totalNumberOfBytes, &totalNumberOfFreeBytes);
    if (res) {
        totalGB = totalNumberOfBytes.QuadPart / (1024.0 * 1024 * 1024);
        freeGB = totalNumberOfFreeBytes.QuadPart / (1024.0 * 1024 * 1024);
    } else {
        totalGB = freeGB = -1.0;
    }
}

// Get GPU names
std::vector<std::wstring> GetGPUNames() {
    std::vector<std::wstring> gpus;
    IDXGIFactory* pFactory = nullptr;
    HRESULT hr = CreateDXGIFactory(__uuidof(IDXGIFactory), (void**)&pFactory);
    if (FAILED(hr)) return gpus;

    IDXGIAdapter* pAdapter = nullptr;
    for (UINT i = 0; pFactory->EnumAdapters(i, &pAdapter) != DXGI_ERROR_NOT_FOUND; ++i) {
        DXGI_ADAPTER_DESC desc;
        pAdapter->GetDesc(&desc);
        gpus.push_back(desc.Description);
        pAdapter->Release();
    }
    pFactory->Release();
    return gpus;
}

// Get OS version string
std::string GetOSVersion() {
    OSVERSIONINFOEXW osvi = { 0 };
    osvi.dwOSVersionInfoSize = sizeof(osvi);
    if (!GetVersionExW((OSVERSIONINFOW*)&osvi)) return "Unknown OS Version";

    std::ostringstream oss;
    oss << "Windows " << osvi.dwMajorVersion << "." << osvi.dwMinorVersion
        << " (Build " << osvi.dwBuildNumber << ")";
    return oss.str();
}

// Get primary display resolution
void GetDisplayResolution(int &width, int &height) {
    width = GetSystemMetrics(SM_CXSCREEN);
    height = GetSystemMetrics(SM_CYSCREEN);
}

// Get network adapters names
std::vector<std::string> GetNetworkAdapters() {
    std::vector<std::string> adapters;
    ULONG bufferSize = 0;
    if (GetAdaptersInfo(NULL, &bufferSize) != ERROR_BUFFER_OVERFLOW) return adapters;

    IP_ADAPTER_INFO* adapterInfo = (IP_ADAPTER_INFO*)malloc(bufferSize);
    if (GetAdaptersInfo(adapterInfo, &bufferSize) != NO_ERROR) {
        free(adapterInfo);
        return adapters;
    }

    for (IP_ADAPTER_INFO* adapter = adapterInfo; adapter != NULL; adapter = adapter->Next) {
        adapters.push_back(adapter->Description);
    }

    free(adapterInfo);
    return adapters;
}

int main() {
    std::cout << "=== System Info ===\n\n";

    std::cout << "CPU: " << GetCPUName() << "\n";
    std::cout << "Logical processors: " << GetLogicalProcessorCount() << "\n";

    double totalRAM = 0, availRAM = 0;
    GetRAMInfo(totalRAM, availRAM);
    std::cout << "RAM: " << totalRAM << " GB total, " << availRAM << " GB available\n";

    double totalDisk = 0, freeDisk = 0;
    GetDiskInfo(L"C:\\", totalDisk, freeDisk);
    if (totalDisk >= 0)
        std::cout << "Disk C: " << totalDisk << " GB total, " << freeDisk << " GB free\n";
    else
        std::cout << "Disk info unavailable\n";

    auto gpus = GetGPUNames();
    if (gpus.empty()) {
        std::cout << "No GPUs found\n";
    } else {
        std::wcout << L"GPU(s):\n";
        for (const auto& gpu : gpus)
            std::wcout << L"  " << gpu << L"\n";
    }

    std::cout << "OS Version: " << GetOSVersion() << "\n";

    int width = 0, height = 0;
    GetDisplayResolution(width, height);
    std::cout << "Display resolution: " << width << " x " << height << "\n";

    auto adapters = GetNetworkAdapters();
    if (adapters.empty()) {
        std::cout << "No network adapters found\n";
    } else {
        std::cout << "Network adapters:\n";
        for (const auto& adapter : adapters)
            std::cout << "  " << adapter << "\n";
    }

    std::cout << "\nPress Enter to exit...";
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');

    return 0;
}
