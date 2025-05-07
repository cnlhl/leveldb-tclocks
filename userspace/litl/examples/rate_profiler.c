#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <time.h>
#include <string.h> // For strerror
#include <errno.h>  // For errno
#include <unistd.h> // For usleep (optional, for yielding)

// --- Предположим, что эти объявления находятся в komb_api.h или аналогичном файле ---
// --- Assume these are in komb_api.h or similar ---
typedef struct komb_mutex_t komb_mutex_t; 

extern komb_mutex_t* komb_api_mutex_create(const pthread_mutexattr_t *attr);
extern int komb_api_mutex_destroy(komb_mutex_t *mutex);
extern int komb_api_mutex_lock(komb_mutex_t *mutex);
extern int komb_api_mutex_trylock(komb_mutex_t *mutex); // Added trylock
extern void komb_api_mutex_unlock(komb_mutex_t *mutex);
extern void komb_api_thread_start(void); 
extern void komb_api_thread_exit(void);  
// --------------------------------------------------------------------------

// Simplified PthreadCall for this test program
static void PthreadCall(const char* label, int result) {
  if (result != 0) {
    fprintf(stderr, "pthread %s: %s\n", label, strerror(result));
    abort();
  }
}

// --- Configuration ---
const int TOTAL_TEST_DURATION_MS = 5000; // 每个线程组合运行的总时长 (ms) / Total duration for each thread combo
const int STATS_WINDOW_MS = 20;          // 统计窗口时长 (ms), e.g., kWindowNs / Stats window duration
long long OPERATIONS_PER_WINDOW_TARGET = 100000; // 每个窗口内目标操作次数 (用于控制循环次数，实际可能更少)
                                                // Target operations per window (to control loop count)

// --- Thread-local statistics --- (Using GCC specific for simplicity, or use pthread_setspecific)
typedef struct {
    long long trylock_attempts;
    long long trylock_successes;
    long long trylock_failures;
    long long lock_acquires_after_fail; // Count how many times lock was acquired after trylock failed
    int       padding[12]; // Avoid false sharing
} thread_stats_t;

// --- Global barrier for thread synchronization ---
pthread_barrier_t start_barrier;
volatile int please_stop = 0; // Signal for threads to stop

// --- Argument structure for threads ---
typedef struct {
    int thread_id;
    void* lock_ptr; 
    int use_komb;   
    thread_stats_t* stats_ptr; // Pointer to this thread's stats storage
} worker_args_t;


// --- Helper to get current time in nanoseconds ---
static inline int64_t get_time_ns() {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return (int64_t)ts.tv_sec * 1000000000LL + ts.tv_nsec;
}

