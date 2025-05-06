#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include <string.h> // For strerror
#include <errno.h>  // For errno

// --- Предположим, что эти объявления находятся в komb_api.h или аналогичном файле ---
// --- Assume these are in komb_api.h or similar ---
typedef struct komb_mutex_t komb_mutex_t; // Opaque struct forward declaration if not fully defined in header

extern komb_mutex_t* komb_api_mutex_create(const pthread_mutexattr_t *attr);
extern int komb_api_mutex_destroy(komb_mutex_t *mutex);
extern int komb_api_mutex_lock(komb_mutex_t *mutex);
extern void komb_api_mutex_unlock(komb_mutex_t *mutex);
extern void komb_api_thread_start(void); // Each thread using komb should call this
extern void komb_api_thread_exit(void);  // And this upon exit
// --------------------------------------------------------------------------

// Simplified PthreadCall for this test program
static void PthreadCall(const char* label, int result) {
  if (result != 0) {
    fprintf(stderr, "pthread %s: %s\n", label, strerror(result));
    abort();
  }
}

#define NUM_OPERATIONS 10000000 // 每个线程的操作次数 / Operations per thread
long long shared_counter;      // 共享计数器 / Shared counter

// 参数结构体 / Argument structure for threads
typedef struct {
    int num_threads;
    void* lock_ptr; // 指向 pthread_mutex_t 或 komb_mutex_t / Points to pthread_mutex_t or komb_mutex_t
    int use_komb;   // 0 for pthread, 1 for komb / 0 for pthread, 1 for komb
} thread_args_t;

// 线程函数 / Thread function
void* worker_thread(void* arg) {
    thread_args_t* args = (thread_args_t*)arg;
    pthread_mutex_t* p_lock = NULL;
    komb_mutex_t* k_lock = NULL;

    if (args->use_komb) {
        komb_api_thread_start(); // Important for komb initialization per thread
        k_lock = (komb_mutex_t*)args->lock_ptr;
    } else {
        p_lock = (pthread_mutex_t*)args->lock_ptr;
    }

    for (int i = 0; i < NUM_OPERATIONS; ++i) {
        if (args->use_komb) {
            komb_api_mutex_lock(k_lock);
        } else {
            PthreadCall("lock", pthread_mutex_lock(p_lock));
        }

        shared_counter++;

        if (args->use_komb) {
            komb_api_mutex_unlock(k_lock);
        } else {
            PthreadCall("unlock", pthread_mutex_unlock(p_lock));
        }
    }

    if (args->use_komb) {
        komb_api_thread_exit(); // Important for komb cleanup per thread
    }
    return NULL;
}

// 运行测试的函数 / Function to run the test
double run_test(int num_threads, int use_komb) {
    pthread_t threads[num_threads];
    thread_args_t args;
    struct timespec start_time, end_time;

    shared_counter = 0;
    args.num_threads = num_threads;
    args.use_komb = use_komb;

    pthread_mutex_t p_lock_instance;
    komb_mutex_t* k_lock_instance = NULL;

    if (use_komb) {
        k_lock_instance = komb_api_mutex_create(NULL);
        if (!k_lock_instance) {
            fprintf(stderr, "Failed to create komb_mutex\n");
            exit(EXIT_FAILURE);
        }
        args.lock_ptr = k_lock_instance;
    } else {
        PthreadCall("init", pthread_mutex_init(&p_lock_instance, NULL));
        args.lock_ptr = &p_lock_instance;
    }

    clock_gettime(CLOCK_MONOTONIC, &start_time);

    for (int i = 0; i < num_threads; ++i) {
        PthreadCall("create", pthread_create(&threads[i], NULL, worker_thread, &args));
    }

    for (int i = 0; i < num_threads; ++i) {
        PthreadCall("join", pthread_join(threads[i], NULL));
    }

    clock_gettime(CLOCK_MONOTONIC, &end_time);

    if (use_komb) {
        komb_api_mutex_destroy(k_lock_instance);
    } else {
        PthreadCall("destroy", pthread_mutex_destroy(&p_lock_instance));
    }

    // 验证计数器 / Verify counter
    long long expected_counter = (long long)num_threads * NUM_OPERATIONS;
    if (shared_counter != expected_counter) {
        fprintf(stderr, "Error: Counter mismatch! Expected: %lld, Got: %lld\n",
                expected_counter, shared_counter);
    }

    // 计算耗时（秒） / Calculate duration in seconds
    double duration = (end_time.tv_sec - start_time.tv_sec) +
                      (end_time.tv_nsec - start_time.tv_nsec) / 1e9;
    return duration;
}

int main() {
    int thread_counts[] = {2, 3, 4,5,6};
    int num_thread_options = sizeof(thread_counts) / sizeof(thread_counts[0]);

    printf("Starting benchmark with %d operations per thread.\n", NUM_OPERATIONS);
    printf("------------------------------------------------------------\n");
    printf("| Threads | Lock Type | Duration (s) | Operations/sec |\n");
    printf("|---------|-----------|--------------|----------------|\n");

    for (int i = 0; i < num_thread_options; ++i) {
        int num_threads = thread_counts[i];
        double duration_pthread, duration_komb;
        double ops_per_sec_pthread, ops_per_sec_komb;
        long long total_ops = (long long)num_threads * NUM_OPERATIONS;

        // 测试 pthread
        // Test pthread
        duration_pthread = run_test(num_threads, 0);
        ops_per_sec_pthread = total_ops / duration_pthread;
        printf("| %7d | pthread   | %12.6f | %14.2f |\n",
               num_threads, duration_pthread, ops_per_sec_pthread);

        // 测试 komb
        // Test komb
        duration_komb = run_test(num_threads, 1);
        ops_per_sec_komb = total_ops / duration_komb;
        printf("| %7d | komb      | %12.6f | %14.2f |\n",
               num_threads, duration_komb, ops_per_sec_komb);
        printf("------------------------------------------------------------\n");
    }

    return 0;
}