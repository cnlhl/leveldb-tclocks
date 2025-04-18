#include <komb_api.h>
#include "kombmtx.h"
#include <pthread.h>

int komb_api_mutex_init(komb_mutex_t *mutex) {
    return komb_mutex_create(mutex, NULL);
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

void komb_api_thread_start(void) {
    komb_thread_start();
}

void komb_api_thread_exit(void) {
    komb_thread_exit();
} 