// --- Worker Thread Function ---
void* worker_thread(void* arg) {
    worker_args_t* args = (worker_args_t*)arg;
    pthread_mutex_t* p_lock = NULL;
    komb_mutex_t* k_lock = NULL;
    thread_stats_t* stats = args->stats_ptr;

    stats->trylock_attempts = 0;
    stats->trylock_successes = 0;
    stats->trylock_failures = 0;
    stats->lock_acquires_after_fail = 0;

    if (args->use_komb) {
        komb_api_thread_start(); 
        k_lock = (komb_mutex_t*)args->lock_ptr;
    } else {
        p_lock = (pthread_mutex_t*)args->lock_ptr;
    }

    // Synchronize all threads before starting the main loop
    pthread_barrier_wait(&start_barrier);

    int64_t window_start_time_ns = get_time_ns();
    int64_t current_window_ops = 0;

    while (!please_stop) {
        stats->trylock_attempts++;
        int trylock_result;

        if (args->use_komb) {
            trylock_result = komb_api_mutex_trylock(k_lock);
        } else {
            trylock_result = pthread_mutex_trylock(p_lock);
        }

        if (trylock_result == 0) { // trylock succeeded
            stats->trylock_successes++;
        } else { // trylock failed (EBUSY for pthread, or non-zero for komb)
            stats->trylock_failures++;
            // Now acquire the lock forcefully
            if (args->use_komb) {
                komb_api_mutex_lock(k_lock);
            } else {
                PthreadCall("lock after trylock fail", pthread_mutex_lock(p_lock));
            }
            stats->lock_acquires_after_fail++;
        }

        // Simulate a very short critical section
        // (e.g., a few no-ops or an increment to a private variable)
        volatile int private_work = 0;
        for(int i=0; i < 5; ++i) private_work++;


        if (args->use_komb) {
            komb_api_mutex_unlock(k_lock);
        } else {
            PthreadCall("unlock", pthread_mutex_unlock(p_lock));
        }
        
        current_window_ops++;

        // Check if window duration has passed (simplified check)
        // A more robust way would be to check at the start of each iteration
        // or have a dedicated stats collection thread, but this is simpler for now.
        if (current_window_ops >= OPERATIONS_PER_WINDOW_TARGET) {
             int64_t now_ns = get_time_ns();
             if ((now_ns - window_start_time_ns) >= (int64_t)STATS_WINDOW_MS * 1000000LL) {
                // This is where you would ideally aggregate stats for *this* window
                // For simplicity in this example, we let threads run and sum up at the end.
                // A real profiler might send these window stats to a central collector.
                window_start_time_ns = now_ns;
                current_window_ops = 0; 
             }
        }
        // Yield occasionally to prevent a tight loop from starving others,
        // especially if trylock is very fast. Not strictly necessary for all lock types.
        // if (stats->trylock_attempts % 1000 == 0) sched_yield(); 
    }

    if (args->use_komb) {
        komb_api_thread_exit(); 
    }
    return NULL;
}

