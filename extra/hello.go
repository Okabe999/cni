package main

import (
    "fmt"
    "os/exec"
    "syscall"
)

func startDaemon() error {
    // Python脚本路径
    pythonScript := "/root/extra/main.py"
    // 输入和输出文件路径
    inputPath := "/root/extra/jsonpath.txt"


    // 构建命令
    cmd := exec.Command("python3", pythonScript, "docker", inputPath, "4026531839")

    // 设置命令为守护进程
    cmd.SysProcAttr = &syscall.SysProcAttr{
        Setsid: true,
    }

    // 启动命令
    if err := cmd.Start(); err != nil {
        return fmt.Errorf("failed to start daemon: %v", err)
    }

    fmt.Printf("Daemon started with PID %d\n", cmd.Process.Pid)
    return nil
}

func main() {
    // 在需要的地方调用startDaemon函数
    if err := startDaemon(); err != nil {
        fmt.Printf("Error starting daemon: %v\n", err)
    }
}

