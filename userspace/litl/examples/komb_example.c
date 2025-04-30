#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include "komb_api.h"

#define NUM_THREADS 4
#define NUM_ITERATIONS 1000000

// 共享计数器
int counter = 0;
komb_mutex_t* counter_lock;

// 线程函数
void* thread_func(void* arg) {
    int thread_id = *(int*)arg;
    
    // 初始化线程上下文
    komb_api_thread_start();
    
    // printf("Thread %d started\n", thread_id);
    
    for (int i = 0; i < NUM_ITERATIONS; i++) {
        // 使用komb锁保护临界区
        komb_api_mutex_lock(counter_lock);
        counter++;
        komb_api_mutex_unlock(counter_lock);
    }
    
    printf("Thread %d finished\n", thread_id);
    
    // 清理线程上下文
    komb_api_thread_exit();
    
    return NULL;
}

int main() {
    pthread_t threads[NUM_THREADS];
    int thread_ids[NUM_THREADS];
    
    // 初始化komb锁
    counter_lock = komb_api_mutex_create(NULL);
    
    // 创建线程
    for (int i = 0; i < NUM_THREADS; i++) {
        thread_ids[i] = i;
        if (pthread_create(&threads[i], NULL, thread_func, &thread_ids[i]) != 0) {
            perror("pthread_create");
            exit(EXIT_FAILURE);
        }
    }
    
    // 等待所有线程完成
    for (int i = 0; i < NUM_THREADS; i++) {
        pthread_join(threads[i], NULL);
    }
    
    // 销毁komb锁
    komb_api_mutex_destroy(counter_lock);
    
    // 验证结果
    printf("Final counter value: %d (expected: %d)\n", 
           counter, NUM_THREADS * NUM_ITERATIONS);
    
    return 0;
} 