// --- Main Test Runner ---
void run_rate_profiler(int num_threads, int use_komb, const char* lock_name) {
    pthread_t threads[num_threads];
    worker_args_t worker_args[num_threads];
    thread_stats_t all_thread_stats[num_threads]; // Store stats for each thread

    pthread_mutex_t p_lock_instance;
    komb_mutex_t* k_lock_instance = NULL;
    void* lock_to_use = NULL;

    printf("Profiling %s with %d threads for %d ms (window: %d ms)...\n", 
           lock_name, num_threads, TOTAL_TEST_DURATION_MS, STATS_WINDOW_MS);

    if (use_komb) {
        k_lock_instance = komb_api_mutex_create(NULL);
        if (!k_lock_instance) {
            fprintf(stderr, "Failed to create komb_mutex\n");
            exit(EXIT_FAILURE);
        }
        lock_to_use = k_lock_instance;
    } else {
        PthreadCall("init lock", pthread_mutex_init(&p_lock_instance, NULL));
        lock_to_use = &p_lock_instance;
    }

    PthreadCall("barrier init", pthread_barrier_init(&start_barrier, NULL, num_threads + 1)); // +1 for main thread
    please_stop = 0;

    for (int i = 0; i < num_threads; ++i) {
        worker_args[i].thread_id = i;
        worker_args[i].lock_ptr = lock_to_use;
        worker_args[i].use_komb = use_komb;
        worker_args[i].stats_ptr = &all_thread_stats[i]; // Assign stats storage
        PthreadCall("create thread", pthread_create(&threads[i], NULL, worker_thread, &worker_args[i]));
    }

    // Wait for all threads to be ready
    pthread_barrier_wait(&start_barrier);
    int64_t test_start_time_ns = get_time_ns();

    // Let threads run for the specified duration
    usleep(TOTAL_TEST_DURATION_MS * 1000); // usleep takes microseconds

    please_stop = 1; // Signal threads to stop
    int64_t test_end_time_ns = get_time_ns();


    // Join threads and aggregate stats
    long long total_trylock_attempts = 0;
    long long total_trylock_successes = 0;
    long long total_trylock_failures = 0;
    long long total_lock_acquires_after_fail = 0;

    for (int i = 0; i < num_threads; ++i) {
        PthreadCall("join thread", pthread_join(threads[i], NULL));
        total_trylock_attempts += all_thread_stats[i].trylock_attempts;
        total_trylock_successes += all_thread_stats[i].trylock_successes;
        total_trylock_failures += all_thread_stats[i].trylock_failures;
        total_lock_acquires_after_fail += all_thread_stats[i].lock_acquires_after_fail;
    }
    
    PthreadCall("barrier destroy", pthread_barrier_destroy(&start_barrier));

    if (use_komb) {
        komb_api_mutex_destroy(k_lock_instance);
    } else {
        PthreadCall("destroy lock", pthread_mutex_destroy(&p_lock_instance));
    }

    double actual_duration_s = (test_end_time_ns - test_start_time_ns) / 1e9;
    double success_rate = 0.0;
    double failure_rate = 0.0;
    if (total_trylock_attempts > 0) {
        success_rate = (double)total_trylock_successes / total_trylock_attempts * 100.0;
        failure_rate = (double)total_trylock_failures / total_trylock_attempts * 100.0;
    }
    
    // Calculate attempts per window (approximate)
    // Number of windows = actual_duration_s * 1000 / STATS_WINDOW_MS
    double num_windows_approx = actual_duration_s * 1000.0 / STATS_WINDOW_MS;
    if (num_windows_approx < 1) num_windows_approx = 1; // Avoid division by zero if duration is too short

    long long avg_attempts_per_window = (long long)(total_trylock_attempts / num_windows_approx);
    long long avg_successes_per_window = (long long)(total_trylock_successes / num_windows_approx);
    long long avg_failures_per_window = (long long)(total_trylock_failures / num_windows_approx);


    printf("Results for %s with %d threads (%.3f s runtime):\n", lock_name, num_threads, actual_duration_s);
    printf("  Total Trylock Attempts: %lld\n", total_trylock_attempts);
    printf("  Total Trylock Successes: %lld (%.2f%%)\n", total_trylock_successes, success_rate);
    printf("  Total Trylock Failures: %lld (%.2f%%)\n", total_trylock_failures, failure_rate);
    printf("  Blocking Locks after Trylock Fail: %lld\n", total_lock_acquires_after_fail);
    printf("  Approx. Avg Attempts/Window (%dms): %lld\n", STATS_WINDOW_MS, avg_attempts_per_window);
    printf("  Approx. Avg Successes/Window (%dms): %lld\n", STATS_WINDOW_MS, avg_successes_per_window);
    printf("  Approx. Avg Failures/Window (%dms): %lld\n", STATS_WINDOW_MS, avg_failures_per_window);
    printf("--------------------------------------------------\n");
}


int main(int argc, char *argv[]) {
    // Thread counts to test. Your machine has 28 cores.
    // Consider NUMA effects if pinning, but for now let OS schedule.
    int thread_counts[] = {1, 2, 3, 4, 6, 8, 12, 16, 20, 24, 28, 32, 40, 56}; 
    int num_thread_options = sizeof(thread_counts) / sizeof(thread_counts[0]);

    // If command line arguments are provided, use them as thread counts
    if (argc > 1) {
        num_thread_options = argc - 1;
        for (int i = 0; i < num_thread_options; ++i) {
            thread_counts[i] = atoi(argv[i+1]);
            if (thread_counts[i] <= 0) {
                fprintf(stderr, "Invalid thread count: %s\n", argv[i+1]);
                return 1;
            }
        }
    }


    for (int i = 0; i < num_thread_options; ++i) {
        if (thread_counts[i] == 0) break; // Stop if we hit a zero from default or bad input
        run_rate_profiler(thread_counts[i], 0, "pthread_mutex"); // Test pthread
        run_rate_profiler(thread_counts[i], 1, "komb_mutex");    // Test komb
    }

    return 0;
}