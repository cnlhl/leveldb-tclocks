import subprocess
import matplotlib.pyplot as plt
import re
import os

def run_c_program(executable_path, num_threads):
    """运行 C 程序并返回执行时间"""
    try:
        # 确保 iterations_per_thread 足够大，使得锁竞争明显
        # 如果 iterations_per_thread * num_threads 过大，总时间会很长
        # 这里 C 程序内部 iterations_per_thread 是固定的，所以总工作量随线程数增加而增加
        # 这更能模拟多个独立任务竞争同一资源的情况
        result = subprocess.run([executable_path, str(num_threads)],
                                capture_output=True, text=True, check=True, timeout=300) # 5分钟超时
        output = result.stdout
        # 从标准输出中解析简化输出
        match = re.search(r"THREADS:(\d+),TIME_MS:([\d.]+)", output)
        if match:
            threads = int(match.group(1))
            time_ms = float(match.group(2))
            print(f"测试: {threads} 线程, 耗时: {time_ms:.2f} ms")
            return threads, time_ms
        else:
            print(f"警告: 无法从输出中解析数据 (线程数 {num_threads}):\n{output}")
            return num_threads, None
    except subprocess.CalledProcessError as e:
        print(f"C 程序执行错误 (线程数 {num_threads}): {e}")
        print(f"Stderr: {e.stderr}")
        return num_threads, None
    except subprocess.TimeoutExpired:
        print(f"C 程序执行超时 (线程数 {num_threads})")
        return num_threads, None
    except Exception as e:
        print(f"运行C程序时发生未知错误 (线程数 {num_threads}): {e}")
        return num_threads, None


def main():
    c_program_executable = "./critical_section_test" # C 程序可执行文件路径

    if not os.path.exists(c_program_executable):
        print(f"错误: C程序可执行文件 '{c_program_executable}' 未找到。请先编译。")
        print("编译命令: gcc -o critical_section_test critical_section_test.c -pthread")
        return

    # 定义要测试的线程数列表
    # 根据你的 CPU核心数调整，如果线程数远超核心数，主要就是等待和上下文切换
    thread_counts = [1, 2, 4, 8, 12, 16, 24, 32, 48, 64]
    # 对于非常高的线程数，C 程序中的 iterations_per_thread 可能需要调整
    # 否则总执行时间会非常长。
    # C 程序中的 iterations_per_thread = 1000000
    # 如果有64个线程，总迭代次数将是 64 * 1,000,000 = 64,000,000
    # 这可能需要一些时间。可以适当减少 iterations_per_thread 或 thread_counts 中的大数值进行快速测试

    execution_times = []
    actual_thread_counts = []

    print(f"C 程序中每个线程的迭代次数: {1000000}") # 与C代码中的值对应

    for tc in thread_counts:
        num_threads, time_ms = run_c_program(c_program_executable, tc)
        if time_ms is not None:
            actual_thread_counts.append(num_threads)
            execution_times.append(time_ms)

    if not actual_thread_counts:
        print("没有收集到有效数据，无法绘图。")
        return

    # 绘图
    plt.figure(figsize=(10, 6))
    plt.plot(actual_thread_counts, execution_times, marker='o', linestyle='-')
    plt.title('Total Execution Time vs. Number of Threads (Mutex Lock)')
    plt.xlabel('Number of Threads')
    plt.ylabel('Total Execution Time (ms)')
    plt.xticks(actual_thread_counts) # 确保x轴刻度为实际测试的线程数
    plt.grid(True)
    # plt.show()
    # 保存高清图像
    output_image_path = "execution_time_vs_threads.png"
    plt.savefig(output_image_path, dpi=300, bbox_inches='tight')
    print(f"图像已保存到: {output_image_path}")

if __name__ == "__main__":
    main()