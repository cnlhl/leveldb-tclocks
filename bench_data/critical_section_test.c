#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h> // For clock_gettime

long long shared_counter = 0;
pthread_mutex_t lock;
int iterations_per_thread = 1000000; // 每个线程执行临界区操作的次数

// 线程工作函数
void* worker_function(void* arg) {
    for (int i = 0; i < iterations_per_thread; ++i) {
        pthread_mutex_lock(&lock);
        // --- 临界区开始 ---
        shared_counter++;
        // --- 临界区结束 ---
        pthread_mutex_unlock(&lock);
    }
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "用法: %s <线程数>\n", argv[0]);
        return 1;
    }

    int num_threads = atoi(argv[1]);
    if (num_threads <= 0) {
        fprintf(stderr, "线程数必须是正整数\n");
        return 1;
    }

    pthread_t threads[num_threads];
    struct timespec start_time, end_time;

    // 初始化互斥锁
    if (pthread_mutex_init(&lock, NULL) != 0) {
        perror("互斥锁初始化失败");
        return 1;
    }

    // 记录开始时间
    clock_gettime(CLOCK_MONOTONIC, &start_time);

    // 创建线程
    for (int i = 0; i < num_threads; ++i) {
        if (pthread_create(&threads[i], NULL, worker_function, NULL) != 0) {
            perror("线程创建失败");
            // 在实际应用中，这里需要更完善的错误处理，比如等待已创建的线程结束
            return 1;
        }
    }

    // 等待所有线程完成
    for (int i = 0; i < num_threads; ++i) {
        pthread_join(threads[i], NULL);
    }

    // 记录结束时间
    clock_gettime(CLOCK_MONOTONIC, &end_time);

    // 销毁互斥锁
    pthread_mutex_destroy(&lock);

    // 计算总耗时
    double elapsed_time_ms = (end_time.tv_sec - start_time.tv_sec) * 1000.0;
    elapsed_time_ms += (end_time.tv_nsec - start_time.tv_nsec) / 1000000.0;

    printf("线程数: %d, 总迭代次数: %lld, 总耗时: %.2f ms\n",
           num_threads, (long long)num_threads * iterations_per_thread, elapsed_time_ms);
    // 为Python绘图准备的简化输出
    fprintf(stdout, "THREADS:%d,TIME_MS:%.2f\n", num_threads, elapsed_time_ms);


    // 验证计数器结果 (可选)
    // printf("预期的共享计数器值: %lld\n", (long long)num_threads * iterations_per_thread);
    // printf("实际的共享计数器值: %lld\n", shared_counter);
    // if (shared_counter != (long long)num_threads * iterations_per_thread) {
    //     printf("错误：计数器值不匹配！锁可能未正确工作。\n");
    // }


    return 0;
}