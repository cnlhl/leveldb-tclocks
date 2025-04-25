#include <komb_api.h>
#include "kombmtx.h"
#include <pthread.h>

unsigned int last_thread_id;
__thread unsigned int cur_thread_id;

komb_mutex_t* komb_api_mutex_create(pthread_mutexattr_t *attr) {
    cur_thread_id = __sync_fetch_and_add(&last_thread_id, 1);
    return komb_mutex_create(attr);
}

int komb_api_mutex_destroy(komb_mutex_t *mutex) {
    return komb_mutex_destroy(mutex);
}

int komb_api_mutex_lock(komb_mutex_t *mutex) {
    return komb_mutex_lock(mutex, NULL);
}

int komb_api_mutex_trylock(komb_mutex_t *mutex) {
    return komb_mutex_trylock(mutex, NULL);
}

void komb_api_mutex_unlock(komb_mutex_t *mutex) {
    komb_mutex_unlock(mutex, NULL);
}

int komb_api_cond_init(komb_cond_t *cond, const pthread_condattr_t *attr) {
    return komb_cond_init(cond, attr);
}

int komb_api_cond_wait(komb_cond_t *cond, komb_mutex_t *mutex) {
    komb_node_t node;
    return komb_cond_wait(cond, mutex, &node);
}

int komb_api_cond_signal(komb_cond_t *cond) {
    return komb_cond_signal(cond);
}

int komb_api_cond_broadcast(komb_cond_t *cond) {
    return komb_cond_broadcast(cond);
}

int komb_api_cond_destroy(komb_cond_t *cond) {
    return komb_cond_destroy(cond);
}

void komb_api_thread_start(void) {
    komb_thread_start();
}

void komb_api_thread_exit(void) {
    komb_thread_exit();
} 